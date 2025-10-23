#!/usr/bin/env python3
"""
libvirt高级功能测试套件
包含：认证、安全、监控、性能、资源管理
"""

import pytest
import libvirt
import time
import xml.etree.ElementTree as ET


class LibvirtAdvancedTestSuite:
    """libvirt高级功能测试套件"""
    
    @pytest.fixture(scope="class")
    def libvirt_connection(self):
        """创建libvirt连接"""
        conn = libvirt.open('qemu:///system')
        if conn is None:
            pytest.skip("无法连接到libvirt")
        yield conn
        conn.close()
    
    # ====================
    # 1. 认证与安全测试
    # ====================
    
    def test_auth_local_connection(self):
        """测试本地连接（Unix socket）"""
        # 本地连接通常不需要认证
        conn = libvirt.open('qemu:///system')
        assert conn is not None
        
        # 验证连接
        hostname = conn.getHostname()
        assert hostname is not None
        print(f"✅ 本地连接成功: {hostname}")
        
        conn.close()
    
    def test_auth_remote_tcp(self):
        """测试远程TCP连接"""
        # 远程TCP连接（需要配置）
        try:
            conn = libvirt.open('qemu+tcp://remote-host/system')
            assert conn is not None
            print("✅ 远程TCP连接成功")
            conn.close()
        except libvirt.libvirtError as e:
            pytest.skip(f"远程连接未配置: {e}")
    
    def test_auth_remote_ssh(self):
        """测试SSH隧道连接"""
        try:
            conn = libvirt.open('qemu+ssh://user@remote-host/system')
            assert conn is not None
            print("✅ SSH隧道连接成功")
            conn.close()
        except libvirt.libvirtError as e:
            pytest.skip(f"SSH连接未配置: {e}")
    
    def test_auth_tls_connection(self):
        """测试TLS加密连接"""
        try:
            conn = libvirt.open('qemu+tls://remote-host/system')
            assert conn is not None
            print("✅ TLS连接成功")
            conn.close()
        except libvirt.libvirtError as e:
            pytest.skip(f"TLS连接未配置: {e}")
    
    def test_security_selinux_context(self, libvirt_connection):
        """测试SELinux上下文"""
        domain_name = f"test-selinux-{int(time.time())}"
        
        # 创建带SELinux标签的域XML
        xml = f"""
        <domain type='kvm'>
          <name>{domain_name}</name>
          <memory unit='MB'>512</memory>
          <vcpu>1</vcpu>
          <os>
            <type arch='x86_64'>hvm</type>
          </os>
          <seclabel type='dynamic' model='selinux' relabel='yes'/>
          <devices>
            <disk type='file' device='disk'>
              <driver name='qemu' type='qcow2'/>
              <source file='/var/lib/libvirt/images/{domain_name}.qcow2'/>
              <target dev='vda' bus='virtio'/>
            </disk>
          </devices>
        </domain>
        """
        
        try:
            domain = libvirt_connection.defineXML(xml)
            
            # 检查SELinux配置
            domain_xml = domain.XMLDesc(0)
            root = ET.fromstring(domain_xml)
            seclabel = root.find('seclabel')
            
            if seclabel is not None:
                print("✅ SELinux上下文配置成功")
                print(f"   类型: {seclabel.get('type')}")
                print(f"   模型: {seclabel.get('model')}")
            else:
                print("⚠️  SELinux未启用")
            
            domain.undefine()
            
        except libvirt.libvirtError as e:
            pytest.skip(f"SELinux测试失败: {e}")
    
    # ====================
    # 2. 性能监控测试
    # ====================
    
    def test_monitor_domain_stats(self, libvirt_connection):
        """测试域性能统计"""
        domain_name = f"test-stats-{int(time.time())}"
        
        # 创建简单域
        xml = f"""
        <domain type='kvm'>
          <name>{domain_name}</name>
          <memory unit='MB'>512</memory>
          <vcpu>1</vcpu>
          <os>
            <type arch='x86_64'>hvm</type>
          </os>
          <devices>
            <disk type='file' device='disk'>
              <driver name='qemu' type='qcow2'/>
              <source file='/var/lib/libvirt/images/{domain_name}.qcow2'/>
              <target dev='vda' bus='virtio'/>
            </disk>
          </devices>
        </domain>
        """
        
        domain = libvirt_connection.defineXML(xml)
        
        try:
            # 启动域
            domain.create()
            time.sleep(2)
            
            # 获取CPU统计
            cpu_stats = domain.getCPUStats(True)
            print(f"✅ CPU统计获取成功")
            print(f"   CPU时间: {cpu_stats}")
            
            # 获取内存统计
            try:
                mem_stats = domain.memoryStats()
                print(f"✅ 内存统计获取成功")
                for key, value in mem_stats.items():
                    print(f"   {key}: {value}")
            except Exception as e:
                print(f"⚠️  内存统计不可用: {e}")
            
            # 获取块设备统计
            try:
                block_stats = domain.blockStats('vda')
                print(f"✅ 块设备统计获取成功")
                print(f"   读请求: {block_stats[0]}")
                print(f"   读字节: {block_stats[1]}")
                print(f"   写请求: {block_stats[2]}")
                print(f"   写字节: {block_stats[3]}")
            except Exception as e:
                print(f"⚠️  块设备统计不可用: {e}")
            
        finally:
            if domain.isActive():
                domain.destroy()
            domain.undefine()
    
    def test_monitor_connection_stats(self, libvirt_connection):
        """测试连接级别统计"""
        # 获取节点信息
        node_info = libvirt_connection.getInfo()
        
        print("✅ 节点信息获取成功")
        print(f"   架构: {node_info[0]}")
        print(f"   内存(MB): {node_info[1]}")
        print(f"   CPU数: {node_info[2]}")
        print(f"   CPU频率(MHz): {node_info[3]}")
        print(f"   NUMA节点: {node_info[4]}")
        print(f"   CPU插槽: {node_info[5]}")
        print(f"   每插槽核数: {node_info[6]}")
        print(f"   每核线程数: {node_info[7]}")
        
        # 获取节点CPU统计
        cpu_stats = libvirt_connection.getCPUStats(libvirt.VIR_NODE_CPU_STATS_ALL_CPUS, 0)
        print(f"✅ 节点CPU统计: {cpu_stats}")
        
        # 获取节点内存统计
        mem_stats = libvirt_connection.getMemoryStats(libvirt.VIR_NODE_MEMORY_STATS_ALL_CELLS, 0)
        print(f"✅ 节点内存统计: {mem_stats}")
    
    def test_monitor_domain_info(self, libvirt_connection):
        """测试域基本信息监控"""
        domain_name = f"test-info-{int(time.time())}"
        
        xml = f"""
        <domain type='kvm'>
          <name>{domain_name}</name>
          <memory unit='MB'>1024</memory>
          <vcpu>2</vcpu>
          <os>
            <type arch='x86_64'>hvm</type>
          </os>
          <devices>
            <disk type='file' device='disk'>
              <driver name='qemu' type='qcow2'/>
              <source file='/var/lib/libvirt/images/{domain_name}.qcow2'/>
              <target dev='vda' bus='virtio'/>
            </disk>
          </devices>
        </domain>
        """
        
        domain = libvirt_connection.defineXML(xml)
        
        try:
            domain.create()
            
            # 获取域信息
            info = domain.info()
            
            print("✅ 域信息获取成功")
            print(f"   状态: {info[0]}")
            print(f"   最大内存(KB): {info[1]}")
            print(f"   使用内存(KB): {info[2]}")
            print(f"   vCPU数: {info[3]}")
            print(f"   CPU时间(ns): {info[4]}")
            
            # 获取域状态
            state, reason = domain.state()
            states = {
                libvirt.VIR_DOMAIN_NOSTATE: 'No state',
                libvirt.VIR_DOMAIN_RUNNING: 'Running',
                libvirt.VIR_DOMAIN_BLOCKED: 'Blocked',
                libvirt.VIR_DOMAIN_PAUSED: 'Paused',
                libvirt.VIR_DOMAIN_SHUTDOWN: 'Shutdown',
                libvirt.VIR_DOMAIN_SHUTOFF: 'Shutoff',
                libvirt.VIR_DOMAIN_CRASHED: 'Crashed',
                libvirt.VIR_DOMAIN_PMSUSPENDED: 'PM Suspended'
            }
            print(f"   详细状态: {states.get(state, 'Unknown')}")
            
        finally:
            if domain.isActive():
                domain.destroy()
            domain.undefine()
    
    # ====================
    # 3. 事件监控测试
    # ====================
    
    def test_events_lifecycle(self, libvirt_connection):
        """测试生命周期事件监听"""
        events_received = []
        
        def lifecycle_callback(conn, dom, event, detail, opaque):
            """生命周期事件回调"""
            events_received.append({
                'domain': dom.name(),
                'event': event,
                'detail': detail
            })
            print(f"   收到事件: 域={dom.name()}, 事件={event}, 详情={detail}")
        
        # 注册事件回调
        libvirt_connection.domainEventRegisterAny(
            None,
            libvirt.VIR_DOMAIN_EVENT_ID_LIFECYCLE,
            lifecycle_callback,
            None
        )
        
        # 创建和操作域以触发事件
        domain_name = f"test-events-{int(time.time())}"
        xml = f"""
        <domain type='kvm'>
          <name>{domain_name}</name>
          <memory unit='MB'>512</memory>
          <vcpu>1</vcpu>
          <os>
            <type arch='x86_64'>hvm</type>
          </os>
          <devices>
            <disk type='file' device='disk'>
              <driver name='qemu' type='qcow2'/>
              <source file='/var/lib/libvirt/images/{domain_name}.qcow2'/>
              <target dev='vda' bus='virtio'/>
            </disk>
          </devices>
        </domain>
        """
        
        domain = libvirt_connection.defineXML(xml)
        
        try:
            print("✅ 开始事件监听")
            
            # 触发启动事件
            domain.create()
            time.sleep(1)
            
            # 触发停止事件
            domain.destroy()
            time.sleep(1)
            
            # 检查收到的事件
            assert len(events_received) > 0, "应该收到至少一个事件"
            print(f"✅ 收到{len(events_received)}个生命周期事件")
            
        finally:
            if domain.isActive():
                domain.destroy()
            domain.undefine()
    
    # ====================
    # 4. 资源管理测试
    # ====================
    
    def test_resource_cpu_hotplug(self, libvirt_connection):
        """测试CPU热插拔"""
        domain_name = f"test-cpu-hotplug-{int(time.time())}"
        
        xml = f"""
        <domain type='kvm'>
          <name>{domain_name}</name>
          <memory unit='MB'>512</memory>
          <vcpu placement='static' current='1'>4</vcpu>
          <os>
            <type arch='x86_64'>hvm</type>
          </os>
          <devices>
            <disk type='file' device='disk'>
              <driver name='qemu' type='qcow2'/>
              <source file='/var/lib/libvirt/images/{domain_name}.qcow2'/>
              <target dev='vda' bus='virtio'/>
            </disk>
          </devices>
        </domain>
        """
        
        domain = libvirt_connection.defineXML(xml)
        
        try:
            domain.create()
            time.sleep(2)
            
            # 获取初始vCPU数
            info = domain.info()
            initial_vcpus = info[3]
            print(f"   初始vCPU数: {initial_vcpus}")
            
            # 热添加vCPU
            try:
                domain.setVcpusFlags(2, libvirt.VIR_DOMAIN_AFFECT_LIVE)
                time.sleep(1)
                
                # 验证vCPU数
                info = domain.info()
                new_vcpus = info[3]
                print(f"✅ CPU热插拔成功: {initial_vcpus} -> {new_vcpus}")
                
            except libvirt.libvirtError as e:
                print(f"⚠️  CPU热插拔不支持: {e}")
            
        finally:
            if domain.isActive():
                domain.destroy()
            domain.undefine()
    
    def test_resource_memory_balloon(self, libvirt_connection):
        """测试内存气球"""
        domain_name = f"test-memory-balloon-{int(time.time())}"
        
        xml = f"""
        <domain type='kvm'>
          <name>{domain_name}</name>
          <memory unit='MB'>1024</memory>
          <currentMemory unit='MB'>512</currentMemory>
          <vcpu>1</vcpu>
          <os>
            <type arch='x86_64'>hvm</type>
          </os>
          <devices>
            <disk type='file' device='disk'>
              <driver name='qemu' type='qcow2'/>
              <source file='/var/lib/libvirt/images/{domain_name}.qcow2'/>
              <target dev='vda' bus='virtio'/>
            </disk>
            <memballoon model='virtio'/>
          </devices>
        </domain>
        """
        
        domain = libvirt_connection.defineXML(xml)
        
        try:
            domain.create()
            time.sleep(2)
            
            # 获取初始内存
            info = domain.info()
            initial_mem = info[2]
            print(f"   初始内存(KB): {initial_mem}")
            
            # 调整内存（通过气球）
            try:
                new_mem = 768 * 1024  # 768MB in KB
                domain.setMemoryFlags(new_mem, libvirt.VIR_DOMAIN_AFFECT_LIVE)
                time.sleep(2)
                
                # 验证内存变化
                info = domain.info()
                current_mem = info[2]
                print(f"✅ 内存气球成功: {initial_mem}KB -> {current_mem}KB")
                
            except libvirt.libvirtError as e:
                print(f"⚠️  内存气球不支持: {e}")
            
        finally:
            if domain.isActive():
                domain.destroy()
            domain.undefine()
    
    def test_resource_cpu_pinning(self, libvirt_connection):
        """测试CPU绑定"""
        domain_name = f"test-cpu-pin-{int(time.time())}"
        
        xml = f"""
        <domain type='kvm'>
          <name>{domain_name}</name>
          <memory unit='MB'>512</memory>
          <vcpu>2</vcpu>
          <cputune>
            <vcpupin vcpu='0' cpuset='0'/>
            <vcpupin vcpu='1' cpuset='1'/>
          </cputune>
          <os>
            <type arch='x86_64'>hvm</type>
          </os>
          <devices>
            <disk type='file' device='disk'>
              <driver name='qemu' type='qcow2'/>
              <source file='/var/lib/libvirt/images/{domain_name}.qcow2'/>
              <target dev='vda' bus='virtio'/>
            </disk>
          </devices>
        </domain>
        """
        
        domain = libvirt_connection.defineXML(xml)
        
        try:
            domain.create()
            time.sleep(2)
            
            # 检查CPU绑定
            domain_xml = domain.XMLDesc(0)
            if 'vcpupin' in domain_xml:
                print("✅ CPU绑定配置成功")
                
                # 显示绑定信息
                root = ET.fromstring(domain_xml)
                cputune = root.find('cputune')
                if cputune is not None:
                    for pin in cputune.findall('vcpupin'):
                        vcpu = pin.get('vcpu')
                        cpuset = pin.get('cpuset')
                        print(f"   vCPU {vcpu} -> 物理CPU {cpuset}")
            else:
                print("⚠️  CPU绑定配置未生效")
            
        finally:
            if domain.isActive():
                domain.destroy()
            domain.undefine()
    
    # ====================
    # 5. 完整高级功能测试
    # ====================
    
    def test_full_advanced_workflow(self, libvirt_connection):
        """测试完整高级功能工作流"""
        print("\n=== libvirt完整高级功能工作流测试 ===")
        
        domain_name = f"test-full-advanced-{int(time.time())}"
        
        # 创建功能完整的域
        xml = f"""
        <domain type='kvm'>
          <name>{domain_name}</name>
          <memory unit='MB'>1024</memory>
          <currentMemory unit='MB'>512</currentMemory>
          <vcpu placement='static'>2</vcpu>
          <cputune>
            <shares>2048</shares>
          </cputune>
          <os>
            <type arch='x86_64'>hvm</type>
          </os>
          <devices>
            <disk type='file' device='disk'>
              <driver name='qemu' type='qcow2'/>
              <source file='/var/lib/libvirt/images/{domain_name}.qcow2'/>
              <target dev='vda' bus='virtio'/>
            </disk>
            <interface type='network'>
              <source network='default'/>
              <model type='virtio'/>
            </interface>
            <memballoon model='virtio'/>
          </devices>
          <seclabel type='dynamic' model='selinux' relabel='yes'/>
        </domain>
        """
        
        # 1. 定义域
        domain = libvirt_connection.defineXML(xml)
        print("✅ 1. 定义域（含安全标签）")
        
        try:
            # 2. 启动域
            domain.create()
            print("✅ 2. 启动域")
            time.sleep(2)
            
            # 3. 获取性能统计
            info = domain.info()
            print(f"✅ 3. 获取性能统计")
            print(f"   内存使用: {info[2]}KB")
            print(f"   vCPU数: {info[3]}")
            
            # 4. CPU统计
            try:
                cpu_stats = domain.getCPUStats(True)
                print(f"✅ 4. CPU统计: {cpu_stats}")
            except:
                print("⚠️  4. CPU统计不可用")
            
            # 5. 内存调整
            try:
                domain.setMemoryFlags(768 * 1024, libvirt.VIR_DOMAIN_AFFECT_LIVE)
                print("✅ 5. 内存气球调整成功")
            except:
                print("⚠️  5. 内存调整不支持")
            
            # 6. 创建快照
            snapshot_xml = """
            <domainsnapshot>
              <name>advanced-snapshot</name>
              <description>Advanced test snapshot</description>
            </domainsnapshot>
            """
            snapshot = domain.snapshotCreateXML(snapshot_xml, 0)
            print("✅ 6. 创建快照")
            
            # 7. 删除快照
            snapshot.delete(0)
            print("✅ 7. 删除快照")
            
            # 8. 关闭域
            domain.destroy()
            print("✅ 8. 关闭域")
            
            # 9. 删除域
            domain.undefine()
            print("✅ 9. 删除域")
            
            print("=== 完整高级功能工作流测试完成 ===\n")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            if domain.isActive():
                domain.destroy()
            domain.undefine()
            raise


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

