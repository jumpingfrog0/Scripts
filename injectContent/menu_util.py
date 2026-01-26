#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
菜单工具类
"""

import os


class MenuUtil:
    """菜单工具类"""
    
    @staticmethod
    def clear_screen():
        """清屏"""
        os.system('clear')
    
    @staticmethod
    def show_menu(title: str, options: dict) -> str:
        """
        显示菜单并获取用户选择
        
        Args:
            title: 菜单标题
            options: 选项字典，格式为 {选项编号: 选项描述}
            
        Returns:
            用户选择的选项编号
        """
        MenuUtil.clear_screen()
        print()
        print(f"\t\t\t{title}\n")
        
        for key, value in options.items():
            print(f"\t{key}. {value}")
        
        print()
        option = input("\t\tEnter option: ")
        return option.strip()
    
    @staticmethod
    def wait_for_key():
        """等待用户按键"""
        print()
        input("\n\n\tHit any key to continue")
