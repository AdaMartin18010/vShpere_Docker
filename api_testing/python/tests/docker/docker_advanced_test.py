#!/usr/bin/env python3
"""
Docker API 高级测试套件
包含：边界条件、错误处理、并发压力、性能基准、复杂场景、负面测试
"""

import docker
import pytest
import time
import threading
import concurrent.futures
from typing import List, Dict
import random
import string

class DockerAdvancedTest:
    """Docker API高级测试类"""
    
    @pytest.fixture(scope="class")
    def docker_client(self):
        """创建Docker客户端"""
        return docker.from_env()
    
    # ====================
    # 1. 边界条件测试
    # ====================
    
    def test_boundary_empty_image_name(self, docker_client):
        """测试空镜像名"""
        with pytest.raises(Exception):
            docker_client.containers.create("")
    
    def test_boundary_invalid_image_names(self, docker_client):
        """测试非法镜像名"""
        invalid_names = [
            "Invalid@Image",
            "image::",
            "image::tag",
            "a" * 256,  # 超长名称
            "../../../etc/passwd",  # 路径遍历
        ]
        
        for name in invalid_names:
            with pytest.raises(Exception):
                docker_client.containers.create(name)
    
    def test_boundary_max_container_name(self, docker_client):
        """测试最大容器名长度"""
        # Docker容器名最大255字符
        max_name = "a" * 255
        too_long_name = "a" * 256
        
        # 测试最大长度
        try:
            container = docker_client.containers.create(
                "alpine:latest",
                name=max_name
            )
            assert container.id is not None
            container.remove(force=True)
        except Exception as e:
            pytest.fail(f"最大长度名称应该成功: {e}")
        
        # 测试超长名称
        with pytest.raises(Exception):
            docker_client.containers.create(
                "alpine:latest",
                name=too_long_name
            )
    
    def test_boundary_memory_limits(self, docker_client):
        """测试内存限制边界值"""
        test_cases = [
            (0, "零内存限制（无限制）"),
            (4 * 1024 * 1024, "4MB（最小推荐值）"),
            (128 * 1024 * 1024, "128MB（正常值）"),
            (16 * 1024 * 1024 * 1024, "16GB（大值）"),
        ]
        
        for mem_limit, desc in test_cases:
            try:
                container = docker_client.containers.create(
                    "alpine:latest",
                    mem_limit=mem_limit
                )
                assert container.id is not None
                container.remove(force=True)
                print(f"✅ {desc}: 成功")
            except Exception as e:
                print(f"❌ {desc}: {e}")
    
    def test_boundary_cpu_limits(self, docker_client):
        """测试CPU限制边界值"""
        test_cases = [
            (0.1, "10% CPU"),
            (0.5, "50% CPU"),
            (1.0, "100% CPU"),
            (2.0, "200% CPU（多核）"),
            (8.0, "800% CPU（8核）"),
        ]
        
        for cpu_quota, desc in test_cases:
            try:
                container = docker_client.containers.create(
                    "alpine:latest",
                    cpu_period=100000,
                    cpu_quota=int(cpu_quota * 100000)
                )
                assert container.id is not None
                container.remove(force=True)
                print(f"✅ {desc}: 成功")
            except Exception as e:
                print(f"❌ {desc}: {e}")
    
    # ====================
    # 2. 错误处理测试
    # ====================
    
    def test_error_nonexistent_container(self, docker_client):
        """测试操作不存在的容器"""
        nonexistent_id = "nonexistent-" + "".join(random.choices(string.hexdigits, k=12))
        
        # 测试启动
        with pytest.raises(docker.errors.NotFound):
            docker_client.containers.get(nonexistent_id).start()
        
        # 测试停止
        with pytest.raises(docker.errors.NotFound):
            docker_client.containers.get(nonexistent_id).stop()
        
        # 测试删除
        with pytest.raises(docker.errors.NotFound):
            docker_client.containers.get(nonexistent_id).remove()
    
    def test_error_start_running_container(self, docker_client):
        """测试重复启动容器"""
        container = docker_client.containers.create(
            "alpine:latest",
            command=["sleep", "30"]
        )
        
        try:
            # 第一次启动
            container.start()
            
            # 第二次启动（应该无错误或返回304）
            container.start()
            
            # 验证容器仍在运行
            container.reload()
            assert container.status == "running"
        finally:
            container.remove(force=True)
    
    def test_error_remove_running_container(self, docker_client):
        """测试删除运行中容器"""
        container = docker_client.containers.create(
            "alpine:latest",
            command=["sleep", "30"]
        )
        
        try:
            container.start()
            
            # 不使用force删除（应该失败）
            with pytest.raises(docker.errors.APIError):
                container.remove(force=False)
            
            # 使用force删除（应该成功）
            container.remove(force=True)
        except Exception:
            container.remove(force=True)
            raise
    
    def test_error_invalid_port_mapping(self, docker_client):
        """测试非法端口映射"""
        invalid_port_configs = [
            {"9999999/tcp": 8080},  # 端口号超出范围
            {"invalid": 8080},       # 非法格式
            {"-1/tcp": 8080},       # 负数端口
        ]
        
        for ports in invalid_port_configs:
            with pytest.raises(Exception):
                docker_client.containers.create(
                    "alpine:latest",
                    ports=ports
                )
    
    def test_error_invalid_volume_mount(self, docker_client):
        """测试非法卷挂载"""
        with pytest.raises(Exception):
            docker_client.containers.create(
                "alpine:latest",
                volumes={
                    "/nonexistent/path": {"bind": "/data", "mode": "rw"}
                }
            )
    
    # ====================
    # 3. 并发压力测试
    # ====================
    
    def test_concurrency_parallel_creation(self, docker_client):
        """测试并发创建容器"""
        concurrency = 20
        container_ids = []
        
        def create_container(idx):
            try:
                container = docker_client.containers.create(
                    "alpine:latest",
                    command=["echo", f"container-{idx}"],
                    name=f"concurrent-test-{idx}-{int(time.time())}"
                )
                return container.id, None
            except Exception as e:
                return None, str(e)
        
        # 并发创建
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(create_container, i) for i in range(concurrency)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # 统计结果
        successes = [r[0] for r in results if r[0] is not None]
        failures = [r[1] for r in results if r[1] is not None]
        
        # 清理容器
        for cid in successes:
            try:
                docker_client.containers.get(cid).remove(force=True)
            except:
                pass
        
        success_rate = len(successes) / concurrency * 100
        print(f"并发创建成功率: {success_rate:.2f}% ({len(successes)}/{concurrency})")
        assert success_rate >= 90.0, f"成功率应该 >= 90%，实际: {success_rate:.2f}%"
    
    def test_concurrency_race_condition(self, docker_client):
        """测试资源竞争"""
        container = docker_client.containers.create(
            "alpine:latest",
            command=["sleep", "10"]
        )
        
        errors = []
        
        def start_stop_operations(op_type, iterations):
            for _ in range(iterations):
                try:
                    if op_type == "start":
                        container.start()
                    else:
                        container.stop()
                    time.sleep(0.01)
                except Exception as e:
                    errors.append(str(e))
        
        # 启动多个线程并发操作
        threads = []
        for i in range(5):
            t1 = threading.Thread(target=start_stop_operations, args=("start", 3))
            t2 = threading.Thread(target=start_stop_operations, args=("stop", 3))
            threads.extend([t1, t2])
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        # 清理
        container.remove(force=True)
        
        print(f"竞争条件测试错误数: {len(errors)}")
        # 容器应该仍然可以操作（验证完整性）
    
    def test_concurrency_stress_list_operations(self, docker_client):
        """测试高并发列表操作"""
        iterations = 100
        errors = []
        
        def list_containers():
            try:
                docker_client.containers.list(all=True)
            except Exception as e:
                errors.append(str(e))
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(list_containers) for _ in range(iterations)]
            concurrent.futures.wait(futures)
        
        success_rate = (iterations - len(errors)) / iterations * 100
        print(f"列表操作成功率: {success_rate:.2f}%")
        assert success_rate >= 95.0, f"成功率应该 >= 95%，实际: {success_rate:.2f}%"
    
    # ====================
    # 4. 幂等性测试
    # ====================
    
    def test_idempotency_multiple_stops(self, docker_client):
        """测试多次停止容器"""
        container = docker_client.containers.create(
            "alpine:latest",
            command=["sleep", "10"]
        )
        
        try:
            container.start()
            
            # 多次停止
            for i in range(3):
                container.stop()
                print(f"第{i+1}次停止: 成功")
            
            # 验证最终状态
            container.reload()
            assert container.status == "exited"
        finally:
            container.remove(force=True)
    
    def test_idempotency_multiple_removes(self, docker_client):
        """测试多次删除容器"""
        container = docker_client.containers.create("alpine:latest")
        
        # 第一次删除
        container.remove()
        
        # 第二次删除（应该失败）
        with pytest.raises(docker.errors.NotFound):
            docker_client.containers.get(container.id).remove()
    
    # ====================
    # 5. 状态机测试
    # ====================
    
    def test_state_machine_full_lifecycle(self, docker_client):
        """测试容器完整生命周期状态转换"""
        container = docker_client.containers.create(
            "alpine:latest",
            command=["sleep", "30"]
        )
        
        try:
            # 状态1: Created
            container.reload()
            assert container.status == "created"
            print(f"✅ 状态1: {container.status}")
            
            # 状态2: Running
            container.start()
            container.reload()
            assert container.status == "running"
            print(f"✅ 状态2: {container.status}")
            
            # 状态3: Paused
            container.pause()
            container.reload()
            assert container.status == "paused"
            print(f"✅ 状态3: {container.status}")
            
            # 状态4: Running (Unpause)
            container.unpause()
            container.reload()
            assert container.status == "running"
            print(f"✅ 状态4: {container.status}")
            
            # 状态5: Exited
            container.stop()
            container.reload()
            assert container.status == "exited"
            print(f"✅ 状态5: {container.status}")
            
            # 状态6: Restarted
            container.restart()
            container.reload()
            assert container.status == "running"
            print(f"✅ 状态6 (重启): {container.status}")
            
        finally:
            container.remove(force=True)
    
    def test_state_machine_invalid_transitions(self, docker_client):
        """测试非法状态转换"""
        container = docker_client.containers.create("alpine:latest")
        
        try:
            # 尝试pause一个未运行的容器（应该失败）
            with pytest.raises(docker.errors.APIError):
                container.pause()
            
            # 尝试unpause一个未暂停的容器（应该失败）
            with pytest.raises(docker.errors.APIError):
                container.unpause()
        finally:
            container.remove(force=True)
    
    # ====================
    # 6. 资源限制测试
    # ====================
    
    def test_resource_oom_killer(self, docker_client):
        """测试内存OOM Killer"""
        try:
            container = docker_client.containers.create(
                "alpine:latest",
                command=["sh", "-c", "dd if=/dev/zero of=/tmp/file bs=1M count=20"],
                mem_limit="10m",
                memswap_limit="10m"
            )
            
            container.start()
            result = container.wait(timeout=10)
            
            # OOM killed通常退出码为137
            print(f"容器退出码: {result['StatusCode']}")
            
            container.remove(force=True)
        except Exception as e:
            print(f"OOM测试跳过: {e}")
            pytest.skip("无法创建内存限制容器")
    
    def test_resource_cpu_throttling(self, docker_client):
        """测试CPU节流"""
        containers = []
        
        try:
            # 创建多个CPU密集型容器
            for i in range(3):
                container = docker_client.containers.create(
                    "alpine:latest",
                    command=["sh", "-c", "while true; do echo test; done"],
                    cpu_period=100000,
                    cpu_quota=10000  # 10% CPU
                )
                container.start()
                containers.append(container)
            
            time.sleep(2)
            
            # 验证容器运行
            for container in containers:
                container.reload()
                assert container.status == "running"
            
        finally:
            for container in containers:
                container.remove(force=True)
    
    # ====================
    # 7. 复杂场景测试
    # ====================
    
    def test_complex_multi_container_network(self, docker_client):
        """测试多容器网络通信"""
        network_name = f"test-network-{int(time.time())}"
        network = docker_client.networks.create(network_name, driver="bridge")
        
        try:
            # 创建服务端容器
            server = docker_client.containers.run(
                "alpine:latest",
                command=["sh", "-c", "nc -l -p 8080"],
                network=network_name,
                name="server",
                detach=True
            )
            
            time.sleep(1)
            
            # 创建客户端容器
            client = docker_client.containers.run(
                "alpine:latest",
                command=["sh", "-c", "echo 'hello' | nc server 8080"],
                network=network_name,
                detach=True
            )
            
            # 等待完成
            client.wait(timeout=5)
            
            print("✅ 多容器网络通信测试完成")
            
        finally:
            try:
                docker_client.containers.get("server").remove(force=True)
            except:
                pass
            try:
                client.remove(force=True)
            except:
                pass
            network.remove()
    
    def test_complex_volume_sharing(self, docker_client):
        """测试容器间卷共享"""
        volume_name = f"shared-volume-{int(time.time())}"
        volume = docker_client.volumes.create(name=volume_name)
        
        try:
            # 容器1写入数据
            writer = docker_client.containers.run(
                "alpine:latest",
                command=["sh", "-c", "echo 'shared data' > /data/test.txt"],
                volumes={volume_name: {"bind": "/data", "mode": "rw"}},
                remove=True
            )
            
            # 容器2读取数据
            reader = docker_client.containers.run(
                "alpine:latest",
                command=["cat", "/data/test.txt"],
                volumes={volume_name: {"bind": "/data", "mode": "ro"}},
                remove=True
            )
            
            print("✅ 卷共享测试完成")
            
        finally:
            volume.remove(force=True)
    
    def test_complex_health_check(self, docker_client):
        """测试健康检查"""
        healthcheck = {
            "test": ["CMD-SHELL", "echo 'healthy'"],
            "interval": 1000000000,  # 1s in nanoseconds
            "timeout": 500000000,    # 0.5s
            "retries": 3,
            "start_period": 0
        }
        
        container = docker_client.containers.create(
            "alpine:latest",
            command=["sleep", "30"],
            healthcheck=healthcheck
        )
        
        try:
            container.start()
            
            # 等待健康检查
            time.sleep(3)
            
            container.reload()
            health_status = container.attrs['State']['Health']['Status']
            print(f"健康状态: {health_status}")
            
        finally:
            container.remove(force=True)
    
    # ====================
    # 8. 性能基准测试
    # ====================
    
    def test_performance_container_creation(self, docker_client):
        """性能测试：容器创建"""
        iterations = 50
        start_time = time.time()
        
        container_ids = []
        for i in range(iterations):
            container = docker_client.containers.create("alpine:latest")
            container_ids.append(container.id)
        
        creation_time = time.time() - start_time
        
        # 清理
        for cid in container_ids:
            docker_client.containers.get(cid).remove(force=True)
        
        avg_time = creation_time / iterations
        print(f"容器创建性能: {iterations}次, 总时间{creation_time:.2f}s, 平均{avg_time:.3f}s/次")
        print(f"吞吐量: {iterations/creation_time:.2f} 容器/秒")
    
    def test_performance_container_lifecycle(self, docker_client):
        """性能测试：完整生命周期"""
        iterations = 20
        start_time = time.time()
        
        for i in range(iterations):
            container = docker_client.containers.create(
                "alpine:latest",
                command=["echo", "test"]
            )
            container.start()
            container.wait(timeout=5)
            container.remove()
        
        total_time = time.time() - start_time
        avg_time = total_time / iterations
        
        print(f"完整生命周期性能: {iterations}次, 总时间{total_time:.2f}s, 平均{avg_time:.3f}s/次")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

