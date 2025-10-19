#!/usr/bin/env python3
"""
Kubernetes版本检查脚本
检查项目中的Kubernetes版本是否为最新稳定版本
"""

import requests
import re
import os
import sys

def get_latest_k8s_version():
    """从GitHub API获取Kubernetes最新稳定版本"""
    try:
        url = "https://api.github.com/repos/kubernetes/kubernetes/releases/latest"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        latest = response.json()['tag_name']
        # 去掉'v'前缀
        return latest.lstrip('v')
    except Exception as e:
        print(f"Error fetching Kubernetes version: {e}", file=sys.stderr)
        return None

def get_project_k8s_version():
    """从项目文档中提取当前Kubernetes版本"""
    try:
        # 读取技术标准对齐报告
        with open('2025年技术标准最终对齐报告.md', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 提取Kubernetes版本
        match = re.search(r'Kubernetes:\s*(\d+\.\d+\.\d+)', content)
        if match:
            return match.group(1)
        
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
    
    # 比较主版本和次版本
    if current_parts[0] < latest_parts[0] or current_parts[1] < latest_parts[1]:
        return 'major'
    # 比较补丁版本
    elif current_parts[2] < latest_parts[2]:
        return 'minor'
    else:
        return 'up-to-date'

def main():
    project_version = get_project_k8s_version()
    latest_version = get_latest_k8s_version()
    
    print(f"Project Kubernetes version: {project_version}")
    print(f"Latest Kubernetes version: {latest_version}")
    
    if not project_version or not latest_version:
        print("Could not determine versions")
        sys.exit(1)
    
    result = compare_versions(project_version, latest_version)
    
    if result == 'up-to-date':
        print("✅ Kubernetes version is up to date")
        print("::set-output name=update_needed::false")
    else:
        print(f"⚠️ Kubernetes version update available: {project_version} -> {latest_version}")
        print(f"Update type: {result}")
        print("::set-output name=update_needed::true")
        print(f"::set-output name=current_version::{project_version}")
        print(f"::set-output name=latest_version::{latest_version}")
        print(f"::set-output name=update_type::{result}")
        
        # 写入文件供后续步骤使用
        with open('k8s_update.txt', 'w') as f:
            f.write(f"Kubernetes|{project_version}|{latest_version}|{result}\n")

if __name__ == '__main__':
    main()

