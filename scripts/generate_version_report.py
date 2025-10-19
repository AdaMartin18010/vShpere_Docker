#!/usr/bin/env python3
"""
生成版本检查报告
"""

import os
from datetime import datetime

def read_update_file(filename):
    """读取更新文件"""
    if not os.path.exists(filename):
        return None
    
    with open(filename, 'r') as f:
        line = f.read().strip()
        if line:
            return line.split('|')
    return None

def generate_report():
    """生成Markdown格式的报告"""
    report = []
    report.append(f"# 技术版本更新检查报告\n")
    report.append(f"**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
    report.append(f"**自动生成**: GitHub Actions\n")
    report.append("\n---\n")
    
    # 读取各个更新文件
    updates = []
    for tech in ['k8s', 'docker', 'podman', 'vsphere']:
        data = read_update_file(f'{tech}_update.txt')
        if data:
            updates.append(data)
    
    if not updates:
        report.append("\n## ✅ 所有技术版本都是最新的\n")
        report.append("无需更新。\n")
    else:
        report.append("\n## ⚠️ 检测到版本更新\n")
        report.append("\n| 技术 | 当前版本 | 最新版本 | 更新类型 | 备注 |\n")
        report.append("|------|---------|---------|---------|------|\n")
        
        for update in updates:
            tech = update[0]
            current = update[1]
            latest = update[2]
            update_type = update[3]
            note = update[4] if len(update) > 4 else '-'
            
            report.append(f"| {tech} | {current} | {latest} | {update_type} | {note} |\n")
        
        report.append("\n## 📋 更新建议\n")
        report.append("\n根据[更新SLA](../README.md#版本更新sla):\n")
        report.append("- **重大版本(major)**: 发布后1个月内更新\n")
        report.append("- **次要版本(minor)**: 发布后2个月内更新\n")
        report.append("- **补丁版本(patch)**: 按需评估\n")
        report.append("- **安全漏洞**: 发布后1周内更新\n")
        
        report.append("\n## ✅ 更新检查清单\n")
        for update in updates:
            tech = update[0]
            report.append(f"\n### {tech}\n")
            report.append(f"- [ ] 查看发行说明\n")
            report.append(f"- [ ] 评估影响范围\n")
            report.append(f"- [ ] 更新技术文档\n")
            report.append(f"- [ ] 更新代码示例\n")
            report.append(f"- [ ] 更新最佳实践\n")
            report.append(f"- [ ] 测试验证\n")
            report.append(f"- [ ] 更新版本对齐报告\n")
        
        report.append("\n## 🔗 参考链接\n")
        report.append("- [Kubernetes Releases](https://github.com/kubernetes/kubernetes/releases)\n")
        report.append("- [Docker Releases](https://github.com/moby/moby/releases)\n")
        report.append("- [Podman Releases](https://github.com/containers/podman/releases)\n")
        report.append("- [VMware vSphere Docs](https://docs.vmware.com/)\n")
        
        report.append("\n---\n")
        report.append(f"\n*本报告由自动化工具生成，请人工审核并评估是否需要更新*\n")
    
    # 写入报告文件
    with open('version_report.md', 'w') as f:
        f.write(''.join(report))
    
    print("Report generated: version_report.md")

if __name__ == '__main__':
    generate_report()

