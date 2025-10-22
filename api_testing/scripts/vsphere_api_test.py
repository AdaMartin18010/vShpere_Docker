#!/usr/bin/env python3
"""
VMware vSphere API 完整测试套件
基于vSphere REST API和PowerCLI
"""

import requests
import json
import urllib3
import sys
import os
from typing import Optional, Dict, List
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import setup_colored_logger
from utils.auth import get_vsphere_session

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class vSphereAPITest:
    """vSphere API测试类"""
    
    def __init__(self, vcenter_host: str, username: str, password: str, verify_ssl: bool = False):
        """
        初始化vSphere API测试
        
        Args:
            vcenter_host: vCenter服务器地址
            username: 用户名
            password: 密码
            verify_ssl: 是否验证SSL证书
        """
        self.vcenter_host = vcenter_host
        self.username = username
        self.password = password
        self.base_url = f"https://{vcenter_host}/api"
        self.rest_url = f"https://{vcenter_host}/rest"
        self.verify_ssl = verify_ssl
        self.session_id: Optional[str] = None
        self.logger = setup_colored_logger('vsphere_api_test', level='INFO')
    
    def test_create_session(self) -> bool:
        """测试1: 创建vSphere会话"""
        self.logger.info("测试1: 创建vSphere会话")
        
        try:
            url = f"{self.base_url}/session"
            response = requests.post(
                url,
                auth=(self.username, self.password),
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 201:
                self.session_id = response.json().get('value')
                self.logger.info(f"✅ 会话创建成功: {self.session_id[:20]}...")
                return True
            else:
                self.logger.error(f"❌ 会话创建失败: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"❌ 会话创建异常: {e}")
            return False
    
    def test_get_session_info(self) -> Optional[Dict]:
        """测试2: 获取会话信息"""
        self.logger.info("\n测试2: 获取会话信息")
        
        try:
            url = f"{self.base_url}/session"
            headers = {"vmware-api-session-id": self.session_id}
            
            response = requests.get(
                url,
                headers=headers,
                verify=self.verify_ssl,
                timeout=10
            )
            
            if response.status_code == 200:
                session_info = response.json().get('value')
                self.logger.info("✅ 会话信息获取成功:")
                self.logger.info(f"  - 用户: {session_info.get('user')}")
                self.logger.info(f"  - 创建时间: {session_info.get('created_time')}")
                return session_info
            else:
                self.logger.error(f"❌ 会话信息获取失败: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"❌ 获取失败: {e}")
            return None
    
    def test_list_vms(self) -> List[Dict]:
        """测试3: 列出所有虚拟机"""
        self.logger.info("\n测试3: 列出所有虚拟机")
        
        try:
            url = f"{self.rest_url}/vcenter/vm"
            headers = {"vmware-api-session-id": self.session_id}
            
            response = requests.get(
                url,
                headers=headers,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                vms = response.json().get('value', [])
                self.logger.info(f"✅ 虚拟机列表获取成功: 共 {len(vms)} 台虚拟机")
                
                # 显示前5台虚拟机
                for vm in vms[:5]:
                    self.logger.info(f"  - {vm.get('name')} (ID: {vm.get('vm')}, 状态: {vm.get('power_state')})")
                
                if len(vms) > 5:
                    self.logger.info(f"  ... 还有 {len(vms) - 5} 台虚拟机")
                
                return vms
            else:
                self.logger.error(f"❌ 虚拟机列表获取失败: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"❌ 获取失败: {e}")
            return []
    
    def test_get_vm_details(self, vm_id: str) -> Optional[Dict]:
        """测试4: 获取虚拟机详细信息"""
        self.logger.info(f"\n测试4: 获取虚拟机详情 (ID: {vm_id})")
        
        try:
            url = f"{self.rest_url}/vcenter/vm/{vm_id}"
            headers = {"vmware-api-session-id": self.session_id}
            
            response = requests.get(
                url,
                headers=headers,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                vm_details = response.json().get('value', {})
                self.logger.info("✅ 虚拟机详情获取成功:")
                self.logger.info(f"  - 名称: {vm_details.get('name')}")
                
                cpu = vm_details.get('cpu', {})
                self.logger.info(f"  - CPU: {cpu.get('count')} 核")
                
                memory = vm_details.get('memory', {})
                self.logger.info(f"  - 内存: {memory.get('size_MiB')} MiB")
                
                self.logger.info(f"  - 电源状态: {vm_details.get('power_state')}")
                
                return vm_details
            else:
                self.logger.error(f"❌ 虚拟机详情获取失败: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"❌ 获取失败: {e}")
            return None
    
    def test_list_hosts(self) -> List[Dict]:
        """测试5: 列出所有主机"""
        self.logger.info("\n测试5: 列出所有ESXi主机")
        
        try:
            url = f"{self.rest_url}/vcenter/host"
            headers = {"vmware-api-session-id": self.session_id}
            
            response = requests.get(
                url,
                headers=headers,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                hosts = response.json().get('value', [])
                self.logger.info(f"✅ 主机列表获取成功: 共 {len(hosts)} 台主机")
                
                for host in hosts:
                    self.logger.info(f"  - {host.get('name')} (状态: {host.get('connection_state')})")
                
                return hosts
            else:
                self.logger.error(f"❌ 主机列表获取失败: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"❌ 获取失败: {e}")
            return []
    
    def test_list_datastores(self) -> List[Dict]:
        """测试6: 列出所有数据存储"""
        self.logger.info("\n测试6: 列出所有数据存储")
        
        try:
            url = f"{self.rest_url}/vcenter/datastore"
            headers = {"vmware-api-session-id": self.session_id}
            
            response = requests.get(
                url,
                headers=headers,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                datastores = response.json().get('value', [])
                self.logger.info(f"✅ 数据存储列表获取成功: 共 {len(datastores)} 个数据存储")
                
                for ds in datastores:
                    self.logger.info(f"  - {ds.get('name')} (类型: {ds.get('type')})")
                
                return datastores
            else:
                self.logger.error(f"❌ 数据存储列表获取失败: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"❌ 获取失败: {e}")
            return []
    
    def test_list_networks(self) -> List[Dict]:
        """测试7: 列出所有网络"""
        self.logger.info("\n测试7: 列出所有网络")
        
        try:
            url = f"{self.rest_url}/vcenter/network"
            headers = {"vmware-api-session-id": self.session_id}
            
            response = requests.get(
                url,
                headers=headers,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                networks = response.json().get('value', [])
                self.logger.info(f"✅ 网络列表获取成功: 共 {len(networks)} 个网络")
                
                for net in networks[:10]:
                    self.logger.info(f"  - {net.get('name')} (类型: {net.get('type')})")
                
                if len(networks) > 10:
                    self.logger.info(f"  ... 还有 {len(networks) - 10} 个网络")
                
                return networks
            else:
                self.logger.error(f"❌ 网络列表获取失败: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"❌ 获取失败: {e}")
            return []
    
    def test_list_clusters(self) -> List[Dict]:
        """测试8: 列出所有集群"""
        self.logger.info("\n测试8: 列出所有集群")
        
        try:
            url = f"{self.rest_url}/vcenter/cluster"
            headers = {"vmware-api-session-id": self.session_id}
            
            response = requests.get(
                url,
                headers=headers,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                clusters = response.json().get('value', [])
                self.logger.info(f"✅ 集群列表获取成功: 共 {len(clusters)} 个集群")
                
                for cluster in clusters:
                    self.logger.info(f"  - {cluster.get('name')}")
                
                return clusters
            else:
                self.logger.error(f"❌ 集群列表获取失败: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"❌ 获取失败: {e}")
            return []
    
    def test_list_resource_pools(self) -> List[Dict]:
        """测试9: 列出所有资源池"""
        self.logger.info("\n测试9: 列出所有资源池")
        
        try:
            url = f"{self.rest_url}/vcenter/resource-pool"
            headers = {"vmware-api-session-id": self.session_id}
            
            response = requests.get(
                url,
                headers=headers,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                pools = response.json().get('value', [])
                self.logger.info(f"✅ 资源池列表获取成功: 共 {len(pools)} 个资源池")
                
                for pool in pools[:5]:
                    self.logger.info(f"  - {pool.get('name')}")
                
                return pools
            else:
                self.logger.error(f"❌ 资源池列表获取失败: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"❌ 获取失败: {e}")
            return []
    
    def test_vm_power_operations(self, vm_id: str, dry_run: bool = True) -> bool:
        """测试10: 虚拟机电源操作 (可选, dry_run模式只显示信息)"""
        self.logger.info(f"\n测试10: 虚拟机电源操作 (Dry Run: {dry_run})")
        
        if dry_run:
            self.logger.warning("  ⚠️  Dry Run模式: 不会执行实际的电源操作")
            self.logger.info("  - 支持的操作: start, stop, reset, suspend")
            return True
        
        # 实际的电源操作 (需要谨慎使用)
        self.logger.warning("  ⚠️  电源操作已禁用以保护生产环境")
        return False
    
    def test_delete_session(self) -> bool:
        """测试11: 删除vSphere会话"""
        self.logger.info("\n测试11: 删除vSphere会话")
        
        try:
            url = f"{self.base_url}/session"
            headers = {"vmware-api-session-id": self.session_id}
            
            response = requests.delete(
                url,
                headers=headers,
                verify=self.verify_ssl,
                timeout=10
            )
            
            if response.status_code == 204:
                self.logger.info("✅ 会话删除成功")
                self.session_id = None
                return True
            else:
                self.logger.error(f"❌ 会话删除失败: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"❌ 删除失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        self.logger.info("=" * 70)
        self.logger.info("vSphere API 完整测试套件")
        self.logger.info("=" * 70)
        self.logger.info(f"vCenter服务器: {self.vcenter_host}")
        self.logger.info(f"用户: {self.username}")
        self.logger.info(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 70)
        
        # 测试1: 创建会话
        if not self.test_create_session():
            self.logger.error("\n❌ 无法创建会话,测试终止")
            return
        
        # 测试2: 获取会话信息
        self.test_get_session_info()
        
        # 测试3-9: 列出各种资源
        vms = self.test_list_vms()
        
        # 如果有虚拟机,获取第一台的详情
        if vms:
            vm_id = vms[0].get('vm')
            self.test_get_vm_details(vm_id)
            self.test_vm_power_operations(vm_id, dry_run=True)
        
        self.test_list_hosts()
        self.test_list_datastores()
        self.test_list_networks()
        self.test_list_clusters()
        self.test_list_resource_pools()
        
        # 测试11: 删除会话
        self.test_delete_session()
        
        self.logger.info("\n" + "=" * 70)
        self.logger.info("所有测试完成")
        self.logger.info(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 70)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='vSphere API测试套件')
    parser.add_argument('--server', required=True, help='vCenter服务器地址')
    parser.add_argument('--username', required=True, help='用户名')
    parser.add_argument('--password', required=True, help='密码')
    parser.add_argument('--no-verify-ssl', action='store_true', help='不验证SSL证书')
    
    args = parser.parse_args()
    
    # 创建测试实例
    tester = vSphereAPITest(
        vcenter_host=args.server,
        username=args.username,
        password=args.password,
        verify_ssl=not args.no_verify_ssl
    )
    
    # 运行所有测试
    tester.run_all_tests()


if __name__ == "__main__":
    # 使用示例
    # python vsphere_api_test.py --server vcenter.example.com --username administrator@vsphere.local --password your_password --no-verify-ssl
    
    # 或者直接运行 (用于开发测试)
    if len(sys.argv) == 1:
        print("使用示例:")
        print("python vsphere_api_test.py --server vcenter.example.com --username admin@vsphere.local --password password --no-verify-ssl")
        print("\n提示: 请提供必需的参数")
    else:
        main()

