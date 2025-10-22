#!/usr/bin/env python3
"""
Kubernetes API 完整测试套件
测试Kubernetes REST API的各种功能
"""

import requests
import json
import urllib3
from typing import Dict, List, Optional
import os

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class KubernetesAPITest:
    """Kubernetes API测试类"""
    
    def __init__(self, api_server: str, token: Optional[str] = None, kubeconfig_path: Optional[str] = None):
        """
        初始化Kubernetes API测试
        
        Args:
            api_server: K8s API Server地址 (例如: https://kubernetes.default.svc)
            token: ServiceAccount Token (可选)
            kubeconfig_path: kubeconfig文件路径 (可选)
        """
        self.api_server = api_server.rstrip('/')
        self.token = token
        self.kubeconfig_path = kubeconfig_path or os.path.expanduser('~/.kube/config')
        
        # 设置认证头
        self.headers = {}
        if self.token:
            self.headers['Authorization'] = f'Bearer {self.token}'
        
        self.verify_ssl = False  # 开发环境可设置为False
    
    def _request(self, method: str, path: str, **kwargs) -> Optional[requests.Response]:
        """通用请求方法"""
        url = f"{self.api_server}{path}"
        kwargs.setdefault('headers', self.headers)
        kwargs.setdefault('verify', self.verify_ssl)
        kwargs.setdefault('timeout', 10)
        
        try:
            response = requests.request(method, url, **kwargs)
            return response
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return None
    
    def test_api_versions(self) -> Optional[Dict]:
        """测试1: 获取API版本"""
        print("测试1: 获取API版本")
        
        response = self._request('GET', '/api')
        
        if response and response.status_code == 200:
            data = response.json()
            print("✅ API版本获取成功:")
            print(f"  - Core API组:")
            for version in data.get('versions', []):
                print(f"    - {version}")
            return data
        else:
            print(f"❌ API版本获取失败: {response.status_code if response else 'N/A'}")
            return None
    
    def test_api_groups(self) -> Optional[Dict]:
        """测试2: 获取API组"""
        print("\n测试2: 获取API组")
        
        response = self._request('GET', '/apis')
        
        if response and response.status_code == 200:
            data = response.json()
            groups = data.get('groups', [])
            print(f"✅ API组获取成功: 共 {len(groups)} 个组")
            
            for group in groups[:10]:  # 显示前10个
                print(f"\n  - {group['name']}")
                print(f"    首选版本: {group['preferredVersion']['version']}")
                versions = [v['version'] for v in group.get('versions', [])]
                print(f"    所有版本: {', '.join(versions)}")
            
            return data
        else:
            print(f"❌ API组获取失败: {response.status_code if response else 'N/A'}")
            return None
    
    def test_list_nodes(self) -> Optional[List[Dict]]:
        """测试3: 列出节点"""
        print("\n测试3: 列出集群节点")
        
        response = self._request('GET', '/api/v1/nodes')
        
        if response and response.status_code == 200:
            data = response.json()
            nodes = data.get('items', [])
            print(f"✅ 节点列表获取成功: 共 {len(nodes)} 个节点")
            
            for node in nodes:
                metadata = node['metadata']
                status = node['status']
                
                print(f"\n  节点: {metadata['name']}")
                print(f"  - UID: {metadata['uid']}")
                
                # 节点状态
                conditions = status.get('conditions', [])
                ready_condition = next((c for c in conditions if c['type'] == 'Ready'), None)
                if ready_condition:
                    print(f"  - 状态: {'Ready' if ready_condition['status'] == 'True' else 'NotReady'}")
                
                # 节点信息
                node_info = status.get('nodeInfo', {})
                print(f"  - 操作系统: {node_info.get('osImage')}")
                print(f"  - 内核版本: {node_info.get('kernelVersion')}")
                print(f"  - 容器运行时: {node_info.get('containerRuntimeVersion')}")
                print(f"  - Kubelet版本: {node_info.get('kubeletVersion')}")
                
                # 资源容量
                capacity = status.get('capacity', {})
                print(f"  - CPU: {capacity.get('cpu')}")
                print(f"  - 内存: {capacity.get('memory')}")
                print(f"  - Pod容量: {capacity.get('pods')}")
            
            return nodes
        else:
            print(f"❌ 节点列表获取失败: {response.status_code if response else 'N/A'}")
            return None
    
    def test_list_namespaces(self) -> Optional[List[Dict]]:
        """测试4: 列出命名空间"""
        print("\n测试4: 列出命名空间")
        
        response = self._request('GET', '/api/v1/namespaces')
        
        if response and response.status_code == 200:
            data = response.json()
            namespaces = data.get('items', [])
            print(f"✅ 命名空间列表获取成功: 共 {len(namespaces)} 个命名空间")
            
            for ns in namespaces:
                metadata = ns['metadata']
                status = ns['status']
                
                print(f"\n  - {metadata['name']}")
                print(f"    状态: {status.get('phase')}")
                print(f"    创建时间: {metadata.get('creationTimestamp')}")
            
            return namespaces
        else:
            print(f"❌ 命名空间列表获取失败: {response.status_code if response else 'N/A'}")
            return None
    
    def test_list_pods(self, namespace: str = 'default') -> Optional[List[Dict]]:
        """测试5: 列出Pod"""
        print(f"\n测试5: 列出Pod (命名空间: {namespace})")
        
        response = self._request('GET', f'/api/v1/namespaces/{namespace}/pods')
        
        if response and response.status_code == 200:
            data = response.json()
            pods = data.get('items', [])
            print(f"✅ Pod列表获取成功: 共 {len(pods)} 个Pod")
            
            for pod in pods[:10]:  # 显示前10个
                metadata = pod['metadata']
                status = pod['status']
                spec = pod['spec']
                
                print(f"\n  Pod: {metadata['name']}")
                print(f"  - 命名空间: {metadata['namespace']}")
                print(f"  - 状态: {status.get('phase')}")
                print(f"  - Pod IP: {status.get('podIP')}")
                print(f"  - 节点: {spec.get('nodeName')}")
                
                # 容器状态
                container_statuses = status.get('containerStatuses', [])
                print(f"  - 容器:")
                for cs in container_statuses:
                    ready = '✓' if cs.get('ready') else '✗'
                    print(f"    [{ready}] {cs['name']} (重启次数: {cs.get('restartCount')})")
            
            return pods
        else:
            print(f"❌ Pod列表获取失败: {response.status_code if response else 'N/A'}")
            return None
    
    def test_get_pod_details(self, namespace: str, pod_name: str) -> Optional[Dict]:
        """测试6: 获取Pod详情"""
        print(f"\n测试6: 获取Pod详情 (命名空间: {namespace}, Pod: {pod_name})")
        
        response = self._request('GET', f'/api/v1/namespaces/{namespace}/pods/{pod_name}')
        
        if response and response.status_code == 200:
            pod = response.json()
            metadata = pod['metadata']
            status = pod['status']
            spec = pod['spec']
            
            print("✅ Pod详情获取成功:")
            print(f"  - 名称: {metadata['name']}")
            print(f"  - UID: {metadata['uid']}")
            print(f"  - 命名空间: {metadata['namespace']}")
            print(f"  - 状态: {status.get('phase')}")
            print(f"  - QoS类: {status.get('qosClass')}")
            
            # 标签
            labels = metadata.get('labels', {})
            if labels:
                print(f"  - 标签:")
                for key, value in labels.items():
                    print(f"    {key}: {value}")
            
            # 容器
            containers = spec.get('containers', [])
            print(f"  - 容器: {len(containers)} 个")
            for container in containers:
                print(f"    - {container['name']}")
                print(f"      镜像: {container['image']}")
                
                # 资源请求和限制
                resources = container.get('resources', {})
                requests = resources.get('requests', {})
                limits = resources.get('limits', {})
                
                if requests:
                    print(f"      请求: CPU={requests.get('cpu')}, Memory={requests.get('memory')}")
                if limits:
                    print(f"      限制: CPU={limits.get('cpu')}, Memory={limits.get('memory')}")
            
            return pod
        else:
            print(f"❌ Pod详情获取失败: {response.status_code if response else 'N/A'}")
            return None
    
    def test_list_deployments(self, namespace: str = 'default') -> Optional[List[Dict]]:
        """测试7: 列出Deployment"""
        print(f"\n测试7: 列出Deployment (命名空间: {namespace})")
        
        response = self._request('GET', f'/apis/apps/v1/namespaces/{namespace}/deployments')
        
        if response and response.status_code == 200:
            data = response.json()
            deployments = data.get('items', [])
            print(f"✅ Deployment列表获取成功: 共 {len(deployments)} 个Deployment")
            
            for deploy in deployments:
                metadata = deploy['metadata']
                spec = deploy['spec']
                status = deploy['status']
                
                print(f"\n  Deployment: {metadata['name']}")
                print(f"  - 副本数:")
                print(f"    期望: {spec.get('replicas')}")
                print(f"    当前: {status.get('replicas')}")
                print(f"    可用: {status.get('availableReplicas')}")
                print(f"    就绪: {status.get('readyReplicas')}")
                
                # 策略
                strategy = spec.get('strategy', {})
                print(f"  - 更新策略: {strategy.get('type')}")
            
            return deployments
        else:
            print(f"❌ Deployment列表获取失败: {response.status_code if response else 'N/A'}")
            return None
    
    def test_list_services(self, namespace: str = 'default') -> Optional[List[Dict]]:
        """测试8: 列出Service"""
        print(f"\n测试8: 列出Service (命名空间: {namespace})")
        
        response = self._request('GET', f'/api/v1/namespaces/{namespace}/services')
        
        if response and response.status_code == 200:
            data = response.json()
            services = data.get('items', [])
            print(f"✅ Service列表获取成功: 共 {len(services)} 个Service")
            
            for svc in services:
                metadata = svc['metadata']
                spec = svc['spec']
                
                print(f"\n  Service: {metadata['name']}")
                print(f"  - 类型: {spec.get('type')}")
                print(f"  - Cluster IP: {spec.get('clusterIP')}")
                
                # 端口
                ports = spec.get('ports', [])
                if ports:
                    print(f"  - 端口:")
                    for port in ports:
                        print(f"    {port.get('name', 'unnamed')}: {port.get('port')}/{port.get('protocol')} -> {port.get('targetPort')}")
                
                # External IP
                external_ips = spec.get('externalIPs', [])
                if external_ips:
                    print(f"  - External IPs: {', '.join(external_ips)}")
                
                # LoadBalancer
                if spec.get('type') == 'LoadBalancer':
                    status = svc.get('status', {})
                    lb = status.get('loadBalancer', {})
                    ingress = lb.get('ingress', [])
                    if ingress:
                        for ing in ingress:
                            print(f"  - LoadBalancer IP: {ing.get('ip', ing.get('hostname'))}")
            
            return services
        else:
            print(f"❌ Service列表获取失败: {response.status_code if response else 'N/A'}")
            return None
    
    def test_list_configmaps(self, namespace: str = 'default') -> Optional[List[Dict]]:
        """测试9: 列出ConfigMap"""
        print(f"\n测试9: 列出ConfigMap (命名空间: {namespace})")
        
        response = self._request('GET', f'/api/v1/namespaces/{namespace}/configmaps')
        
        if response and response.status_code == 200:
            data = response.json()
            configmaps = data.get('items', [])
            print(f"✅ ConfigMap列表获取成功: 共 {len(configmaps)} 个ConfigMap")
            
            for cm in configmaps[:5]:  # 显示前5个
                metadata = cm['metadata']
                cm_data = cm.get('data', {})
                
                print(f"\n  ConfigMap: {metadata['name']}")
                print(f"  - 数据项: {len(cm_data)} 个")
                
                # 显示数据项的键
                if cm_data:
                    print(f"  - 键:")
                    for key in list(cm_data.keys())[:5]:
                        value_preview = str(cm_data[key])[:50]
                        print(f"    {key}: {value_preview}...")
            
            return configmaps
        else:
            print(f"❌ ConfigMap列表获取失败: {response.status_code if response else 'N/A'}")
            return None
    
    def test_list_secrets(self, namespace: str = 'default') -> Optional[List[Dict]]:
        """测试10: 列出Secret"""
        print(f"\n测试10: 列出Secret (命名空间: {namespace})")
        
        response = self._request('GET', f'/api/v1/namespaces/{namespace}/secrets')
        
        if response and response.status_code == 200:
            data = response.json()
            secrets = data.get('items', [])
            print(f"✅ Secret列表获取成功: 共 {len(secrets)} 个Secret")
            
            for secret in secrets[:5]:  # 显示前5个
                metadata = secret['metadata']
                secret_type = secret.get('type')
                secret_data = secret.get('data', {})
                
                print(f"\n  Secret: {metadata['name']}")
                print(f"  - 类型: {secret_type}")
                print(f"  - 数据项: {len(secret_data)} 个")
                
                # 只显示键名,不显示值(安全考虑)
                if secret_data:
                    print(f"  - 键: {', '.join(list(secret_data.keys())[:5])}")
            
            return secrets
        else:
            print(f"❌ Secret列表获取失败: {response.status_code if response else 'N/A'}")
            return None
    
    def test_list_pv(self) -> Optional[List[Dict]]:
        """测试11: 列出PersistentVolume"""
        print("\n测试11: 列出PersistentVolume")
        
        response = self._request('GET', '/api/v1/persistentvolumes')
        
        if response and response.status_code == 200:
            data = response.json()
            pvs = data.get('items', [])
            print(f"✅ PV列表获取成功: 共 {len(pvs)} 个PV")
            
            for pv in pvs:
                metadata = pv['metadata']
                spec = pv['spec']
                status = pv['status']
                
                print(f"\n  PV: {metadata['name']}")
                print(f"  - 容量: {spec.get('capacity', {}).get('storage')}")
                print(f"  - 访问模式: {', '.join(spec.get('accessModes', []))}")
                print(f"  - 回收策略: {spec.get('persistentVolumeReclaimPolicy')}")
                print(f"  - 状态: {status.get('phase')}")
                print(f"  - StorageClass: {spec.get('storageClassName', 'default')}")
            
            return pvs
        else:
            print(f"❌ PV列表获取失败: {response.status_code if response else 'N/A'}")
            return None
    
    def test_list_pvc(self, namespace: str = 'default') -> Optional[List[Dict]]:
        """测试12: 列出PersistentVolumeClaim"""
        print(f"\n测试12: 列出PersistentVolumeClaim (命名空间: {namespace})")
        
        response = self._request('GET', f'/api/v1/namespaces/{namespace}/persistentvolumeclaims')
        
        if response and response.status_code == 200:
            data = response.json()
            pvcs = data.get('items', [])
            print(f"✅ PVC列表获取成功: 共 {len(pvcs)} 个PVC")
            
            for pvc in pvcs:
                metadata = pvc['metadata']
                spec = pvc['spec']
                status = pvc['status']
                
                print(f"\n  PVC: {metadata['name']}")
                print(f"  - 请求容量: {spec.get('resources', {}).get('requests', {}).get('storage')}")
                print(f"  - 访问模式: {', '.join(spec.get('accessModes', []))}")
                print(f"  - 状态: {status.get('phase')}")
                print(f"  - 绑定的PV: {spec.get('volumeName', 'N/A')}")
                print(f"  - StorageClass: {spec.get('storageClassName', 'default')}")
            
            return pvcs
        else:
            print(f"❌ PVC列表获取失败: {response.status_code if response else 'N/A'}")
            return None
    
    def test_cluster_health(self) -> bool:
        """测试13: 集群健康检查"""
        print("\n测试13: 集群健康检查")
        
        # 检查 /healthz
        response = self._request('GET', '/healthz')
        
        if response and response.status_code == 200:
            print("✅ 集群健康检查通过:")
            print(f"  - /healthz: {response.text}")
            
            # 检查详细健康信息
            response_verbose = self._request('GET', '/healthz?verbose=true')
            if response_verbose and response_verbose.status_code == 200:
                health_checks = response_verbose.text.split('\n')
                print(f"  - 健康检查项:")
                for check in health_checks[:10]:  # 显示前10项
                    if check:
                        print(f"    {check}")
            
            return True
        else:
            print(f"❌ 集群健康检查失败: {response.status_code if response else 'N/A'}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 70)
        print("Kubernetes API 完整测试套件")
        print("=" * 70)
        
        # API基础测试
        self.test_api_versions()
        self.test_api_groups()
        
        # 集群资源测试
        self.test_list_nodes()
        namespaces = self.test_list_namespaces()
        
        # 使用第一个非系统命名空间进行测试
        test_namespace = 'default'
        if namespaces:
            for ns in namespaces:
                ns_name = ns['metadata']['name']
                if not ns_name.startswith('kube-') and ns_name != 'default':
                    test_namespace = ns_name
                    break
        
        # 工作负载测试
        pods = self.test_list_pods(test_namespace)
        if pods:
            # 获取第一个Pod的详情
            pod_name = pods[0]['metadata']['name']
            self.test_get_pod_details(test_namespace, pod_name)
        
        self.test_list_deployments(test_namespace)
        self.test_list_services(test_namespace)
        
        # 配置测试
        self.test_list_configmaps(test_namespace)
        self.test_list_secrets(test_namespace)
        
        # 存储测试
        self.test_list_pv()
        self.test_list_pvc(test_namespace)
        
        # 健康检查
        self.test_cluster_health()
        
        print("\n" + "=" * 70)
        print("所有测试完成")
        print("=" * 70)


if __name__ == "__main__":
    # 配置参数
    
    # 方式1: 使用ServiceAccount Token (Pod内部)
    # api_server = "https://kubernetes.default.svc"
    # with open('/var/run/secrets/kubernetes.io/serviceaccount/token') as f:
    #     token = f.read()
    
    # 方式2: 使用kubectl proxy (推荐用于测试)
    # 首先运行: kubectl proxy --port=8001
    api_server = "http://localhost:8001"
    token = None
    
    # 方式3: 使用kubeconfig中的凭证
    # 需要手动实现kubeconfig解析
    
    # 创建测试实例
    tester = KubernetesAPITest(api_server, token)
    
    # 运行所有测试
    tester.run_all_tests()

