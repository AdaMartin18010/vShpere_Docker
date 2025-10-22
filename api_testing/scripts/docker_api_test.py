#!/usr/bin/env python3
"""
Docker Engine API 完整测试套件
测试Docker Engine REST API的各种功能
"""

import requests
import json
import sys
from typing import Dict, List, Optional

class DockerAPITest:
    """Docker Engine API测试类"""
    
    def __init__(self, base_url: str = 'http://localhost:2375'):
        """
        初始化Docker API测试
        
        Args:
            base_url: Docker API基础URL
                     - Unix Socket: unix:///var/run/docker.sock
                     - TCP: http://localhost:2375
                     - TLS: https://localhost:2376
        """
        if base_url.startswith('unix://'):
            import requests_unixsocket
            requests_unixsocket.monkeypatch()
            self.base_url = base_url
        else:
            self.base_url = base_url
        
        self.api_version = 'v1.43'  # Docker API版本
    
    def test_ping(self) -> bool:
        """测试1: Docker守护进程连通性"""
        print("测试1: Docker守护进程连通性")
        
        try:
            url = f"{self.base_url}/_ping"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200 and response.text == "OK":
                print(f"✅ Docker守护进程连接成功")
                print(f"  - API状态: {response.text}")
                return True
            else:
                print(f"❌ Docker守护进程连接失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def test_version(self) -> Optional[Dict]:
        """测试2: 获取Docker版本信息"""
        print("\n测试2: 获取Docker版本信息")
        
        try:
            url = f"{self.base_url}/version"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                version_info = response.json()
                print("✅ 版本信息获取成功:")
                print(f"  - Docker版本: {version_info.get('Version')}")
                print(f"  - API版本: {version_info.get('ApiVersion')}")
                print(f"  - Go版本: {version_info.get('GoVersion')}")
                print(f"  - Git Commit: {version_info.get('GitCommit')}")
                print(f"  - 构建时间: {version_info.get('BuildTime')}")
                print(f"  - 操作系统: {version_info.get('Os')}")
                print(f"  - 架构: {version_info.get('Arch')}")
                return version_info
            else:
                print(f"❌ 版本信息获取失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 获取失败: {e}")
            return None
    
    def test_info(self) -> Optional[Dict]:
        """测试3: 获取Docker系统信息"""
        print("\n测试3: 获取Docker系统信息")
        
        try:
            url = f"{self.base_url}/info"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                info = response.json()
                print("✅ 系统信息获取成功:")
                print(f"  - 容器数: {info.get('Containers')}")
                print(f"    - 运行中: {info.get('ContainersRunning')}")
                print(f"    - 已暂停: {info.get('ContainersPaused')}")
                print(f"    - 已停止: {info.get('ContainersStopped')}")
                print(f"  - 镜像数: {info.get('Images')}")
                print(f"  - 存储驱动: {info.get('Driver')}")
                print(f"  - 日志驱动: {info.get('LoggingDriver')}")
                print(f"  - Cgroup驱动: {info.get('CgroupDriver')}")
                print(f"  - 内核版本: {info.get('KernelVersion')}")
                print(f"  - 操作系统: {info.get('OperatingSystem')}")
                print(f"  - CPU数: {info.get('NCPU')}")
                print(f"  - 总内存: {info.get('MemTotal') // (1024**3)} GB")
                return info
            else:
                print(f"❌ 系统信息获取失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 获取失败: {e}")
            return None
    
    def test_list_containers(self, all_containers: bool = True) -> List[Dict]:
        """测试4: 列出容器"""
        print(f"\n测试4: 列出容器 (all={all_containers})")
        
        try:
            url = f"{self.base_url}/{self.api_version}/containers/json"
            params = {'all': str(all_containers).lower()}
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                containers = response.json()
                print(f"✅ 容器列表获取成功: 共 {len(containers)} 个容器")
                
                for container in containers[:5]:  # 显示前5个
                    print(f"\n  容器ID: {container['Id'][:12]}")
                    print(f"  - 名称: {', '.join(container['Names'])}")
                    print(f"  - 镜像: {container['Image']}")
                    print(f"  - 状态: {container['State']}")
                    print(f"  - 状态描述: {container['Status']}")
                    print(f"  - 端口: {container.get('Ports', [])}")
                
                return containers
            else:
                print(f"❌ 容器列表获取失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ 获取失败: {e}")
            return []
    
    def test_inspect_container(self, container_id: str) -> Optional[Dict]:
        """测试5: 检查容器详情"""
        print(f"\n测试5: 检查容器详情 (ID: {container_id[:12]})")
        
        try:
            url = f"{self.base_url}/{self.api_version}/containers/{container_id}/json"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                container = response.json()
                print("✅ 容器详情获取成功:")
                print(f"  - ID: {container['Id'][:12]}")
                print(f"  - 名称: {container['Name']}")
                print(f"  - 状态: {container['State']['Status']}")
                print(f"  - 运行中: {container['State']['Running']}")
                print(f"  - 镜像: {container['Config']['Image']}")
                print(f"  - 主机名: {container['Config']['Hostname']}")
                print(f"  - 创建时间: {container['Created']}")
                
                # 网络信息
                networks = container['NetworkSettings']['Networks']
                print(f"  - 网络:")
                for net_name, net_info in networks.items():
                    print(f"    - {net_name}: {net_info.get('IPAddress')}")
                
                return container
            else:
                print(f"❌ 容器详情获取失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 获取失败: {e}")
            return None
    
    def test_container_stats(self, container_id: str) -> Optional[Dict]:
        """测试6: 获取容器统计信息"""
        print(f"\n测试6: 获取容器统计信息 (ID: {container_id[:12]})")
        
        try:
            url = f"{self.base_url}/{self.api_version}/containers/{container_id}/stats"
            params = {'stream': 'false'}  # 只获取一次,不流式传输
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                stats = response.json()
                print("✅ 容器统计信息获取成功:")
                
                # CPU统计
                cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                           stats['precpu_stats']['cpu_usage']['total_usage']
                system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                              stats['precpu_stats']['system_cpu_usage']
                cpu_percent = (cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100.0 if system_delta > 0 else 0.0
                
                print(f"  - CPU使用率: {cpu_percent:.2f}%")
                
                # 内存统计
                mem_usage = stats['memory_stats']['usage']
                mem_limit = stats['memory_stats']['limit']
                mem_percent = (mem_usage / mem_limit) * 100.0
                
                print(f"  - 内存使用: {mem_usage / (1024**2):.2f} MB / {mem_limit / (1024**2):.2f} MB ({mem_percent:.2f}%)")
                
                # 网络统计
                networks = stats.get('networks', {})
                for net_name, net_stats in networks.items():
                    print(f"  - 网络 ({net_name}):")
                    print(f"    - 接收: {net_stats['rx_bytes'] / (1024**2):.2f} MB")
                    print(f"    - 发送: {net_stats['tx_bytes'] / (1024**2):.2f} MB")
                
                return stats
            else:
                print(f"❌ 容器统计信息获取失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 获取失败: {e}")
            return None
    
    def test_list_images(self) -> List[Dict]:
        """测试7: 列出镜像"""
        print("\n测试7: 列出镜像")
        
        try:
            url = f"{self.base_url}/{self.api_version}/images/json"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                images = response.json()
                print(f"✅ 镜像列表获取成功: 共 {len(images)} 个镜像")
                
                for image in images[:5]:  # 显示前5个
                    print(f"\n  镜像ID: {image['Id'][:19]}")
                    print(f"  - 仓库标签: {image.get('RepoTags', ['<none>'])}")
                    print(f"  - 大小: {image['Size'] / (1024**2):.2f} MB")
                    print(f"  - 创建时间: {image['Created']}")
                
                return images
            else:
                print(f"❌ 镜像列表获取失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ 获取失败: {e}")
            return []
    
    def test_inspect_image(self, image_id: str) -> Optional[Dict]:
        """测试8: 检查镜像详情"""
        print(f"\n测试8: 检查镜像详情 (ID: {image_id[:19]})")
        
        try:
            url = f"{self.base_url}/{self.api_version}/images/{image_id}/json"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                image = response.json()
                print("✅ 镜像详情获取成功:")
                print(f"  - ID: {image['Id'][:19]}")
                print(f"  - 仓库标签: {image.get('RepoTags', ['<none>'])}")
                print(f"  - 大小: {image['Size'] / (1024**2):.2f} MB")
                print(f"  - 虚拟大小: {image['VirtualSize'] / (1024**2):.2f} MB")
                print(f"  - 架构: {image['Architecture']}")
                print(f"  - 操作系统: {image['Os']}")
                print(f"  - 层数: {len(image['RootFS']['Layers'])}")
                
                return image
            else:
                print(f"❌ 镜像详情获取失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 获取失败: {e}")
            return None
    
    def test_list_volumes(self) -> List[Dict]:
        """测试9: 列出卷"""
        print("\n测试9: 列出卷")
        
        try:
            url = f"{self.base_url}/{self.api_version}/volumes"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                volumes = data.get('Volumes', [])
                print(f"✅ 卷列表获取成功: 共 {len(volumes)} 个卷")
                
                for volume in volumes[:5]:  # 显示前5个
                    print(f"\n  卷名: {volume['Name']}")
                    print(f"  - 驱动: {volume['Driver']}")
                    print(f"  - 挂载点: {volume['Mountpoint']}")
                    print(f"  - 作用域: {volume['Scope']}")
                
                return volumes
            else:
                print(f"❌ 卷列表获取失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ 获取失败: {e}")
            return []
    
    def test_list_networks(self) -> List[Dict]:
        """测试10: 列出网络"""
        print("\n测试10: 列出网络")
        
        try:
            url = f"{self.base_url}/{self.api_version}/networks"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                networks = response.json()
                print(f"✅ 网络列表获取成功: 共 {len(networks)} 个网络")
                
                for network in networks:
                    print(f"\n  网络ID: {network['Id'][:12]}")
                    print(f"  - 名称: {network['Name']}")
                    print(f"  - 驱动: {network['Driver']}")
                    print(f"  - 作用域: {network['Scope']}")
                    print(f"  - 子网: {network['IPAM']['Config']}")
                
                return networks
            else:
                print(f"❌ 网络列表获取失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ 获取失败: {e}")
            return []
    
    def test_create_container(self, image: str = 'alpine:latest', name: str = 'test-container') -> Optional[str]:
        """测试11: 创建容器 (可选)"""
        print(f"\n测试11: 创建容器 (镜像: {image}, 名称: {name})")
        
        try:
            url = f"{self.base_url}/{self.api_version}/containers/create"
            params = {'name': name}
            body = {
                'Image': image,
                'Cmd': ['echo', 'Hello Docker API'],
                'HostConfig': {
                    'AutoRemove': True  # 容器停止后自动删除
                }
            }
            
            response = requests.post(url, params=params, json=body, timeout=10)
            
            if response.status_code == 201:
                data = response.json()
                container_id = data['Id']
                print(f"✅ 容器创建成功:")
                print(f"  - 容器ID: {container_id[:12]}")
                print(f"  - 警告: {data.get('Warnings', '无')}")
                return container_id
            else:
                error_data = response.json()
                print(f"❌ 容器创建失败: {response.status_code}")
                print(f"  - 错误: {error_data.get('message')}")
                return None
        except Exception as e:
            print(f"❌ 创建失败: {e}")
            return None
    
    def test_start_container(self, container_id: str) -> bool:
        """测试12: 启动容器 (可选)"""
        print(f"\n测试12: 启动容器 (ID: {container_id[:12]})")
        
        try:
            url = f"{self.base_url}/{self.api_version}/containers/{container_id}/start"
            response = requests.post(url, timeout=10)
            
            if response.status_code == 204:
                print(f"✅ 容器启动成功")
                return True
            else:
                print(f"❌ 容器启动失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            return False
    
    def test_stop_container(self, container_id: str) -> bool:
        """测试13: 停止容器 (可选)"""
        print(f"\n测试13: 停止容器 (ID: {container_id[:12]})")
        
        try:
            url = f"{self.base_url}/{self.api_version}/containers/{container_id}/stop"
            response = requests.post(url, timeout=15)
            
            if response.status_code == 204:
                print(f"✅ 容器停止成功")
                return True
            else:
                print(f"❌ 容器停止失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 停止失败: {e}")
            return False
    
    def test_remove_container(self, container_id: str, force: bool = False) -> bool:
        """测试14: 删除容器 (可选)"""
        print(f"\n测试14: 删除容器 (ID: {container_id[:12]}, force={force})")
        
        try:
            url = f"{self.base_url}/{self.api_version}/containers/{container_id}"
            params = {'force': str(force).lower()}
            response = requests.delete(url, params=params, timeout=10)
            
            if response.status_code == 204:
                print(f"✅ 容器删除成功")
                return True
            else:
                print(f"❌ 容器删除失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 删除失败: {e}")
            return False
    
    def run_all_tests(self, create_test_container: bool = False):
        """运行所有测试"""
        print("=" * 70)
        print("Docker Engine API 完整测试套件")
        print("=" * 70)
        
        # 基础测试
        if not self.test_ping():
            print("\n⚠️  无法连接到Docker守护进程,请检查Docker是否运行")
            return
        
        self.test_version()
        self.test_info()
        
        # 容器测试
        containers = self.test_list_containers(all_containers=True)
        if containers:
            self.test_inspect_container(containers[0]['Id'])
            # 只对运行中的容器获取统计信息
            if containers[0]['State'] == 'running':
                self.test_container_stats(containers[0]['Id'])
        
        # 镜像测试
        images = self.test_list_images()
        if images:
            self.test_inspect_image(images[0]['Id'])
        
        # 卷和网络测试
        self.test_list_volumes()
        self.test_list_networks()
        
        # 容器生命周期测试 (可选)
        if create_test_container:
            print("\n" + "=" * 70)
            print("容器生命周期测试 (创建/启动/停止/删除)")
            print("=" * 70)
            
            container_id = self.test_create_container()
            if container_id:
                if self.test_start_container(container_id):
                    import time
                    time.sleep(2)  # 等待容器完成
                    self.test_stop_container(container_id)
                    self.test_remove_container(container_id)
        
        print("\n" + "=" * 70)
        print("所有测试完成")
        print("=" * 70)


if __name__ == "__main__":
    # 配置参数
    # 方式1: Unix Socket (推荐,本地使用)
    docker_url = "unix:///var/run/docker.sock"
    
    # 方式2: TCP (需要配置Docker守护进程)
    # docker_url = "http://localhost:2375"
    
    # 方式3: TLS (安全连接)
    # docker_url = "https://localhost:2376"
    
    # 创建测试实例
    tester = DockerAPITest(docker_url)
    
    # 运行所有测试
    # 参数: create_test_container=True 会创建测试容器(需要有alpine:latest镜像)
    tester.run_all_tests(create_test_container=False)

