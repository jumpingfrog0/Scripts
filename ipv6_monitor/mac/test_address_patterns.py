#!/usr/bin/env python3
"""
分析IPv6临时地址和永久地址的区分规律
"""
import socket
import subprocess
import re
import time
import uuid
import hashlib

def analyze_ipv6_address_patterns():
    """分析IPv6地址模式"""
    print("=== IPv6地址模式分析 ===")
    
    # 获取当前系统的IPv6地址
    ipv6_addresses = get_system_ipv6_addresses()
    
    print(f"发现 {len(ipv6_addresses)} 个IPv6地址:\n")
    
    for addr_info in ipv6_addresses:
        analyze_single_address(addr_info)

def get_system_ipv6_addresses():
    """获取系统的所有IPv6地址"""
    addresses = []
    
    try:
        # 使用socket.getaddrinfo
        hostname = socket.gethostname()
        addr_info = socket.getaddrinfo(hostname, None, socket.AF_INET6, socket.SOCK_STREAM)
        
        for info in addr_info:
            family, socktype, proto, canonname, sockaddr = info
            if family == socket.AF_INET6:
                addresses.append({
                    'address': sockaddr[0],
                    'source': 'socket.getaddrinfo',
                    'scope_id': sockaddr[3] if len(sockaddr) > 3 else None
                })
    except Exception as e:
        print(f"socket.getaddrinfo失败: {e}")
    
    # 尝试使用系统命令获取更多信息
    try:
        ifconfig_addrs = get_ifconfig_ipv6_addresses()
        addresses.extend(ifconfig_addrs)
    except Exception as e:
        print(f"ifconfig获取失败: {e}")
    
    # 去重
    unique_addrs = []
    seen = set()
    for addr in addresses:
        if addr['address'] not in seen:
            unique_addrs.append(addr)
            seen.add(addr['address'])
    
    return unique_addrs

def get_ifconfig_ipv6_addresses():
    """使用ifconfig获取IPv6地址"""
    addresses = []
    
    try:
        result = subprocess.run(['ifconfig'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            current_interface = None
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith(' ') and ':' in line:
                    current_interface = line.split(':')[0]
                elif 'inet6' in line and 'prefixlen' in line:
                    parts = line.split()
                    ipv6_addr = parts[1]
                    
                    # 提取标志信息
                    flags = []
                    if 'temporary' in line.lower():
                        flags.append('temporary')
                    if 'autoconf' in line.lower():
                        flags.append('autoconf')
                    if 'secured' in line.lower():
                        flags.append('secured')
                    
                    addresses.append({
                        'address': ipv6_addr,
                        'source': 'ifconfig',
                        'interface': current_interface,
                        'flags': flags
                    })
    except Exception:
        pass
    
    return addresses

def analyze_single_address(addr_info):
    """分析单个IPv6地址"""
    addr = addr_info['address']
    print(f"地址: {addr}")
    
    # 基本分类
    if addr == '::1':
        print("  类型: 本地回环地址")
        print("  性质: 永久地址")
        return
    elif addr.startswith('fe80:'):
        print("  类型: 链路本地地址")
        analyze_link_local_address(addr)
        return
    elif addr.startswith('fc00:') or addr.startswith('fd00:'):
        print("  类型: 唯一本地地址 (ULA)")
    elif addr.startswith('2001:') or addr.startswith('2003:'):
        print("  类型: 全局单播地址")
    else:
        print("  类型: 其他")
    
    # 临时vs永久地址分析
    analyze_temporary_vs_permanent(addr, addr_info)
    
    # EUI-64分析
    analyze_eui64(addr)
    
    # 随机性分析
    analyze_randomness(addr)
    
    # 接口标识符分析
    analyze_interface_identifier(addr)
    
    print()

def analyze_link_local_address(addr):
    """分析链路本地地址"""
    # 链路本地地址通常基于MAC地址生成
    print("  性质: 通常是基于MAC地址的永久地址")
    
    # 检查是否包含EUI-64标识
    if 'ff:fe' in addr.lower():
        print("  生成方式: EUI-64 (基于MAC地址)")
        print("  性质: 永久地址 (基于硬件)")
    else:
        print("  生成方式: 可能是随机化标识符")
        print("  性质: 可能是临时地址")

def analyze_temporary_vs_permanent(addr, addr_info):
    """分析临时地址vs永久地址"""
    print("\n  临时vs永久分析:")
    
    # 检查标志
    if 'flags' in addr_info:
        flags = addr_info['flags']
        if 'temporary' in flags:
            print("  → 临时地址 (由temporary标志确定)")
            return
        if 'autoconf' in flags:
            print("  → 可能是自动配置的永久地址")
    
    # 基于地址特征分析
    is_temporary = False
    is_permanent = False
    
    # 规则1: 包含EUI-64的通常是永久地址
    if 'ff:fe' in addr.lower():
        is_permanent = True
        print("  → 可能是永久地址 (包含EUI-64标识符)")
    
    # 规则2: 全局地址中，简单模式的可能是永久地址
    if addr.startswith('2001:') or addr.startswith('2003:'):
        # 分析地址复杂度
        segments = addr.split(':')
        complexity_score = calculate_complexity(segments)
        
        if complexity_score < 0.3:
            is_permanent = True
            print("  → 可能是永久地址 (地址结构较简单)")
        elif complexity_score > 0.7:
            is_temporary = True
            print("  → 可能是临时地址 (地址高度随机化)")
        else:
            print("  → 无法确定 (中等复杂度)")
    
    # 规则3: 检查是否为隐私地址格式
    if is_privacy_address_format(addr):
        is_temporary = True
        print("  → 可能是临时地址 (符合隐私地址格式)")
    
    if not is_temporary and not is_permanent:
        print("  → 无法确定，需要更多信息")

def analyze_eui64(addr):
    """分析EUI-64标识符"""
    print("\n  EUI-64分析:")
    
    # 查找ff:fe模式
    if 'ff:fe' in addr.lower():
        print("  → 发现EUI-64标识符 'ff:fe'")
        print("  → 地址基于MAC地址生成")
        
        # 尝试提取MAC地址
        try:
            mac = extract_mac_from_eui64(addr)
            if mac:
                print(f"  → 可能的MAC地址: {mac}")
        except:
            pass
    else:
        print("  → 未发现EUI-64标识符")
        print("  → 地址可能是随机生成")

def analyze_randomness(addr):
    """分析地址随机性"""
    print("\n  随机性分析:")
    
    # 标准化地址
    full_addr = expand_ipv6(addr)
    segments = full_addr.split(':')
    
    # 计算随机性指标
    entropy = calculate_entropy(segments)
    pattern_score = detect_patterns(segments)
    
    print(f"  → 熵值: {entropy:.2f} (越高越随机)")
    print(f"  → 模式得分: {pattern_score:.2f} (越低越有规律)")
    
    if entropy > 3.5 and pattern_score < 0.2:
        print("  → 高度随机化，可能是临时地址")
    elif entropy < 2.5 and pattern_score > 0.5:
        print("  → 有规律性，可能是永久地址")
    else:
        print("  → 中等随机性，需要进一步分析")

def analyze_interface_identifier(addr):
    """分析接口标识符"""
    print("\n  接口标识符分析:")
    
    # IPv6地址的最后64位通常是接口标识符
    segments = addr.split(':')
    if len(segments) >= 4:
        interface_id = ':'.join(segments[-4:])
        print(f"  → 接口标识符: {interface_id}")
        
        # 检查是否为常见的模式
        if interface_id.startswith('0000:0000:0000:0001'):
            print("  → 简单计数器模式，可能是永久地址")
        elif interface_id.count('0') < 8:
            print("  → 高度随机化，可能是临时地址")
        else:
            print("  → 中等随机性")

def calculate_complexity(segments):
    """计算地址复杂度"""
    # 简单的复杂度计算
    total_chars = sum(len(seg) for seg in segments)
    unique_chars = len(set(''.join(segments)))
    return unique_chars / total_chars if total_chars > 0 else 0

def calculate_entropy(segments):
    """计算信息熵"""
    import math
    
    all_chars = ''.join(segments)
    char_counts = {}
    for char in all_chars:
        char_counts[char] = char_counts.get(char, 0) + 1
    
    entropy = 0
    total_chars = len(all_chars)
    for count in char_counts.values():
        if count > 0:
            probability = count / total_chars
            entropy -= probability * math.log2(probability)
    
    return entropy

def detect_patterns(segments):
    """检测模式"""
    # 检测重复模式
    patterns = 0
    for i in range(len(segments)):
        for j in range(i+1, len(segments)):
            if segments[i] == segments[j]:
                patterns += 1
    
    return patterns / len(segments) if segments else 0

def is_privacy_address_format(addr):
    """检查是否为隐私地址格式"""
    # RFC 4941 隐私地址通常有特定的随机化特征
    segments = addr.split(':')
    
    # 检查最后64位的随机性
    if len(segments) >= 4:
        last_4 = segments[-4:]
        # 如果最后64位高度随机化，可能是隐私地址
        entropy = calculate_entropy(last_4)
        return entropy > 3.0
    
    return False

def extract_mac_from_eui64(addr):
    """从EUI-64地址提取MAC地址"""
    # 这个函数需要更复杂的实现
    # 这里只是简单示例
    return None

def expand_ipv6(addr):
    """展开IPv6地址"""
    # 处理IPv6简写
    if '::' in addr:
        parts = addr.split('::')
        left = parts[0].split(':') if parts[0] else []
        right = parts[1].split(':') if parts[1] else []
        
        missing = 8 - len(left) - len(right)
        expanded = left + ['0000'] * missing + right
        
        # 确保每个段都是4位
        expanded = [seg.zfill(4) for seg in expanded]
        return ':'.join(expanded)
    else:
        segments = addr.split(':')
        return ':'.join([seg.zfill(4) for seg in segments])

def compare_addresses():
    """比较不同类型地址的特征"""
    print("\n=== 地址类型比较 ===")
    
    # 示例地址
    test_addresses = [
        ('2001:db8::1', '手动配置地址'),
        ('2001:db8:1:2:3:4:5:6', '可能永久地址'),
        ('2001:db8:a1b2:c3d4:e5f6:7890:1234:5678', '可能临时地址'),
        ('fe80::1', '链路本地简单地址'),
        ('fe80::a1b2:c3d4:e5f6:1234', '链路本地复杂地址'),
    ]
    
    for addr, description in test_addresses:
        print(f"\n{description}: {addr}")
        
        # 模拟地址信息
        addr_info = {'address': addr, 'source': 'test'}
        
        # 快速分析
        segments = addr.split(':')
        entropy = calculate_entropy(segments)
        pattern_score = detect_patterns(segments)
        
        print(f"  熵值: {entropy:.2f}")
        print(f"  模式得分: {pattern_score:.2f}")
        
        if entropy > 3.0:
            print("  → 可能是临时地址")
        elif entropy < 2.0:
            print("  → 可能是永久地址")
        else:
            print("  → 不确定")

if __name__ == "__main__":
    analyze_ipv6_address_patterns()
    compare_addresses()