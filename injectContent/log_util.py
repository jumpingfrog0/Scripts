#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志打印工具类
"""

from datetime import datetime


class Colors:
    """ANSI颜色代码"""
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RESET = '\033[0m'


class LogUtil:
    """日志工具类"""
    
    @staticmethod
    def print_tip(message: str):
        """打印提示信息（黄色）"""
        print(f"{Colors.YELLOW}{message}{Colors.RESET}")
    
    @staticmethod
    def print_info(message: str):
        """打印普通信息（绿色）"""
        print(f"{Colors.GREEN}{message}{Colors.RESET}")
    
    @staticmethod
    def print_error(message: str):
        """打印错误信息（红色）"""
        print(f"{Colors.RED}{message}{Colors.RESET}")
    
    @staticmethod
    def print_warning(message: str):
        """打印警告信息（绿色）"""
        timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S%z')
        print(f"[{timestamp}]: {Colors.GREEN}{message}{Colors.RESET}")
    
    @staticmethod
    def print_highlight(message: str):
        """打印高亮信息（红色）"""
        print(f"{Colors.RED}{message}{Colors.RESET}")
