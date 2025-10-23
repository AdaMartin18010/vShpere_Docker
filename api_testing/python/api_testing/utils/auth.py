#!/usr/bin/env python3
"""
认证工具模块
提供各种API的认证功能
"""

import os
import json
import base64
import requests
from typing import Optional, Dict
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_vsphere_session(server: str, username: str, password: str, verify_ssl: bool = False) -> Optional[str]:
    """
    获取vSphere会话ID
    
    Args:
        server: vCenter服务器地址
        username: 用户名
        password: 密码
        verify_ssl: 是否验证SSL证书
    
    Returns:
        session_id: 会话ID,失败返回None
    """
    try:
        url = f"https://{server}/api/session"
        response = requests.post(
            url,
            auth=(username, password),
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 201:
            session_id = response.json().get('value')
            return session_id
        else:
            print(f"vSphere认证失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"vSphere认证异常: {e}")
        return None


def get_k8s_token(kubeconfig_path: Optional[str] = None, context: Optional[str] = None) -> Optional[str]:
    """
    从kubeconfig获取Kubernetes Token
    
    Args:
        kubeconfig_path: kubeconfig文件路径,默认为~/.kube/config
        context: 上下文名称,默认使用当前上下文
    
    Returns:
        token: Bearer Token,失败返回None
    """
    try:
        import yaml
        
        if kubeconfig_path is None:
            kubeconfig_path = os.path.expanduser('~/.kube/config')
        
        if not os.path.exists(kubeconfig_path):
            print(f"kubeconfig文件不存在: {kubeconfig_path}")
            return None
        
        with open(kubeconfig_path, 'r') as f:
            kubeconfig = yaml.safe_load(f)
        
        # 获取当前上下文
        if context is None:
            context = kubeconfig.get('current-context')
        
        # 查找上下文配置
        contexts = kubeconfig.get('contexts', [])
        current_context = next((c for c in contexts if c['name'] == context), None)
        
        if not current_context:
            print(f"找不到上下文: {context}")
            return None
        
        user_name = current_context['context']['user']
        
        # 查找用户配置
        users = kubeconfig.get('users', [])
        user = next((u for u in users if u['name'] == user_name), None)
        
        if not user:
            print(f"找不到用户: {user_name}")
            return None
        
        user_config = user['user']
        
        # 尝试从不同位置获取token
        if 'token' in user_config:
            return user_config['token']
        elif 'exec' in user_config:
            # 执行命令获取token (如aws eks get-token)
            import subprocess
            exec_config = user_config['exec']
            command = exec_config['command']
            args = exec_config.get('args', [])
            
            result = subprocess.run(
                [command] + args,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                token_data = json.loads(result.stdout)
                return token_data['status']['token']
        
        print("无法从kubeconfig获取token")
        return None
    except Exception as e:
        print(f"获取K8s Token异常: {e}")
        return None


def get_k8s_serviceaccount_token(namespace: str = 'default', 
                                  service_account: str = 'default',
                                  api_server: Optional[str] = None) -> Optional[str]:
    """
    从ServiceAccount获取Kubernetes Token (Pod内部使用)
    
    Args:
        namespace: 命名空间
        service_account: ServiceAccount名称
        api_server: API服务器地址
    
    Returns:
        token: Bearer Token,失败返回None
    """
    try:
        # 尝试从默认位置读取token (Pod内部)
        token_path = f'/var/run/secrets/kubernetes.io/serviceaccount/token'
        
        if os.path.exists(token_path):
            with open(token_path, 'r') as f:
                return f.read().strip()
        
        # 如果不在Pod内部,尝试使用kubectl获取
        import subprocess
        
        result = subprocess.run(
            ['kubectl', 'get', 'secret', 
             '-n', namespace,
             '-o', 'jsonpath={.items[?(@.metadata.annotations.kubernetes\.io/service-account\.name=="' + service_account + '")].data.token}'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and result.stdout:
            # Base64解码
            token_b64 = result.stdout
            token = base64.b64decode(token_b64).decode('utf-8')
            return token
        
        print("无法获取ServiceAccount Token")
        return None
    except Exception as e:
        print(f"获取ServiceAccount Token异常: {e}")
        return None


def get_docker_auth(registry: str = 'https://index.docker.io/v1/',
                    username: Optional[str] = None,
                    password: Optional[str] = None) -> Optional[Dict]:
    """
    获取Docker认证配置
    
    Args:
        registry: Docker Registry地址
        username: 用户名 (可选)
        password: 密码 (可选)
    
    Returns:
        auth_config: 认证配置字典,失败返回None
    """
    try:
        # 尝试从~/.docker/config.json读取
        docker_config_path = os.path.expanduser('~/.docker/config.json')
        
        if os.path.exists(docker_config_path):
            with open(docker_config_path, 'r') as f:
                docker_config = json.load(f)
            
            # 查找registry的认证信息
            auths = docker_config.get('auths', {})
            
            if registry in auths:
                auth_data = auths[registry]
                
                if 'auth' in auth_data:
                    # Base64解码 username:password
                    auth_decoded = base64.b64decode(auth_data['auth']).decode('utf-8')
                    username, password = auth_decoded.split(':', 1)
                    
                    return {
                        'username': username,
                        'password': password,
                        'registry': registry
                    }
        
        # 如果提供了用户名和密码,使用它们
        if username and password:
            return {
                'username': username,
                'password': password,
                'registry': registry
            }
        
        print("无法获取Docker认证信息")
        return None
    except Exception as e:
        print(f"获取Docker认证信息异常: {e}")
        return None


def get_etcd_credentials(ca_cert: Optional[str] = None,
                         cert: Optional[str] = None,
                         key: Optional[str] = None) -> Optional[Dict]:
    """
    获取etcd客户端证书配置
    
    Args:
        ca_cert: CA证书路径
        cert: 客户端证书路径
        key: 客户端密钥路径
    
    Returns:
        credentials: 证书配置字典
    """
    try:
        if ca_cert and cert and key:
            if not all(os.path.exists(p) for p in [ca_cert, cert, key]):
                print("证书文件不存在")
                return None
            
            return {
                'ca_cert': ca_cert,
                'cert': cert,
                'key': key
            }
        
        # 尝试从默认位置读取
        default_paths = {
            'ca_cert': '/etc/etcd/ca.crt',
            'cert': '/etc/etcd/client.crt',
            'key': '/etc/etcd/client.key'
        }
        
        if all(os.path.exists(p) for p in default_paths.values()):
            return default_paths
        
        print("无法获取etcd证书")
        return None
    except Exception as e:
        print(f"获取etcd证书异常: {e}")
        return None


def get_consul_token(token_file: Optional[str] = None) -> Optional[str]:
    """
    获取Consul ACL Token
    
    Args:
        token_file: Token文件路径
    
    Returns:
        token: Consul Token,失败返回None
    """
    try:
        # 从环境变量获取
        token = os.environ.get('CONSUL_HTTP_TOKEN')
        if token:
            return token
        
        # 从文件获取
        if token_file and os.path.exists(token_file):
            with open(token_file, 'r') as f:
                return f.read().strip()
        
        # 从默认位置获取
        default_token_file = os.path.expanduser('~/.consul-token')
        if os.path.exists(default_token_file):
            with open(default_token_file, 'r') as f:
                return f.read().strip()
        
        print("无法获取Consul Token")
        return None
    except Exception as e:
        print(f"获取Consul Token异常: {e}")
        return None


def validate_token(token: str, api_server: str, verify_ssl: bool = False) -> bool:
    """
    验证Token有效性
    
    Args:
        token: Bearer Token
        api_server: API服务器地址
        verify_ssl: 是否验证SSL证书
    
    Returns:
        valid: Token是否有效
    """
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(
            f"{api_server}/api",
            headers=headers,
            verify=verify_ssl,
            timeout=10
        )
        
        return response.status_code == 200
    except Exception as e:
        print(f"Token验证异常: {e}")
        return False


# 测试函数
if __name__ == "__main__":
    print("=" * 60)
    print("认证工具测试")
    print("=" * 60)
    
    # 测试vSphere认证
    print("\n测试vSphere认证:")
    # session_id = get_vsphere_session("vcenter.example.com", "admin", "password")
    # print(f"Session ID: {session_id}")
    
    # 测试K8s Token获取
    print("\n测试K8s Token获取:")
    # token = get_k8s_token()
    # print(f"Token: {token[:20] if token else None}...")
    
    # 测试Docker认证
    print("\n测试Docker认证:")
    # auth = get_docker_auth()
    # print(f"Auth: {auth}")
    
    print("\n所有认证工具测试完成")

