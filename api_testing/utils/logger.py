#!/usr/bin/env python3
"""
日志工具模块
提供统一的日志记录功能
"""

import logging
import os
from typing import Optional
from logging.handlers import RotatingFileHandler
import sys


def setup_logger(name: str = 'api_test',
                 log_file: Optional[str] = None,
                 level: str = 'INFO',
                 console: bool = True,
                 rotate: bool = True,
                 max_bytes: int = 10485760,  # 10MB
                 backup_count: int = 5) -> logging.Logger:
    """
    配置日志记录器
    
    Args:
        name: 日志记录器名称
        log_file: 日志文件路径
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console: 是否输出到控制台
        rotate: 是否启用日志轮转
        max_bytes: 日志文件最大字节数
        backup_count: 保留的备份文件数
    
    Returns:
        logger: 配置好的日志记录器
    """
    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 文件handler
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        if rotate:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
        else:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
        
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = 'api_test') -> logging.Logger:
    """
    获取已配置的日志记录器
    
    Args:
        name: 日志记录器名称
    
    Returns:
        logger: 日志记录器
    """
    return logging.getLogger(name)


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器 (用于终端)"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',     # 青色
        'INFO': '\033[32m',      # 绿色
        'WARNING': '\033[33m',   # 黄色
        'ERROR': '\033[31m',     # 红色
        'CRITICAL': '\033[35m',  # 品红色
        'RESET': '\033[0m'       # 重置
    }
    
    def format(self, record):
        # 添加颜色
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_colored_logger(name: str = 'api_test',
                         log_file: Optional[str] = None,
                         level: str = 'INFO') -> logging.Logger:
    """
    配置彩色日志记录器
    
    Args:
        name: 日志记录器名称
        log_file: 日志文件路径
        level: 日志级别
    
    Returns:
        logger: 配置好的彩色日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 彩色控制台handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    colored_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(colored_formatter)
    logger.addHandler(console_handler)
    
    # 文件handler (不使用颜色)
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10485760,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


# 测试函数
if __name__ == "__main__":
    # 测试基础logger
    logger = setup_logger(
        name='test_logger',
        log_file='reports/test.log',
        level='DEBUG'
    )
    
    logger.debug("这是DEBUG消息")
    logger.info("这是INFO消息")
    logger.warning("这是WARNING消息")
    logger.error("这是ERROR消息")
    logger.critical("这是CRITICAL消息")
    
    # 测试彩色logger
    colored_logger = setup_colored_logger(
        name='colored_test',
        log_file='reports/colored_test.log',
        level='DEBUG'
    )
    
    colored_logger.debug("彩色DEBUG消息")
    colored_logger.info("彩色INFO消息")
    colored_logger.warning("彩色WARNING消息")
    colored_logger.error("彩色ERROR消息")
    colored_logger.critical("彩色CRITICAL消息")

