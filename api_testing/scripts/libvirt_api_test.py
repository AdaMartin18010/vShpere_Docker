#!/usr/bin/env python3
"""
libvirt API 完整测试套件
支持QEMU/KVM, Xen, VMware ESXi等多种Hypervisor
"""

import sys
import os
from typing import Optional, List, Dict
from xml.dom import minidom
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import setup_colored_logger

try:
    import libvirt
except ImportError:
    print("❌ libvirt-python未安装")
    print("安装方法:")
    print("  Ubuntu/Debian: sudo apt-get install python3-libvirt")
    print("  CentOS/RHEL: sudo yum install python3-libvirt")
    print("  pip: pip install libvirt-python")
    sys.exit(1)


class LibvirtAPITest:
    """libvirt API测试类"""
    
    def __init__(self, uri: str = 'qemu:///system'):
        """
        初始化libvirt API测试
        
        Args:
            uri: libvirt连接URI
                 - qemu:///system - 本地QEMU系统
                 - qemu+ssh://user@host/system - 远程SSH
                 - qemu+tcp://host:16509/system - 远程TCP
                 - qemu+tls://host:16514/system - 远程TLS
        """
        self.uri = uri
        self.conn: Optional[libvirt.virConnect] = None
        self.logger = setup_colored_logger('libvirt_api_test', level='INFO')
    
    def test_connect(self) -> bool:
        """测试1: 连接到libvirt"""
        self.logger.info(f"测试1: 连接到libvirt (URI: {self.uri})")
        
        try:
            self.conn = libvirt.open(self.uri)
            
            if self.conn is None:
                self.logger.error("❌ libvirt连接失败: 连接为None")
                return False
            
            self.logger.info("✅ libvirt连接成功")
            self.logger.info(f"  - Hypervisor: {self.conn.getType()}")
            self.logger.info(f"  - 版本: {self.conn.getVersion()}")
            self.logger.info(f"  - 库版本: {self.conn.getLibVersion()}")
            self.logger.info(f"  - 主机名: {self.conn.getHostname()}")
            
            return True
        except libvirt.libvirtError as e:
            self.logger.error(f"❌ libvirt连接失败: {e}")
            return False
    
    def test_get_node_info(self) -> Optional[tuple]:
        """测试2: 获取节点信息"""
        self.logger.info("\n测试2: 获取节点信息")
        
        try:
            node_info = self.conn.getInfo()
            
            self.logger.info("✅ 节点信息获取成功:")
            self.logger.info(f"  - 架构: {node_info[0]}")
            self.logger.info(f"  - 内存: {node_info[1]} MB")
            self.logger.info(f"  - CPU数: {node_info[2]}")
            self.logger.info(f"  - CPU频率: {node_info[3]} MHz")
            self.logger.info(f"  - NUMA节点: {node_info[4]}")
            self.logger.info(f"  - CPU Socket数: {node_info[5]}")
            self.logger.info(f"  - 每Socket核心数: {node_info[6]}")
            self.logger.info(f"  - 每核心线程数: {node_info[7]}")
            
            return node_info
        except libvirt.libvirtError as e:
            self.logger.error(f"❌ 节点信息获取失败: {e}")
            return None
    
    def test_list_domains(self) -> tuple:
        """测试3: 列出所有虚拟机"""
        self.logger.info("\n测试3: 列出所有虚拟机(域)")
        
        try:
            # 列出所有虚拟机 (运行中和关闭的)
            domain_ids = self.conn.listDomainsID()
            inactive_names = self.conn.listDefinedDomains()
            
            self.logger.info("✅ 虚拟机列表获取成功")
            self.logger.info(f"  - 运行中: {len(domain_ids)} 台")
            self.logger.info(f"  - 已关闭: {len(inactive_names)} 台")
            self.logger.info(f"  - 总计: {len(domain_ids) + len(inactive_names)} 台")
            
            # 显示运行中的虚拟机
            if domain_ids:
                self.logger.info("\n运行中的虚拟机:")
                for domain_id in domain_ids:
                    domain = self.conn.lookupByID(domain_id)
                    state, max_mem, mem, num_cpu, cpu_time = domain.info()
                    
                    self.logger.info(f"  - {domain.name()}")
                    self.logger.info(f"    ID: {domain_id}, 状态: {self._get_state_name(state)}")
                    self.logger.info(f"    CPU: {num_cpu} 核, 内存: {mem // 1024} MB")
            
            # 显示已关闭的虚拟机
            if inactive_names:
                self.logger.info("\n已关闭的虚拟机:")
                for name in inactive_names[:5]:  # 显示前5台
                    self.logger.info(f"  - {name}")
                
                if len(inactive_names) > 5:
                    self.logger.info(f"  ... 还有 {len(inactive_names) - 5} 台")
            
            return domain_ids, inactive_names
        except libvirt.libvirtError as e:
            self.logger.error(f"❌ 虚拟机列表获取失败: {e}")
            return [], []
    
    def test_get_domain_info(self, domain_name: str) -> Optional[libvirt.virDomain]:
        """测试4: 获取虚拟机详细信息"""
        self.logger.info(f"\n测试4: 获取虚拟机详情 (名称: {domain_name})")
        
        try:
            domain = self.conn.lookupByName(domain_name)
            state, max_mem, mem, num_cpu, cpu_time = domain.info()
            
            self.logger.info("✅ 虚拟机详情获取成功:")
            self.logger.info(f"  - 名称: {domain.name()}")
            self.logger.info(f"  - UUID: {domain.UUIDString()}")
            self.logger.info(f"  - 状态: {self._get_state_name(state)}")
            self.logger.info(f"  - 最大内存: {max_mem // 1024} MB")
            self.logger.info(f"  - 当前内存: {mem // 1024} MB")
            self.logger.info(f"  - vCPU数: {num_cpu}")
            self.logger.info(f"  - CPU时间: {cpu_time / 1000000000:.2f} 秒")
            
            # 获取自动启动状态
            autostart = domain.autostart()
            self.logger.info(f"  - 自动启动: {'是' if autostart else '否'}")
            
            # XML配置大小
            xml_desc = domain.XMLDesc(0)
            self.logger.info(f"  - XML配置: {len(xml_desc)} 字节")
            
            return domain
        except libvirt.libvirtError as e:
            self.logger.error(f"❌ 虚拟机详情获取失败: {e}")
            return None
    
    def test_get_domain_xml(self, domain_name: str) -> Optional[str]:
        """测试5: 获取虚拟机XML配置"""
        self.logger.info(f"\n测试5: 获取虚拟机XML配置 (名称: {domain_name})")
        
        try:
            domain = self.conn.lookupByName(domain_name)
            xml_desc = domain.XMLDesc(0)
            
            # 格式化XML
            dom = minidom.parseString(xml_desc)
            pretty_xml = dom.toprettyxml(indent="  ")
            
            self.logger.info("✅ XML配置获取成功:")
            self.logger.info(f"  - 总行数: {len(pretty_xml.split('\\n'))}")
            
            # 只显示前15行
            lines = pretty_xml.split('\n')
            self.logger.info("  - 配置预览 (前15行):")
            for line in lines[:15]:
                if line.strip():
                    self.logger.info(f"    {line}")
            self.logger.info("    ...")
            
            return xml_desc
        except libvirt.libvirtError as e:
            self.logger.error(f"❌ XML配置获取失败: {e}")
            return None
    
    def test_list_networks(self) -> tuple:
        """测试6: 列出所有网络"""
        self.logger.info("\n测试6: 列出所有网络")
        
        try:
            active_nets = self.conn.listNetworks()
            inactive_nets = self.conn.listDefinedNetworks()
            
            self.logger.info("✅ 网络列表获取成功")
            self.logger.info(f"  - 活动网络: {len(active_nets)} 个")
            self.logger.info(f"  - 非活动网络: {len(inactive_nets)} 个")
            
            if active_nets:
                self.logger.info("\n活动网络:")
                for net_name in active_nets:
                    net = self.conn.networkLookupByName(net_name)
                    self.logger.info(f"  - {net_name}")
                    self.logger.info(f"    UUID: {net.UUIDString()}")
                    self.logger.info(f"    自动启动: {'是' if net.autostart() else '否'}")
            
            return active_nets, inactive_nets
        except libvirt.libvirtError as e:
            self.logger.error(f"❌ 网络列表获取失败: {e}")
            return [], []
    
    def test_list_storage_pools(self) -> tuple:
        """测试7: 列出所有存储池"""
        self.logger.info("\n测试7: 列出所有存储池")
        
        try:
            active_pools = self.conn.listStoragePools()
            inactive_pools = self.conn.listDefinedStoragePools()
            
            self.logger.info("✅ 存储池列表获取成功")
            self.logger.info(f"  - 活动存储池: {len(active_pools)} 个")
            self.logger.info(f"  - 非活动存储池: {len(inactive_pools)} 个")
            
            if active_pools:
                self.logger.info("\n活动存储池:")
                for pool_name in active_pools:
                    pool = self.conn.storagePoolLookupByName(pool_name)
                    info = pool.info()
                    
                    self.logger.info(f"  - {pool_name}")
                    self.logger.info(f"    状态: {self._get_pool_state_name(info[0])}")
                    self.logger.info(f"    容量: {info[1] // (1024**3)} GB")
                    self.logger.info(f"    已用: {info[2] // (1024**3)} GB")
                    self.logger.info(f"    可用: {info[3] // (1024**3)} GB")
            
            return active_pools, inactive_pools
        except libvirt.libvirtError as e:
            self.logger.error(f"❌ 存储池列表获取失败: {e}")
            return [], []
    
    def test_get_capabilities(self) -> Optional[str]:
        """测试8: 获取Hypervisor能力"""
        self.logger.info("\n测试8: 获取Hypervisor能力")
        
        try:
            caps = self.conn.getCapabilities()
            
            # 解析XML
            dom = minidom.parseString(caps)
            
            self.logger.info("✅ Hypervisor能力获取成功:")
            
            # 提取主机信息
            host = dom.getElementsByTagName('host')[0]
            uuid = host.getElementsByTagName('uuid')[0].firstChild.data
            cpu = host.getElementsByTagName('cpu')[0]
            arch = cpu.getElementsByTagName('arch')[0].firstChild.data
            
            self.logger.info(f"  - 主机UUID: {uuid}")
            self.logger.info(f"  - CPU架构: {arch}")
            
            # 提取客户机支持
            guests = dom.getElementsByTagName('guest')
            self.logger.info(f"  - 支持的客户机类型: {len(guests)} 种")
            
            for guest in guests[:5]:  # 显示前5种
                os_type = guest.getElementsByTagName('os_type')[0].firstChild.data
                arch_elem = guest.getElementsByTagName('arch')[0]
                guest_arch = arch_elem.getAttribute('name')
                self.logger.info(f"    - {os_type} ({guest_arch})")
            
            if len(guests) > 5:
                self.logger.info(f"    ... 还有 {len(guests) - 5} 种")
            
            return caps
        except libvirt.libvirtError as e:
            self.logger.error(f"❌ Hypervisor能力获取失败: {e}")
            return None
    
    def test_get_sysinfo(self) -> Optional[str]:
        """测试9: 获取系统信息"""
        self.logger.info("\n测试9: 获取系统信息")
        
        try:
            sysinfo = self.conn.getSysinfo()
            
            self.logger.info("✅ 系统信息获取成功")
            self.logger.info(f"  - 信息长度: {len(sysinfo)} 字节")
            
            # 解析部分系统信息
            if '<smbios' in sysinfo:
                self.logger.info("  - SMBIOS信息: 包含")
            
            return sysinfo
        except libvirt.libvirtError as e:
            self.logger.warning(f"⚠️  系统信息获取失败: {e}")
            self.logger.info("  - 提示: 某些Hypervisor可能不支持此功能")
            return None
    
    def test_list_interfaces(self) -> List[str]:
        """测试10: 列出所有网络接口"""
        self.logger.info("\n测试10: 列出所有网络接口")
        
        try:
            interfaces = self.conn.listInterfaces()
            
            self.logger.info(f"✅ 网络接口列表获取成功: 共 {len(interfaces)} 个接口")
            
            for iface in interfaces:
                self.logger.info(f"  - {iface}")
            
            return interfaces
        except libvirt.libvirtError as e:
            self.logger.error(f"❌ 网络接口列表获取失败: {e}")
            return []
    
    def test_disconnect(self) -> bool:
        """测试11: 断开libvirt连接"""
        self.logger.info("\n测试11: 断开libvirt连接")
        
        if self.conn:
            try:
                result = self.conn.close()
                self.conn = None
                
                if result == 0:
                    self.logger.info("✅ libvirt连接已断开")
                    return True
                else:
                    self.logger.warning(f"⚠️  断开连接返回: {result}")
                    return True
            except libvirt.libvirtError as e:
                self.logger.error(f"❌ 断开连接失败: {e}")
                return False
        else:
            self.logger.warning("⚠️  连接未建立,无需断开")
            return True
    
    def _get_state_name(self, state: int) -> str:
        """将状态码转换为名称"""
        states = {
            libvirt.VIR_DOMAIN_NOSTATE: 'No State',
            libvirt.VIR_DOMAIN_RUNNING: 'Running',
            libvirt.VIR_DOMAIN_BLOCKED: 'Blocked',
            libvirt.VIR_DOMAIN_PAUSED: 'Paused',
            libvirt.VIR_DOMAIN_SHUTDOWN: 'Shutdown',
            libvirt.VIR_DOMAIN_SHUTOFF: 'Shut Off',
            libvirt.VIR_DOMAIN_CRASHED: 'Crashed',
            libvirt.VIR_DOMAIN_PMSUSPENDED: 'PM Suspended'
        }
        return states.get(state, f'Unknown ({state})')
    
    def _get_pool_state_name(self, state: int) -> str:
        """将存储池状态码转换为名称"""
        states = {
            libvirt.VIR_STORAGE_POOL_INACTIVE: 'Inactive',
            libvirt.VIR_STORAGE_POOL_BUILDING: 'Building',
            libvirt.VIR_STORAGE_POOL_RUNNING: 'Running',
            libvirt.VIR_STORAGE_POOL_DEGRADED: 'Degraded',
            libvirt.VIR_STORAGE_POOL_INACCESSIBLE: 'Inaccessible'
        }
        return states.get(state, f'Unknown ({state})')
    
    def run_all_tests(self):
        """运行所有测试"""
        self.logger.info("=" * 70)
        self.logger.info("libvirt API 完整测试套件")
        self.logger.info("=" * 70)
        self.logger.info(f"连接URI: {self.uri}")
        self.logger.info(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 70)
        
        # 测试1: 连接
        if not self.test_connect():
            self.logger.error("\n❌ 无法连接到libvirt,测试终止")
            return
        
        # 测试2-10: 各种查询操作
        self.test_get_node_info()
        domain_ids, inactive_names = self.test_list_domains()
        
        # 如果有虚拟机,获取详细信息
        if domain_ids:
            domain = self.conn.lookupByID(domain_ids[0])
            self.test_get_domain_info(domain.name())
            self.test_get_domain_xml(domain.name())
        elif inactive_names:
            self.test_get_domain_info(inactive_names[0])
            self.test_get_domain_xml(inactive_names[0])
        
        self.test_list_networks()
        self.test_list_storage_pools()
        self.test_get_capabilities()
        self.test_get_sysinfo()
        self.test_list_interfaces()
        
        # 测试11: 断开连接
        self.test_disconnect()
        
        self.logger.info("\n" + "=" * 70)
        self.logger.info("所有测试完成")
        self.logger.info(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 70)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='libvirt API测试套件')
    parser.add_argument(
        '--uri',
        default='qemu:///system',
        help='libvirt连接URI (默认: qemu:///system)'
    )
    parser.add_argument(
        '--examples',
        action='store_true',
        help='显示URI示例'
    )
    
    args = parser.parse_args()
    
    if args.examples:
        print("libvirt连接URI示例:")
        print("  qemu:///system           - 本地QEMU系统连接")
        print("  qemu:///session          - 本地QEMU用户会话")
        print("  qemu+ssh://user@host/system - 远程SSH连接")
        print("  qemu+tcp://host:16509/system - 远程TCP连接")
        print("  qemu+tls://host:16514/system - 远程TLS连接")
        print("  xen:///                  - 本地Xen")
        print("  esx://host/?no_verify=1  - VMware ESXi")
        return
    
    # 创建测试实例
    tester = LibvirtAPITest(uri=args.uri)
    
    # 运行所有测试
    tester.run_all_tests()


if __name__ == "__main__":
    # 使用示例
    # python libvirt_api_test.py
    # python libvirt_api_test.py --uri qemu+ssh://user@remotehost/system
    # python libvirt_api_test.py --examples
    
    main()

