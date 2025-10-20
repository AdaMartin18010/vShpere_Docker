#!/usr/bin/env python3
"""
链接有效性检查工具
功能: 检查Markdown文档中的所有链接
适用版本: Python 3.8+
作者: vSphere_Docker Project
日期: 2025-10-20
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict
from collections import defaultdict

class LinkChecker:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.results = defaultdict(list)
        self.stats = {
            'total_files': 0,
            'total_links': 0,
            'valid_links': 0,
            'invalid_links': 0,
            'external_links': 0
        }
    
    def extract_links(self, content: str, file_path: Path) -> List[Tuple[str, str, int]]:
        """
        提取Markdown文件中的链接
        返回: [(link_text, link_url, line_number), ...]
        """
        links = []
        
        # 匹配Markdown链接: [text](url)
        pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        
        for line_num, line in enumerate(content.split('\n'), 1):
            for match in re.finditer(pattern, line):
                text = match.group(1)
                url = match.group(2)
                links.append((text, url, line_num))
        
        return links
    
    def is_external_link(self, url: str) -> bool:
        """判断是否为外部链接"""
        return url.startswith(('http://', 'https://', 'ftp://'))
    
    def check_internal_link(self, link_url: str, source_file: Path) -> bool:
        """检查内部链接是否有效"""
        # 移除锚点
        link_path = link_url.split('#')[0]
        
        if not link_path:
            # 仅锚点链接，认为有效
            return True
        
        # 处理相对路径
        if link_path.startswith('/'):
            # 绝对路径（相对于仓库根目录）
            target = self.root_dir / link_path.lstrip('/')
        else:
            # 相对路径（相对于当前文件）
            target = (source_file.parent / link_path).resolve()
        
        return target.exists()
    
    def check_file(self, file_path: Path):
        """检查单个文件中的所有链接"""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"❌ 无法读取文件 {file_path}: {e}")
            return
        
        links = self.extract_links(content, file_path)
        
        for text, url, line_num in links:
            self.stats['total_links'] += 1
            
            if self.is_external_link(url):
                self.stats['external_links'] += 1
                # 外部链接需要手动验证
                self.results['external'].append({
                    'file': str(file_path.relative_to(self.root_dir)),
                    'line': line_num,
                    'text': text,
                    'url': url,
                    'status': 'external'
                })
            else:
                # 检查内部链接
                if self.check_internal_link(url, file_path):
                    self.stats['valid_links'] += 1
                    self.results['valid'].append({
                        'file': str(file_path.relative_to(self.root_dir)),
                        'line': line_num,
                        'text': text,
                        'url': url,
                        'status': 'valid'
                    })
                else:
                    self.stats['invalid_links'] += 1
                    self.results['invalid'].append({
                        'file': str(file_path.relative_to(self.root_dir)),
                        'line': line_num,
                        'text': text,
                        'url': url,
                        'status': 'invalid'
                    })
    
    def scan_directory(self):
        """扫描整个目录"""
        print("🔍 开始扫描Markdown文件...")
        
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
        report.append("# 链接有效性检查报告\n")
        report.append(f"**检查时间**: 2025-10-20\n")
        report.append(f"**项目**: vSphere_Docker\n\n")
        
        # 统计信息
        report.append("## 📊 统计信息\n\n")
        report.append(f"- **检查文件数**: {self.stats['total_files']}\n")
        report.append(f"- **总链接数**: {self.stats['total_links']}\n")
        report.append(f"- **有效链接**: {self.stats['valid_links']} ({self._percentage('valid_links')}%)\n")
        report.append(f"- **失效链接**: {self.stats['invalid_links']} ({self._percentage('invalid_links')}%)\n")
        report.append(f"- **外部链接**: {self.stats['external_links']} (需手动验证)\n\n")
        
        # 有效率
        internal_total = self.stats['valid_links'] + self.stats['invalid_links']
        if internal_total > 0:
            validity_rate = (self.stats['valid_links'] / internal_total) * 100
            report.append(f"**内部链接有效率**: {validity_rate:.2f}%\n\n")
        
        # 失效链接详情
        if self.results['invalid']:
            report.append("## ❌ 失效链接 (需要修复)\n\n")
            report.append("| 文件 | 行号 | 链接文本 | 链接URL |\n")
            report.append("|------|------|---------|--------|\n")
            
            for item in self.results['invalid']:
                report.append(f"| {item['file']} | {item['line']} | {item['text']} | `{item['url']}` |\n")
            report.append("\n")
        else:
            report.append("## ✅ 所有内部链接有效\n\n")
        
        # 外部链接
        if self.results['external']:
            report.append("## 🌐 外部链接 (需手动验证)\n\n")
            report.append("以下外部链接需要手动验证其有效性:\n\n")
            
            # 按文件分组
            by_file = defaultdict(list)
            for item in self.results['external']:
                by_file[item['file']].append(item)
            
            for file, links in sorted(by_file.items()):
                report.append(f"### {file}\n\n")
                for item in links:
                    report.append(f"- 行 {item['line']}: [{item['text']}]({item['url']})\n")
                report.append("\n")
        
        # 建议
        report.append("## 💡 建议\n\n")
        
        if self.stats['invalid_links'] > 0:
            report.append("### 修复失效链接\n\n")
            report.append("1. 检查文件是否存在\n")
            report.append("2. 确认路径是否正确\n")
            report.append("3. 更新链接到正确路径\n\n")
        
        if self.stats['external_links'] > 0:
            report.append("### 验证外部链接\n\n")
            report.append("1. 使用浏览器或curl验证链接可访问\n")
            report.append("2. 检查链接是否返回404\n")
            report.append("3. 更新过期的链接\n\n")
        
        report.append("---\n\n")
        report.append(f"**报告生成**: Python LinkChecker v1.0\n")
        report.append(f"**文档总数**: {self.stats['total_files']}\n")
        report.append(f"**链接总数**: {self.stats['total_links']}\n")
        
        return ''.join(report)
    
    def _percentage(self, key: str) -> str:
        """计算百分比"""
        if self.stats['total_links'] == 0:
            return "0.00"
        return f"{(self.stats[key] / self.stats['total_links']) * 100:.2f}"


def main():
    """主函数"""
    # 获取项目根目录
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    
    print("=" * 60)
    print("链接有效性检查工具")
    print("=" * 60)
    print()
    
    # 创建检查器
    checker = LinkChecker(str(root_dir))
    
    # 扫描目录
    checker.scan_directory()
    
    print()
    print("=" * 60)
    print("扫描完成!")
    print("=" * 60)
    print()
    print(f"📁 检查文件: {checker.stats['total_files']}")
    print(f"🔗 总链接数: {checker.stats['total_links']}")
    print(f"✅ 有效链接: {checker.stats['valid_links']}")
    print(f"❌ 失效链接: {checker.stats['invalid_links']}")
    print(f"🌐 外部链接: {checker.stats['external_links']}")
    print()
    
    # 生成报告
    report_path = root_dir / "2025年10月20日_链接有效性检查报告.md"
    report = checker.generate_report()
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 报告已生成: {report_path}")
    print()
    
    # 返回状态
    if checker.stats['invalid_links'] > 0:
        print("⚠️  发现失效链接，请查看报告进行修复")
        return 1
    else:
        print("✅ 所有内部链接有效!")
        return 0


if __name__ == '__main__':
    sys.exit(main())

