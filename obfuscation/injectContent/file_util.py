#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件操作工具类
"""

from pathlib import Path
from typing import List
from log_util import LogUtil


class FileUtil:
    """文件操作工具类"""
    
    @staticmethod
    def read_files_recursively(directory: str, extension: str = ".m") -> List[str]:
        """
        递归读取目录下的所有指定扩展名的文件
        
        Args:
            directory: 目录路径
            extension: 文件扩展名，默认为.m
            
        Returns:
            文件路径列表
        """
        LogUtil.print_tip(f"递归遍历目录: {directory}")
        
        dir_path = Path(directory)
        if not dir_path.is_dir():
            LogUtil.print_error(f"错误: 不是一个目录 {directory}")
            return []
        
        file_list = []
        for item_path in dir_path.rglob(f"*{extension}"):
            if item_path.is_file():
                file_list.append(str(item_path))
        
        LogUtil.print_info(f"找到 {len(file_list)} 个{extension}文件")
        return file_list
    
    @staticmethod
    def check_file_exists(file_path: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件是否存在
        """
        return Path(file_path).is_file()
    
    @staticmethod
    def check_dir_exists(dir_path: str) -> bool:
        """
        检查目录是否存在
        
        Args:
            dir_path: 目录路径
            
        Returns:
            目录是否存在
        """
        return Path(dir_path).is_dir()
    
    @staticmethod
    def create_file_if_not_exists(file_path: str):
        """
        如果文件不存在则创建
        
        Args:
            file_path: 文件路径
        """
        path = Path(file_path)
        if path.is_file():
            LogUtil.print_info(f"检测到文件存在: {file_path}")
        else:
            LogUtil.print_info(f"创建文件: {file_path}")
            path.touch()
    
    @staticmethod
    def read_file_content(file_path: str, encoding: str = 'utf-8') -> str:
        """
        读取文件内容
        
        Args:
            file_path: 文件路径
            encoding: 编码格式，默认utf-8
            
        Returns:
            文件内容
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            LogUtil.print_error(f"读取文件失败 {file_path}: {str(e)}")
            return ""
    
    @staticmethod
    def write_file_content(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """
        写入文件内容
        
        Args:
            file_path: 文件路径
            content: 文件内容
            encoding: 编码格式，默认utf-8
            
        Returns:
            是否写入成功
        """
        try:
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except Exception as e:
            LogUtil.print_error(f"写入文件失败 {file_path}: {str(e)}")
            return False
    
    @staticmethod
    def read_file_lines(file_path: str, encoding: str = 'utf-8') -> List[str]:
        """
        读取文件行
        
        Args:
            file_path: 文件路径
            encoding: 编码格式，默认utf-8
            
        Returns:
            文件行列表
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.readlines()
        except Exception as e:
            LogUtil.print_error(f"读取文件失败 {file_path}: {str(e)}")
            return []
    
    @staticmethod
    def write_file_lines(file_path: str, lines: List[str], encoding: str = 'utf-8') -> bool:
        """
        写入文件行
        
        Args:
            file_path: 文件路径
            lines: 文件行列表
            encoding: 编码格式，默认utf-8
            
        Returns:
            是否写入成功
        """
        try:
            with open(file_path, 'w', encoding=encoding) as f:
                f.writelines(lines)
            return True
        except Exception as e:
            LogUtil.print_error(f"写入文件失败 {file_path}: {str(e)}")
            return False
