#!/usr/bin/env python3
"""
运行所有API测试的主脚本
"""

import sys
import os
import argparse
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import setup_colored_logger
from utils.report import TestReport

def run_docker_tests(logger):
    """运行Docker API测试"""
    logger.info("开始运行Docker API测试...")
    
    try:
        from docker_api_test import DockerAPITest
        
        tester = DockerAPITest()
        tester.run_all_tests(create_test_container=False)
        
        logger.info("✅ Docker API测试完成")
        return True
    except Exception as e:
        logger.error(f"❌ Docker API测试失败: {e}")
        return False

def run_kubernetes_tests(logger):
    """运行Kubernetes API测试"""
    logger.info("开始运行Kubernetes API测试...")
    
    try:
        from kubernetes_api_test import KubernetesAPITest
        
        tester = KubernetesAPITest(
            api_server="http://localhost:8001",
            token=None
        )
        tester.run_all_tests()
        
        logger.info("✅ Kubernetes API测试完成")
        return True
    except Exception as e:
        logger.error(f"❌ Kubernetes API测试失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='运行API测试套件')
    parser.add_argument('--tests', nargs='+', 
                       choices=['docker', 'kubernetes', 'vsphere', 'all'],
                       default=['all'],
                       help='指定要运行的测试')
    parser.add_argument('--report-dir', default='reports',
                       help='报告输出目录')
    parser.add_argument('--report-format', nargs='+',
                       choices=['html', 'json', 'markdown'],
                       default=['html'],
                       help='报告格式')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='日志级别')
    
    args = parser.parse_args()
    
    # 设置日志
    log_file = os.path.join(args.report_dir, 'api_test.log')
    logger = setup_colored_logger(
        name='api_test_runner',
        log_file=log_file,
        level=args.log_level
    )
    
    # 创建测试报告
    report = TestReport("API测试套件")
    
    logger.info("=" * 70)
    logger.info("API测试套件 - 开始执行")
    logger.info("=" * 70)
    logger.info(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"测试项目: {', '.join(args.tests)}")
    logger.info(f"报告目录: {args.report_dir}")
    logger.info("=" * 70)
    
    # 运行测试
    tests_to_run = args.tests
    if 'all' in tests_to_run:
        tests_to_run = ['docker', 'kubernetes']
    
    for test_name in tests_to_run:
        logger.info(f"\n{'=' * 70}")
        logger.info(f"执行测试: {test_name.upper()}")
        logger.info('=' * 70)
        
        start_time = datetime.now()
        
        if test_name == 'docker':
            success = run_docker_tests(logger)
        elif test_name == 'kubernetes':
            success = run_kubernetes_tests(logger)
        else:
            logger.warning(f"未知的测试: {test_name}")
            continue
        
        duration = (datetime.now() - start_time).total_seconds()
        
        # 添加到报告
        report.add_test_result(
            test_case=f"{test_name}_api_test",
            status='passed' if success else 'failed',
            duration=duration,
            message=f"{test_name.upper()} API测试{'成功' if success else '失败'}"
        )
    
    report.finish()
    
    # 生成报告
    logger.info("\n" + "=" * 70)
    logger.info("生成测试报告")
    logger.info("=" * 70)
    
    os.makedirs(args.report_dir, exist_ok=True)
    
    for fmt in args.report_format:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if fmt == 'html':
            report_file = os.path.join(args.report_dir, f'api_test_report_{timestamp}.html')
            report.to_html(report_file)
            logger.info(f"✅ HTML报告已生成: {report_file}")
        
        elif fmt == 'json':
            report_file = os.path.join(args.report_dir, f'api_test_report_{timestamp}.json')
            report.to_json(report_file)
            logger.info(f"✅ JSON报告已生成: {report_file}")
        
        elif fmt == 'markdown':
            report_file = os.path.join(args.report_dir, f'api_test_report_{timestamp}.md')
            report.to_markdown(report_file)
            logger.info(f"✅ Markdown报告已生成: {report_file}")
    
    # 打印摘要
    logger.info("\n" + "=" * 70)
    logger.info("测试摘要")
    logger.info("=" * 70)
    logger.info(f"总测试数: {report.summary['total']}")
    logger.info(f"通过: {report.summary['passed']} ✅")
    logger.info(f"失败: {report.summary['failed']} ❌")
    logger.info(f"跳过: {report.summary['skipped']} ⏭️")
    logger.info(f"错误: {report.summary['errors']} ⚠️")
    logger.info(f"总耗时: {report.get_duration():.2f} 秒")
    logger.info("=" * 70)
    
    # 返回退出码
    sys.exit(0 if report.summary['failed'] == 0 and report.summary['errors'] == 0 else 1)

if __name__ == "__main__":
    main()

