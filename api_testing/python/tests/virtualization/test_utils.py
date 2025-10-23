#!/usr/bin/env python3
"""
虚拟化测试工具函数库
提供通用的测试辅助功能
"""

import time
import yaml
import os
from typing import Dict, Any, Optional, Callable
from functools import wraps
import logging

# ========================================
# 配置加载
# ========================================

def load_test_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    加载测试配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    # 尝试从多个位置加载配置
    config_locations = [
        config_path,
        os.path.join(os.path.dirname(__file__), config_path),
        os.path.join(os.path.dirname(__file__), "config.yaml.example"),
    ]
    
    for location in config_locations:
        if os.path.exists(location):
            with open(location, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logging.info(f"Loaded config from: {location}")
                return config
    
    # 如果没有找到配置文件，返回默认配置
    logging.warning("No config file found, using defaults")
    return get_default_config()


def get_default_config() -> Dict[str, Any]:
    """获取默认配置"""
    return {
        'vsphere': {
            'host': os.getenv('VSPHERE_HOST', 'vcenter.example.com'),
            'port': int(os.getenv('VSPHERE_PORT', '443')),
            'admin': {
                'username': os.getenv('VSPHERE_USER', 'administrator@vsphere.local'),
                'password': os.getenv('VSPHERE_PASSWORD', 'password'),
            },
            'ssl': {
                'verify_cert': os.getenv('VSPHERE_VERIFY_SSL', 'false').lower() == 'true',
            },
            'timeouts': {
                'connection': 30,
                'power_on': 300,
                'power_off': 120,
            }
        },
        'libvirt': {
            'uri': os.getenv('LIBVIRT_URI', 'qemu:///system'),
            'timeouts': {
                'connection': 30,
                'domain_start': 120,
            }
        },
        'test_execution': {
            'cleanup': {
                'auto_cleanup': True,
            }
        },
        'logging': {
            'level': 'INFO',
        }
    }


# ========================================
# 重试机制
# ========================================

def retry_on_exception(max_attempts: int = 3, delay: int = 5, 
                      exceptions: tuple = (Exception,)):
    """
    装饰器：在异常时重试函数
    
    Args:
        max_attempts: 最大尝试次数
        delay: 重试间隔（秒）
        exceptions: 需要重试的异常类型
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logging.warning(
                            f"Attempt {attempt}/{max_attempts} failed: {e}. "
                            f"Retrying in {delay} seconds..."
                        )
                        time.sleep(delay)
                    else:
                        logging.error(
                            f"All {max_attempts} attempts failed. Last error: {e}"
                        )
            raise last_exception
        return wrapper
    return decorator


# ========================================
# 等待机制
# ========================================

def wait_for_condition(condition: Callable[[], bool], 
                       timeout: int = 60,
                       interval: int = 5,
                       error_message: str = "Condition not met") -> bool:
    """
    等待条件满足
    
    Args:
        condition: 返回布尔值的条件函数
        timeout: 超时时间（秒）
        interval: 检查间隔（秒）
        error_message: 超时错误消息
        
    Returns:
        是否在超时前满足条件
        
    Raises:
        TimeoutError: 如果超时
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            if condition():
                return True
        except Exception as e:
            logging.debug(f"Condition check raised exception: {e}")
        time.sleep(interval)
    
    raise TimeoutError(f"{error_message} (timeout: {timeout}s)")


def wait_for_state(get_state: Callable[[], str],
                  expected_state: str,
                  timeout: int = 60,
                  interval: int = 5) -> bool:
    """
    等待状态达到预期值
    
    Args:
        get_state: 获取当前状态的函数
        expected_state: 期望的状态
        timeout: 超时时间（秒）
        interval: 检查间隔（秒）
        
    Returns:
        是否成功达到预期状态
    """
    def condition():
        current_state = get_state()
        logging.debug(f"Current state: {current_state}, expected: {expected_state}")
        return current_state == expected_state
    
    return wait_for_condition(
        condition,
        timeout=timeout,
        interval=interval,
        error_message=f"State did not reach '{expected_state}'"
    )


# ========================================
# 资源清理
# ========================================

class ResourceTracker:
    """资源跟踪器，用于自动清理测试资源"""
    
    def __init__(self):
        self.resources = []
    
    def track(self, resource: Any, cleanup_func: Callable[[Any], None]):
        """
        跟踪一个资源
        
        Args:
            resource: 资源对象
            cleanup_func: 清理函数
        """
        self.resources.append((resource, cleanup_func))
    
    def cleanup_all(self, ignore_errors: bool = True):
        """
        清理所有跟踪的资源
        
        Args:
            ignore_errors: 是否忽略清理错误
        """
        errors = []
        for resource, cleanup_func in reversed(self.resources):
            try:
                logging.info(f"Cleaning up resource: {resource}")
                cleanup_func(resource)
            except Exception as e:
                error_msg = f"Failed to cleanup {resource}: {e}"
                logging.error(error_msg)
                if not ignore_errors:
                    errors.append(error_msg)
        
        self.resources.clear()
        
        if errors:
            raise Exception(f"Cleanup failed with {len(errors)} errors: {errors}")


# ========================================
# 时间测量
# ========================================

class Timer:
    """测量代码执行时间"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = time.time()
        logging.info(f"{self.name} started")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        logging.info(f"{self.name} completed in {self.duration:.2f}s")
        return False
    
    def elapsed(self) -> float:
        """获取已经过的时间"""
        if self.start_time is None:
            return 0.0
        current_time = time.time()
        return current_time - self.start_time


# ========================================
# 日志辅助
# ========================================

def setup_test_logging(level: str = "INFO", 
                       log_file: Optional[str] = None) -> logging.Logger:
    """
    设置测试日志
    
    Args:
        level: 日志级别
        log_file: 日志文件路径（可选）
        
    Returns:
        配置好的logger
    """
    # 创建logger
    logger = logging.getLogger("virtualization_tests")
    logger.setLevel(getattr(logging, level.upper()))
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定）
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


# ========================================
# 测试数据生成
# ========================================

def generate_test_name(prefix: str = "test") -> str:
    """
    生成唯一的测试名称
    
    Args:
        prefix: 名称前缀
        
    Returns:
        唯一名称
    """
    timestamp = int(time.time())
    return f"{prefix}-{timestamp}"


def generate_test_config(base_config: Dict[str, Any], 
                        overrides: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成测试配置（合并基础配置和覆盖配置）
    
    Args:
        base_config: 基础配置
        overrides: 覆盖配置
        
    Returns:
        合并后的配置
    """
    result = base_config.copy()
    
    def deep_update(d: dict, u: dict) -> dict:
        """递归更新字典"""
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = deep_update(d.get(k, {}), v)
            else:
                d[k] = v
        return d
    
    return deep_update(result, overrides)


# ========================================
# 断言辅助
# ========================================

def assert_eventually(condition: Callable[[], bool],
                     timeout: int = 30,
                     interval: int = 5,
                     message: str = "Condition not met"):
    """
    断言条件最终会满足
    
    Args:
        condition: 条件函数
        timeout: 超时时间
        interval: 检查间隔
        message: 失败消息
    """
    try:
        wait_for_condition(condition, timeout, interval, message)
    except TimeoutError as e:
        raise AssertionError(str(e))


def assert_state_transition(get_state: Callable[[], str],
                           from_state: str,
                           to_state: str,
                           timeout: int = 60):
    """
    断言状态转换
    
    Args:
        get_state: 获取状态函数
        from_state: 初始状态
        to_state: 目标状态
        timeout: 超时时间
    """
    current_state = get_state()
    assert current_state == from_state, \
        f"Expected initial state '{from_state}', got '{current_state}'"
    
    wait_for_state(get_state, to_state, timeout)


# ========================================
# 性能测试辅助
# ========================================

class PerformanceMetrics:
    """性能指标收集器"""
    
    def __init__(self):
        self.metrics = {}
    
    def record(self, name: str, value: float, unit: str = ""):
        """记录一个指标"""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append({
            'value': value,
            'unit': unit,
            'timestamp': time.time()
        })
    
    def get_stats(self, name: str) -> Dict[str, float]:
        """获取指标统计信息"""
        if name not in self.metrics or not self.metrics[name]:
            return {}
        
        values = [m['value'] for m in self.metrics[name]]
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'total': sum(values)
        }
    
    def report(self) -> str:
        """生成性能报告"""
        report = ["Performance Metrics Report", "=" * 50]
        
        for name in sorted(self.metrics.keys()):
            stats = self.get_stats(name)
            unit = self.metrics[name][0].get('unit', '')
            report.append(f"\n{name}:")
            report.append(f"  Count: {stats['count']}")
            report.append(f"  Min: {stats['min']:.2f}{unit}")
            report.append(f"  Max: {stats['max']:.2f}{unit}")
            report.append(f"  Avg: {stats['avg']:.2f}{unit}")
            if name.lower().find('time') >= 0 or name.lower().find('duration') >= 0:
                report.append(f"  Total: {stats['total']:.2f}{unit}")
        
        return "\n".join(report)


# ========================================
# 测试报告生成
# ========================================

def generate_test_summary(test_results: Dict[str, Any]) -> str:
    """
    生成测试摘要
    
    Args:
        test_results: 测试结果字典
        
    Returns:
        摘要字符串
    """
    total = test_results.get('total', 0)
    passed = test_results.get('passed', 0)
    failed = test_results.get('failed', 0)
    skipped = test_results.get('skipped', 0)
    duration = test_results.get('duration', 0)
    
    summary = [
        "Test Summary",
        "=" * 50,
        f"Total Tests: {total}",
        f"Passed: {passed} ({passed/total*100:.1f}%)" if total > 0 else "Passed: 0",
        f"Failed: {failed} ({failed/total*100:.1f}%)" if total > 0 else "Failed: 0",
        f"Skipped: {skipped} ({skipped/total*100:.1f}%)" if total > 0 else "Skipped: 0",
        f"Duration: {duration:.2f}s",
        "=" * 50,
    ]
    
    return "\n".join(summary)


# ========================================
# 上下文管理器
# ========================================

class test_context:
    """测试上下文管理器"""
    
    def __init__(self, name: str, cleanup_func: Optional[Callable] = None):
        self.name = name
        self.cleanup_func = cleanup_func
        self.timer = Timer(name)
        self.tracker = ResourceTracker()
    
    def __enter__(self):
        self.timer.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.cleanup_func:
                self.cleanup_func()
            self.tracker.cleanup_all()
        finally:
            self.timer.__exit__(exc_type, exc_val, exc_tb)
        return False
    
    def track_resource(self, resource: Any, cleanup_func: Callable[[Any], None]):
        """跟踪需要清理的资源"""
        self.tracker.track(resource, cleanup_func)


# ========================================
# 示例使用
# ========================================

if __name__ == "__main__":
    # 配置日志
    logger = setup_test_logging(level="DEBUG", log_file="logs/test.log")
    
    # 加载配置
    config = load_test_config()
    logger.info(f"Loaded config: {config}")
    
    # 使用重试装饰器
    @retry_on_exception(max_attempts=3, delay=2)
    def unstable_operation():
        import random
        if random.random() < 0.7:
            raise Exception("Random failure")
        return "Success"
    
    # 使用计时器
    with Timer("Test Operation") as timer:
        time.sleep(2)
        logger.info(f"Elapsed: {timer.elapsed():.2f}s")
    
    # 使用性能指标
    metrics = PerformanceMetrics()
    for i in range(10):
        with Timer("Operation") as t:
            time.sleep(0.1)
        metrics.record("operation_time", t.duration, "s")
    
    print(metrics.report())
    
    # 生成测试摘要
    results = {
        'total': 100,
        'passed': 85,
        'failed': 10,
        'skipped': 5,
        'duration': 120.5
    }
    print(generate_test_summary(results))

