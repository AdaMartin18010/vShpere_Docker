#!/usr/bin/env python3
"""
报告生成工具模块
提供测试报告生成功能
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from jinja2 import Template

class TestReport:
    """测试报告类"""
    
    def __init__(self, test_name: str = "API Test"):
        self.test_name = test_name
        self.start_time = datetime.now()
        self.end_time = None
        self.test_results = []
        self.summary = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0
        }
    
    def add_test_result(self, test_case: str, status: str, 
                       duration: float = 0, message: str = "", 
                       details: Optional[Dict] = None):
        """
        添加测试结果
        
        Args:
            test_case: 测试用例名称
            status: 测试状态 (passed/failed/skipped/error)
            duration: 执行时长(秒)
            message: 消息
            details: 详细信息
        """
        result = {
            'test_case': test_case,
            'status': status,
            'duration': duration,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.test_results.append(result)
        self.summary['total'] += 1
        
        if status == 'passed':
            self.summary['passed'] += 1
        elif status == 'failed':
            self.summary['failed'] += 1
        elif status == 'skipped':
            self.summary['skipped'] += 1
        elif status == 'error':
            self.summary['errors'] += 1
    
    def finish(self):
        """完成测试,记录结束时间"""
        self.end_time = datetime.now()
    
    def get_duration(self) -> float:
        """获取总执行时长(秒)"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'test_name': self.test_name,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.get_duration(),
            'summary': self.summary,
            'test_results': self.test_results
        }
    
    def to_json(self, file_path: Optional[str] = None) -> str:
        """
        导出为JSON格式
        
        Args:
            file_path: 文件路径(可选)
        
        Returns:
            json_str: JSON字符串
        """
        json_str = json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
        
        if file_path:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
        
        return json_str
    
    def to_html(self, file_path: Optional[str] = None) -> str:
        """
        导出为HTML格式
        
        Args:
            file_path: 文件路径(可选)
        
        Returns:
            html_str: HTML字符串
        """
        template = HTML_TEMPLATE
        
        html = Template(template).render(
            test_name=self.test_name,
            start_time=self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            end_time=self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else 'N/A',
            duration=f"{self.get_duration():.2f}",
            summary=self.summary,
            pass_rate=f"{(self.summary['passed'] / self.summary['total'] * 100) if self.summary['total'] > 0 else 0:.1f}",
            test_results=self.test_results
        )
        
        if file_path:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html)
        
        return html
    
    def to_markdown(self, file_path: Optional[str] = None) -> str:
        """
        导出为Markdown格式
        
        Args:
            file_path: 文件路径(可选)
        
        Returns:
            md_str: Markdown字符串
        """
        lines = [
            f"# {self.test_name} - 测试报告",
            "",
            "## 执行摘要",
            "",
            f"- **开始时间**: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **结束时间**: {self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else 'N/A'}",
            f"- **执行时长**: {self.get_duration():.2f} 秒",
            "",
            "## 测试统计",
            "",
            f"- **总数**: {self.summary['total']}",
            f"- **通过**: {self.summary['passed']} ✅",
            f"- **失败**: {self.summary['failed']} ❌",
            f"- **跳过**: {self.summary['skipped']} ⏭️",
            f"- **错误**: {self.summary['errors']} ⚠️",
            f"- **通过率**: {(self.summary['passed'] / self.summary['total'] * 100) if self.summary['total'] > 0 else 0:.1f}%",
            "",
            "## 测试结果详情",
            "",
            "| 测试用例 | 状态 | 时长(秒) | 消息 |",
            "|---------|------|---------|------|"
        ]
        
        for result in self.test_results:
            status_icon = {
                'passed': '✅',
                'failed': '❌',
                'skipped': '⏭️',
                'error': '⚠️'
            }.get(result['status'], '❓')
            
            lines.append(
                f"| {result['test_case']} | {status_icon} {result['status']} | "
                f"{result['duration']:.2f} | {result['message']} |"
            )
        
        md_str = '\n'.join(lines)
        
        if file_path:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(md_str)
        
        return md_str


# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ test_name }} - 测试报告</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
        }
        .header h1 { margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }
        .summary-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .summary-card h3 {
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
        }
        .summary-card .value {
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }
        .summary-card.passed .value { color: #28a745; }
        .summary-card.failed .value { color: #dc3545; }
        .summary-card.skipped .value { color: #ffc107; }
        .summary-card.errors .value { color: #fd7e14; }
        .results {
            padding: 30px;
        }
        .results h2 {
            margin-bottom: 20px;
            color: #333;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }
        .status.passed {
            background: #d4edda;
            color: #155724;
        }
        .status.failed {
            background: #f8d7da;
            color: #721c24;
        }
        .status.skipped {
            background: #fff3cd;
            color: #856404;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
        }
        .footer {
            padding: 20px 30px;
            background: #f8f9fa;
            color: #666;
            text-align: center;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ test_name }}</h1>
            <p>测试报告 - 生成时间: {{ end_time }}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>总测试数</h3>
                <div class="value">{{ summary.total }}</div>
            </div>
            <div class="summary-card passed">
                <h3>通过 ✅</h3>
                <div class="value">{{ summary.passed }}</div>
            </div>
            <div class="summary-card failed">
                <h3>失败 ❌</h3>
                <div class="value">{{ summary.failed }}</div>
            </div>
            <div class="summary-card skipped">
                <h3>跳过 ⏭️</h3>
                <div class="value">{{ summary.skipped }}</div>
            </div>
            <div class="summary-card errors">
                <h3>错误 ⚠️</h3>
                <div class="value">{{ summary.errors }}</div>
            </div>
            <div class="summary-card">
                <h3>通过率</h3>
                <div class="value">{{ pass_rate }}%</div>
            </div>
            <div class="summary-card">
                <h3>执行时长</h3>
                <div class="value">{{ duration }}s</div>
            </div>
        </div>
        
        <div class="results">
            <h2>测试结果详情</h2>
            <table>
                <thead>
                    <tr>
                        <th>测试用例</th>
                        <th>状态</th>
                        <th>时长(秒)</th>
                        <th>消息</th>
                        <th>时间戳</th>
                    </tr>
                </thead>
                <tbody>
                    {% for result in test_results %}
                    <tr>
                        <td>{{ result.test_case }}</td>
                        <td><span class="status {{ result.status }}">{{ result.status }}</span></td>
                        <td>{{ "%.2f"|format(result.duration) }}</td>
                        <td>{{ result.message }}</td>
                        <td>{{ result.timestamp }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>API测试报告 © 2025 | 开始时间: {{ start_time }} | 结束时间: {{ end_time }}</p>
        </div>
    </div>
</body>
</html>
"""


def generate_report(test_results: List[Dict], 
                   output_file: str,
                   format: str = 'html',
                   test_name: str = 'API Test') -> str:
    """
    生成测试报告
    
    Args:
        test_results: 测试结果列表
        output_file: 输出文件路径
        format: 报告格式 (html/json/markdown)
        test_name: 测试名称
    
    Returns:
        report_content: 报告内容
    """
    report = TestReport(test_name)
    
    for result in test_results:
        report.add_test_result(
            test_case=result.get('test_case', 'Unknown'),
            status=result.get('status', 'unknown'),
            duration=result.get('duration', 0),
            message=result.get('message', ''),
            details=result.get('details')
        )
    
    report.finish()
    
    if format == 'html':
        return report.to_html(output_file)
    elif format == 'json':
        return report.to_json(output_file)
    elif format == 'markdown' or format == 'md':
        return report.to_markdown(output_file)
    else:
        raise ValueError(f"不支持的格式: {format}")


# 测试函数
if __name__ == "__main__":
    # 创建测试报告
    report = TestReport("Docker API 测试")
    
    # 添加测试结果
    report.add_test_result("test_ping", "passed", 0.123, "连接成功")
    report.add_test_result("test_version", "passed", 0.234, "版本获取成功")
    report.add_test_result("test_list_containers", "passed", 0.456, "容器列表获取成功")
    report.add_test_result("test_create_container", "failed", 1.234, "镜像不存在")
    report.add_test_result("test_performance", "skipped", 0, "跳过性能测试")
    
    report.finish()
    
    # 生成报告
    print("生成HTML报告...")
    report.to_html("reports/test_report.html")
    print("✅ HTML报告已生成: reports/test_report.html")
    
    print("\n生成JSON报告...")
    report.to_json("reports/test_report.json")
    print("✅ JSON报告已生成: reports/test_report.json")
    
    print("\n生成Markdown报告...")
    report.to_markdown("reports/test_report.md")
    print("✅ Markdown报告已生成: reports/test_report.md")

