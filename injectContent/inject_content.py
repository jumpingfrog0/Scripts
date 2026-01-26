#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在Objective-C方法第一行注入垃圾代码
"""

import os
import sys
import re
import random
from pathlib import Path
from typing import List

from log_util import LogUtil
from file_util import FileUtil
from menu_util import MenuUtil


######请修改以下配置#######

# 注入内容的前缀（用于删除操作）
CFG_RM_CONTENT_PREFIX = "FY_ZEUS_ZONE_MAIN_"

######请修改以上配置#######


class ContentInjector:
    """内容注入器"""
    
    def __init__(self):
        """需要处理的文件目录"""
        self.dir_array = [
            "BaseService",
            "Modules",
            "Components",
            "pyrooApp",
            "UIKits"
        ]
        
        """注入的内容"""
        self.inject_content_array = [
            "    FY_ZEUS_ZONE_MAIN_A",
            "    FY_ZEUS_ZONE_MAIN_B",
            "    FY_ZEUS_ZONE_MAIN_C",
            "    FY_ZEUS_ZONE_MAIN_D",
            "    FY_ZEUS_ZONE_MAIN_E",
            "    FY_ZEUS_ZONE_MAIN_F",
            "    FY_ZEUS_ZONE_MAIN_G"
        ]

        self.target_file_array = []
        self.root_dir = ""
    
    def read_target_file_recursively(self, directory: str):
        """递归读取目录下的所有.m文件"""
        self.target_file_array = FileUtil.read_files_recursively(directory, ".m")
    
    def process_to_inject_content(self):
        """处理目标文件，添加随机注入内容"""
        for file_path in self.target_file_array:
            self._inject_content_to_methods(file_path)
    
    def process_to_remove_content(self):
        """处理目标文件，删除注入的内容"""
        for file_path in self.target_file_array:
            self._remove_content_by_prefix(file_path)
    
    def _inject_content_to_methods(self, file_path: str) -> bool:
        """
        在Objective-C方法第一行随机注入内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否成功注入
        """
        LogUtil.print_tip(f"正在处理目标文件: {file_path}")
        
        try:
            content = FileUtil.read_file_content(file_path)
            if not content:
                return False
            
            lines = content.split('\n')
            new_lines = []
            i = 0
            
            while i < len(lines):
                line = lines[i]
                
                # 检查是否是方法定义的开始
                if re.match(r'^-\s*\(', line.strip()):
                    # 收集完整的方法定义（可能跨多行）
                    new_lines.append(line)
                    i += 1
                    
                    # 继续查找左花括号
                    while i < len(lines):
                        current_line = lines[i]
                        new_lines.append(current_line)
                        
                        # 找到左花括号
                        if re.search(r'\{\s*$', current_line):
                            # 随机选择一个注入内容
                            injected_content = random.choice(self.inject_content_array)
                            LogUtil.print_info(f">>>>>>> {injected_content}")
                            new_lines.append(injected_content)
                            i += 1
                            break
                        i += 1
                else:
                    new_lines.append(line)
                    i += 1
            
            # 写回文件
            new_content = '\n'.join(new_lines)
            if new_content != content:
                if FileUtil.write_file_content(file_path, new_content):
                    LogUtil.print_info(f"文件处理完成: {file_path}")
                    return True
            
            return False
            
        except Exception as e:
            LogUtil.print_error(f"处理文件出错 {file_path}: {str(e)}")
            return False
    
    def _remove_content_by_prefix(self, file_path: str) -> bool:
        """
        删除包含指定前缀的行
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否成功删除
        """
        LogUtil.print_tip(f"正在处理目标文件: {file_path}")
        
        try:
            lines = FileUtil.read_file_lines(file_path)
            if not lines:
                return False
            
            # 过滤掉包含前缀的行
            new_lines = [line for line in lines if CFG_RM_CONTENT_PREFIX not in line]
            
            if len(new_lines) != len(lines):
                return FileUtil.write_file_lines(file_path, new_lines)
            
            return False
            
        except Exception as e:
            LogUtil.print_error(f"处理文件出错 {file_path}: {str(e)}")
            return False
    
    def patch_inject_content(self):
        """批量注入内容"""
        print(self.dir_array)
        
        for target_dir_name in self.dir_array:
            target_dir = os.path.join(self.root_dir, target_dir_name)
            print(target_dir)
            
            self.target_file_array = []
            self.read_target_file_recursively(target_dir)
            
            # 添加注入内容
            self.process_to_inject_content()
        
        LogUtil.print_tip("内容添加完成")
    
    def patch_remove_content(self):
        """批量删除内容"""
        print(self.dir_array)
        
        for target_dir_name in self.dir_array:
            target_dir = os.path.join(self.root_dir, target_dir_name)
            print(target_dir)
            
            self.target_file_array = []
            self.read_target_file_recursively(target_dir)
            
            # 删除注入内容
            self.process_to_remove_content()
        
        LogUtil.print_tip("内容删除完成")
    
    def load_inject_config(self):        
        # 需要处理的文件目录
        LogUtil.print_tip("需要处理的文件目录")
        for dir_name in self.dir_array:
            LogUtil.print_info(f"文件目录: {dir_name}")
    
    def add_injected_content(self):
        """添加注入内容"""
        print()
        
        # 获取根目录（当前目录的上两级）
        current_dir = Path.cwd()
        self.root_dir = str(current_dir.parent.parent)
        print(self.root_dir)
        
        self.load_inject_config()
        self.patch_inject_content()
    
    def remove_injected_content(self):
        """删除注入内容"""
        print()
        
        # 获取根目录（当前目录的上两级）
        current_dir = Path.cwd()
        self.root_dir = str(current_dir.parent.parent)
        print(self.root_dir)
        
        self.patch_remove_content()


def gen_menu():
    """生成菜单"""
    options = {
        "1": "删除注入内容",
        "2": "添加注入内容",
        "0": "Exit menu"
    }
    return MenuUtil.show_menu("选项菜单", options)


def main():
    """主函数"""
    injector = ContentInjector()
    
    while True:
        option = gen_menu()
        
        if option == '0':
            print()
            print("Bye")
            sys.exit(0)
        elif option == '1':
            # 删除配置文件中注入的内容
            injector.remove_injected_content()
        elif option == '2':
            # 添加配置文件中注入的内容
            injector.add_injected_content()
        elif option == 'h':
            continue
        else:
            print("Wrong!!")
        
        MenuUtil.wait_for_key()


if __name__ == "__main__":
    main()
