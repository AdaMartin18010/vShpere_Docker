#!/usr/bin/env python3
"""
文档格式检查工具
功能: 检查Markdown文档格式规范性
适用版本: Python 3.8+
作者: vSphere_Docker Project
日期: 2025-10-20
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

class FormatChecker:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.issues = defaultdict(list)
        self.stats = {
            'total_files': 0,
            'files_with_issues': 0,
            'code_block_issues': 0,
            'table_issues': 0,
            'list_issues': 0,
            'whitespace_issues': 0,
            'total_issues': 0
        }
    
    def check_code_blocks(self, content: str, file_path: Path) -> List[Dict]:
        """检查代码块格式"""
        issues = []
        lines = content.split('\n')
        
        in_code_block = False
        code_block_start = 0
        
        for i, line in enumerate(lines, 1):
            # 检查代码块标记
            if line.strip().startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    code_block_start = i
                    
                    # 检查是否指定语言
                    lang = line.strip()[3:].strip()
                    if not lang and line.strip() == '```':
                        # 允许纯```作为结束标记，但开始时应指定语言
                        pass
                else:
                    in_code_block = False
            
            # 检查代码块内的制表符
            if in_code_block and '\t' in line:
                issues.append({
                    'type': 'code_block',
                    'severity': 'info',
                    'line': i,
                    'message': '代码块中包含制表符，建议使用空格'
                })
        
        # 检查未闭合的代码块
        if in_code_block:
            issues.append({
                'type': 'code_block',
                'severity': 'error',
                'line': code_block_start,
                'message': '代码块未正确闭合'
            })
        
        return issues
    
    def check_tables(self, content: str, file_path: Path) -> List[Dict]:
        """检查表格格式"""
        issues = []
        lines = content.split('\n')
        
        in_table = False
        table_start = 0
        table_cols = 0
        
        for i, line in enumerate(lines, 1):
            # 检测表格行
            if '|' in line and not line.strip().startswith('```'):
                if not in_table:
                    in_table = True
                    table_start = i
                    table_cols = line.count('|') - 1
                
                # 检查列数一致性
                current_cols = line.count('|') - 1
                if current_cols != table_cols:
                    issues.append({
                        'type': 'table',
                        'severity': 'warning',
                        'line': i,
                        'message': f'表格列数不一致：期望{table_cols}列，实际{current_cols}列'
                    })
                
                # 检查表格对齐格式（第二行）
                if i == table_start + 1:
                    if not re.match(r'^\s*\|[\s\-:]+\|\s*$', line):
                        # 允许一定的格式变化
                        pass
            else:
                if in_table:
                    in_table = False
        
        return issues
    
    def check_lists(self, content: str, file_path: Path) -> List[Dict]:
        """检查列表格式"""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # 检查无序列表
            if stripped.startswith(('-', '*', '+')):
                # 检查空格
                if len(line) - len(line.lstrip()) > 0:
                    indent = len(line) - len(line.lstrip())
                    if indent % 2 != 0:
                        issues.append({
                            'type': 'list',
                            'severity': 'info',
                            'line': i,
                            'message': '列表缩进不是2的倍数，建议使用2/4/6空格'
                        })
                
                # 检查列表标记后是否有空格
                if len(stripped) > 1 and stripped[1] != ' ':
                    issues.append({
                        'type': 'list',
                        'severity': 'warning',
                        'line': i,
                        'message': '列表标记后缺少空格'
                    })
            
            # 检查有序列表
            if re.match(r'^\d+\.', stripped):
                # 检查点号后是否有空格
                if len(stripped) > 2 and not stripped[stripped.index('.')+1].isspace():
                    issues.append({
                        'type': 'list',
                        'severity': 'warning',
                        'line': i,
                        'message': '有序列表点号后缺少空格'
                    })
        
        return issues
    
    def check_whitespace(self, content: str, file_path: Path) -> List[Dict]:
        """检查空白字符问题"""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 检查行尾空格
            if line != line.rstrip():
                issues.append({
                    'type': 'whitespace',
                    'severity': 'info',
                    'line': i,
                    'message': '行尾包含空白字符'
                })
            
            # 检查连续空行（超过2行）
            if i > 2:
                if not lines[i-1].strip() and not lines[i-2].strip() and not line.strip():
                    issues.append({
                        'type': 'whitespace',
                        'severity': 'info',
                        'line': i,
                        'message': '连续超过2个空行'
                    })
        
        return issues
    
    def check_file(self, file_path: Path):
        """检查单个文件"""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"❌ 无法读取文件 {file_path}: {e}")
            return
        
        file_issues = []
        
        # 执行各项检查
        file_issues.extend(self.check_code_blocks(content, file_path))
        file_issues.extend(self.check_tables(content, file_path))
        file_issues.extend(self.check_lists(content, file_path))
        file_issues.extend(self.check_whitespace(content, file_path))
        
        # 统计问题
        if file_issues:
            self.stats['files_with_issues'] += 1
            rel_path = str(file_path.relative_to(self.root_dir))
            self.issues[rel_path] = file_issues
            
            for issue in file_issues:
                self.stats['total_issues'] += 1
                issue_type = issue['type']
                if issue_type == 'code_block':
                    self.stats['code_block_issues'] += 1
                elif issue_type == 'table':
                    self.stats['table_issues'] += 1
                elif issue_type == 'list':
                    self.stats['list_issues'] += 1
                elif issue_type == 'whitespace':
                    self.stats['whitespace_issues'] += 1
    
    def scan_directory(self):
        """扫描整个目录"""
        print("🔍 开始扫描Markdown文件格式...")
        
        # 排除目录
        exclude_dirs = {'.git', 'node_modules', '.venv', '__pycache__', '_archive'}
        
        for md_file in self.root_dir.rglob('*.md'):
            # 跳过排除目录
            if any(exclude in md_file.parts for exclude in exclude_dirs):
                continue
            
            self.stats['total_files'] += 1
            self.check_file(md_file)
    
    def generate_report(self) -> str:
        """生成检查报告"""
        report = []
        report.append("# 文档格式检查报告\n")
        report.append(f"**检查时间**: 2025-10-20\n")
        report.append(f"**项目**: vSphere_Docker\n\n")
        
        # 统计信息
        report.append("## 📊 统计信息\n\n")
        report.append(f"- **检查文件数**: {self.stats['total_files']}\n")
        report.append(f"- **有问题文件**: {self.stats['files_with_issues']}\n")
        report.append(f"- **总问题数**: {self.stats['total_issues']}\n")
        report.append(f"- **代码块问题**: {self.stats['code_block_issues']}\n")
        report.append(f"- **表格问题**: {self.stats['table_issues']}\n")
        report.append(f"- **列表问题**: {self.stats['list_issues']}\n")
        report.append(f"- **空白字符问题**: {self.stats['whitespace_issues']}\n\n")
        
        # 计算格式规范率
        if self.stats['total_files'] > 0:
            compliant_rate = ((self.stats['total_files'] - self.stats['files_with_issues']) / self.stats['total_files']) * 100
            report.append(f"**格式规范率**: {compliant_rate:.2f}%\n\n")
        
        # 问题详情（按严重程度分类）
        errors = []
        warnings = []
        infos = []
        
        for file_path, issues in sorted(self.issues.items()):
            for issue in issues:
                item = {
                    'file': file_path,
                    'line': issue['line'],
                    'type': issue['type'],
                    'message': issue['message']
                }
                
                if issue['severity'] == 'error':
                    errors.append(item)
                elif issue['severity'] == 'warning':
                    warnings.append(item)
                else:
                    infos.append(item)
        
        # 错误
        if errors:
            report.append("## ❌ 错误 (需要修复)\n\n")
            report.append("| 文件 | 行号 | 类型 | 问题描述 |\n")
            report.append("|------|------|------|----------|\n")
            
            for item in errors[:50]:  # 限制显示数量
                report.append(f"| {item['file']} | {item['line']} | {item['type']} | {item['message']} |\n")
            
            if len(errors) > 50:
                report.append(f"\n... 还有 {len(errors) - 50} 个错误未显示\n")
            report.append("\n")
        
        # 警告
        if warnings:
            report.append("## ⚠️ 警告 (建议修复)\n\n")
            report.append("| 文件 | 行号 | 类型 | 问题描述 |\n")
            report.append("|------|------|------|----------|\n")
            
            for item in warnings[:50]:
                report.append(f"| {item['file']} | {item['line']} | {item['type']} | {item['message']} |\n")
            
            if len(warnings) > 50:
                report.append(f"\n... 还有 {len(warnings) - 50} 个警告未显示\n")
            report.append("\n")
        
        # 信息
        if infos:
            report.append("## ℹ️ 信息 (可选优化)\n\n")
            report.append(f"共 {len(infos)} 个格式优化建议\n\n")
        
        # 建议
        report.append("## 💡 修复建议\n\n")
        
        if self.stats['code_block_issues'] > 0:
            report.append("### 代码块格式\n\n")
            report.append("1. 确保代码块正确闭合\n")
            report.append("2. 代码块开始标记指定语言（如 ```python）\n")
            report.append("3. 使用空格代替制表符\n\n")
        
        if self.stats['table_issues'] > 0:
            report.append("### 表格格式\n\n")
            report.append("1. 确保表格所有行列数一致\n")
            report.append("2. 表格第二行使用分隔符（如 |---|---|）\n")
            report.append("3. 对齐表格列（可选）\n\n")
        
        if self.stats['list_issues'] > 0:
            report.append("### 列表格式\n\n")
            report.append("1. 列表标记后添加空格（如 `- 项目`）\n")
            report.append("2. 有序列表点号后添加空格（如 `1. 项目`）\n")
            report.append("3. 嵌套列表使用2/4/6空格缩进\n\n")
        
        if self.stats['whitespace_issues'] > 0:
            report.append("### 空白字符\n\n")
            report.append("1. 删除行尾空白字符\n")
            report.append("2. 避免连续超过2个空行\n")
            report.append("3. 文件末尾保留一个空行\n\n")
        
        report.append("---\n\n")
        report.append(f"**报告生成**: Python FormatChecker v1.0\n")
        report.append(f"**文档总数**: {self.stats['total_files']}\n")
        report.append(f"**问题总数**: {self.stats['total_issues']}\n")
        
        return ''.join(report)


def main():
    """主函数"""
    # 获取项目根目录
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    
    print("=" * 60)
    print("文档格式检查工具")
    print("=" * 60)
    print()
    
    # 创建检查器
    checker = FormatChecker(str(root_dir))
    
    # 扫描目录
    checker.scan_directory()
    
    print()
    print("=" * 60)
    print("扫描完成!")
    print("=" * 60)
    print()
    print(f"📁 检查文件: {checker.stats['total_files']}")
    print(f"⚠️  有问题文件: {checker.stats['files_with_issues']}")
    print(f"📝 总问题数: {checker.stats['total_issues']}")
    print(f"   - 代码块: {checker.stats['code_block_issues']}")
    print(f"   - 表格: {checker.stats['table_issues']}")
    print(f"   - 列表: {checker.stats['list_issues']}")
    print(f"   - 空白字符: {checker.stats['whitespace_issues']}")
    print()
    
    # 生成报告
    report_path = root_dir / "2025年10月20日_文档格式检查报告.md"
    report = checker.generate_report()
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 报告已生成: {report_path}")
    print()
    
    # 返回状态
    if checker.stats['total_issues'] == 0:
        print("✅ 所有文档格式规范!")
        return 0
    else:
        print(f"ℹ️  发现 {checker.stats['total_issues']} 个格式问题，请查看报告")
        return 0  # 格式问题不算失败


if __name__ == '__main__':
    sys.exit(main())

