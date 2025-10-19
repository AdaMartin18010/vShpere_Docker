#!/usr/bin/env python3
"""
Podman版本检查脚本
"""

import requests
import re
import sys

def get_latest_podman_version():
    """从GitHub API获取Podman最新稳定版本"""
    try:
        url = "https://api.github.com/repos/containers/podman/releases/latest"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        latest = response.json()['tag_name']
        return latest.lstrip('v')
    except Exception as e:
        print(f"Error fetching Podman version: {e}", file=sys.stderr)
        return None

def get_project_podman_version():
    """从项目文档中提取当前Podman版本"""
    try:
        # 尝试从Podman README读取
        with open('Container/02_Podman技术详解/README.md', 'r', encoding='utf-8') as f:
            content = f.read()
            
        match = re.search(r'Podman\s+(\d+\.\d+)', content)
        if match:
            return match.group(1) + '.0'  # 添加补丁版本
        
        return None
    except Exception as e:
        print(f"Error reading project version: {e}", file=sys.stderr)
        return None

def compare_versions(current, latest):
    """比较版本号"""
    if not current or not latest:
        return None
    
    current_parts = [int(x) for x in current.split('.')]
    latest_parts = [int(x) for x in latest.split('.')]
    
    if current_parts[0] < latest_parts[0] or current_parts[1] < latest_parts[1]:
        return 'major'
    elif current_parts[2] < latest_parts[2]:
        return 'minor'
    else:
        return 'up-to-date'

def main():
    project_version = get_project_podman_version()
    latest_version = get_latest_podman_version()
    
    print(f"Project Podman version: {project_version}")
    print(f"Latest Podman version: {latest_version}")
    
    if not project_version or not latest_version:
        print("Could not determine versions")
        print("::set-output name=update_needed::false")
        sys.exit(0)
    
    result = compare_versions(project_version, latest_version)
    
    if result == 'up-to-date':
        print("✅ Podman version is up to date")
        print("::set-output name=update_needed::false")
    else:
        print(f"⚠️ Podman version update available: {project_version} -> {latest_version}")
        print(f"Update type: {result}")
        print("::set-output name=update_needed::true")
        print(f"::set-output name=current_version::{project_version}")
        print(f"::set-output name=latest_version::{latest_version}")
        print(f"::set-output name=update_type::{result}")
        
        with open('podman_update.txt', 'w') as f:
            f.write(f"Podman|{project_version}|{latest_version}|{result}\n")

if __name__ == '__main__':
    main()

