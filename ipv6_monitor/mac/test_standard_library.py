#!/usr/bin/env python3
"""
研究Python标准库中其他获取IPv6地址的方法
"""
import socket
import subprocess
import json
import sys
import os
import platform

def test_subprocess_ifconfig():
    """使用ifconfig命令获取IPv6地址"""
    print("=== 使用ifconfig命令 ===")
    
    try:
        # 尝试使用ifconfig命令
        result = subprocess.run(['ifconfig'], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("ifconfig输出中的IPv6地址:")
            lines = result.stdout.split('\n')
            current_interface = None
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith(' '):
                    # 新的接口
                    current_interface = line.split(':')[0]
                elif 'inet6' in line and 'prefixlen' in line:
                    # IPv6地址行
                    parts = line.split()
                    ipv6_addr = parts[1]
                    prefixlen = parts[2].replace('prefixlen', '')
                    
                    print(f"接口: {current_interface}")
                    print(f"  IPv6地址: {ipv6_addr}")
                    print(f"  前缀长度: {prefixlen}")
                    analyze_ipv6_flags(line)
                    print()
        else:
            print(f"ifconfig命令失败: {result.stderr}")
            
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"ifconfig命令不可用: {e}")

def test_subprocess_ip_addr():
    """使用ip addr命令获取IPv6地址"""
    print("=== 使用ip addr命令 ===")
    
    try:
        result = subprocess.run(['ip', '-6', 'addr', 'show'], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("ip addr输出:")
            lines = result.stdout.split('\n')
            current_interface = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('inet6'):
                    # IPv6地址行
                    parts = line.split()
                    ipv6_addr = parts[1].split('/')[0]
                    prefixlen = parts[1].split('/')[1]
                    
                    print(f"接口: {current_interface}")
                    print(f"  IPv6地址: {ipv6_addr}")
                    print(f"  前缀长度: {prefixlen}")
                    
                    # 分析标志
                    flags = []
                    if 'scope' in line:
                        scope_idx = line.find('scope')
                        scope_value = line[scope_idx:].split()[1]
                        flags.append(f"scope:{scope_value}")
                    
                    if 'valid_lft' in line and 'preferred_lft' in line:
                        if 'forever' not in line:
                            flags.append("可能有生命周期限制")
                    
                    if flags:
                        print(f"  标志: {', '.join(flags)}")
                    print()
                elif ':' in line and not line.startswith('inet6'):
                    # 接口名行
                    current_interface = line.split(':')[1].strip()
                    
        else:
            print(f"ip addr命令失败: {result.stderr}")
            
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"ip addr命令不可用: {e}")

def test_os_level_files():
    """尝试读取系统文件获取IPv6地址"""
    print("=== 读取系统文件 ===")
    
    # Linux系统文件
    if platform.system() == 'Linux':
        test_linux_sys_files()
    elif platform.system() == 'Darwin':  # macOS
        test_macos_sys_files()
    else:
        print(f"不支持的操作系统: {platform.system()}")

def test_linux_sys_files():
    """测试Linux系统文件"""
    print("Linux系统文件分析:")
    
    # 尝试读取/proc/net/if_inet6
    if os.path.exists('/proc/net/if_inet6'):
        try:
            with open('/proc/net/if_inet6', 'r') as f:
                content = f.read()
                print("\n/proc/net/if_inet6内容:")
                print("格式: IPv6地址 接口索引 前缀长度 范围 标志 接口名")
                for line in content.strip().split('\n'):
                    parts = line.split()
                    if len(parts) >= 6:
                        ipv6_addr = format_ipv6_from_proc(parts[0])
                        if_idx = parts[1]
                        prefixlen = parts[2]
                        scope = parts[3]
                        flags = parts[4]
                        interface = parts[5]
                        
                        print(f"\n接口: {interface}")
                        print(f"  IPv6地址: {ipv6_addr}")
                        print(f"  前缀长度: {prefixlen}")
                        print(f"  范围: {get_scope_name(scope)}")
                        print(f"  标志: {analyze_proc_flags(flags)}")
                        
        except Exception as e:
            print(f"读取/proc/net/if_inet6失败: {e}")
    else:
        print("文件/proc/net/if_inet6不存在")

def test_macos_sys_files():
    """测试macOS系统文件"""
    print("macOS系统文件分析:")
    
    # macOS使用不同的方法
    try:
        # 尝试使用networksetup命令
        result = subprocess.run(['networksetup', '-listallhardwareports'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("可用网络接口:")
            print(result.stdout)
            
            # 获取特定接口的IPv6地址
            interfaces = ['Wi-Fi', 'Ethernet', 'Thunderbolt Ethernet']
            for interface in interfaces:
                try:
                    ipv6_result = subprocess.run(['networksetup', '-getinfo', interface], 
                                               capture_output=True, text=True, timeout=5)
                    if 'IPv6:' in ipv6_result.stdout:
                        print(f"\n{interface} IPv6信息:")
                        lines = ipv6_result.stdout.split('\n')
                        for line in lines:
                            if 'IPv6:' in line or 'IPv6 IP address:' in line:
                                print(f"  {line}")
                except:
                    pass
                    
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"networksetup命令不可用: {e}")

def format_ipv6_from_proc(proc_addr):
    """将/proc/net/if_inet6中的地址格式化为标准IPv6格式"""
    # 地址在proc文件中是32个十六进制字符，没有冒号分隔
    if len(proc_addr) == 32:
        # 每4个字符一组，用冒号分隔
        groups = [proc_addr[i:i+4] for i in range(0, 32, 4)]
        return ':'.join(groups)
    return proc_addr

def get_scope_name(scope_code):
    """将scope代码转换为名称"""
    scope_map = {
        '00': '全局',
        '20': '链路本地',
        '40': '管理员本地',
        '50': '站点本地',
        '80': '组织本地'
    }
    return scope_map.get(scope_code, f'未知({scope_code})')

def analyze_proc_flags(flags):
    """分析/proc/net/if_inet6中的标志"""
    flags_int = int(flags, 16)
    flag_names = []
    
    if flags_int & 0x80:
        flag_names.append('临时地址')
    if flags_int & 0x40:
        flag_names.append('自动配置')
    if flags_int & 0x20:
        flag_names.append('永久地址')
    if flags_int & 0x10:
        flag_names.append('回环地址')
    
    return ', '.join(flag_names) if flag_names else '无特殊标志'

def analyze_ipv6_flags(ifconfig_line):
    """分析ifconfig输出中的IPv6标志"""
    flags = []
    
    if 'temporary' in line.lower():
        flags.append('临时地址')
    if 'autoconf' in line.lower():
        flags.append('自动配置')
    if 'secured' in line.lower():
        flags.append('安全地址')
    
    if flags:
        print(f"  检测到的标志: {', '.join(flags)}")

def test_socket_interface_ioctl():
    """测试使用socket的ioctl接口"""
    print("\n=== 测试socket ioctl接口 ===")
    
    try:
        # 尝试使用SIOCGIFADDR等ioctl命令
        # 注意：这在不同平台上差异很大
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        
        # 这个在Python中很难直接使用，需要平台相关的代码
        print("socket ioctl接口在不同平台上差异较大，需要平台相关代码")
        print("建议使用subprocess调用系统命令作为替代方案")
        
    except Exception as e:
        print(f"socket ioctl测试失败: {e}")

if __name__ == "__main__":
    test_subprocess_ifconfig()
    print("\n" + "="*50 + "\n")
    test_subprocess_ip_addr()
    print("\n" + "="*50 + "\n")
    test_os_level_files()
    print("\n" + "="*50 + "\n")
    test_socket_interface_ioctl()