#!/usr/bin/env python3
"""
vSphere版本检查脚本
注意: VMware vSphere不提供公开API，此脚本提供基本框架
实际使用时需要手动维护最新版本信息
"""

import re
import sys

def get_known_latest_vsphere_version():
    """
    返回已知的最新vSphere版本
    需要定期手动更新此信息
    """
    # TODO: 定期手动更新此版本号
    return "8.0.2"

def get_project_vsphere_version():
    """从项目文档中提取当前vSphere版本"""
    try:
        with open('2025年技术标准最终对齐报告.md', 'r', encoding='utf-8') as f:
            content = f.read()
            
        match = re.search(r'vSphere:\s*(\d+\.\d+\.\d+)', content)
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
    
    if current_parts[0] < latest_parts[0] or current_parts[1] < latest_parts[1]:
        return 'major'
    elif current_parts[2] < latest_parts[2]:
        return 'minor'
    else:
        return 'up-to-date'

def main():
    project_version = get_project_vsphere_version()
    latest_version = get_known_latest_vsphere_version()
    
    print(f"Project vSphere version: {project_version}")
    print(f"Known latest vSphere version: {latest_version}")
    print("Note: vSphere version check requires manual updates")
    
    if not project_version:
        print("Could not determine project version")
        print("::set-output name=update_needed::false")
        sys.exit(0)
    
    result = compare_versions(project_version, latest_version)
    
    if result == 'up-to-date':
        print("✅ vSphere version is up to date (based on known version)")
        print("::set-output name=update_needed::false")
    else:
        print(f"⚠️ vSphere version may need update: {project_version} -> {latest_version}")
        print(f"Update type: {result}")
        print("Please verify manually at: https://docs.vmware.com/")
        print("::set-output name=update_needed::true")
        print(f"::set-output name=current_version::{project_version}")
        print(f"::set-output name=latest_version::{latest_version}")
        print(f"::set-output name=update_type::{result}")
        
        with open('vsphere_update.txt', 'w') as f:
            f.write(f"vSphere|{project_version}|{latest_version}|{result}|需人工验证\n")

if __name__ == '__main__':
    main()

