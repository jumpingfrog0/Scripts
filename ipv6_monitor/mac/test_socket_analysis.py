#!/usr/bin/env python3
"""
分析socket.getaddrinfo()获取IPv6地址的能力
"""
import socket
import sys

def test_socket_getaddrinfo():
    """测试socket.getaddrinfo()的功能"""
    print("=== 测试socket.getaddrinfo()功能 ===")
    
    # 获取本机主机名
    hostname = socket.gethostname()
    print(f"主机名: {hostname}")
    
    try:
        # 获取所有地址信息
        addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        
        print(f"\n获取到 {len(addr_info)} 个地址信息:")
        for i, info in enumerate(addr_info):
            family, socktype, proto, canonname, sockaddr = info
            
            if family == socket.AF_INET6:
                print(f"\nIPv6地址 {i+1}:")
                print(f"  协议族: {family} (AF_INET6)")
                print(f"  套接字类型: {socktype}")
                print(f"  协议: {proto}")
                print(f"  规范名: {canonname}")
                print(f"  地址: {sockaddr[0]}")
                print(f"  端口: {sockaddr[1]}")
                print(f"  流信息: {sockaddr[2] if len(sockaddr) > 2 else 'N/A'}")
                print(f"  范围ID: {sockaddr[3] if len(sockaddr) > 3 else 'N/A'}")
                
                # 分析地址特征
                ipv6_addr = sockaddr[0]
                analyze_ipv6_address(ipv6_addr)
                
    except socket.gaierror as e:
        print(f"获取地址信息失败: {e}")

def analyze_ipv6_address(ipv6_addr):
    """分析IPv6地址特征"""
    print(f"  地址分析:")
    
    # 检查是否为本地地址
    if ipv6_addr.startswith('::1') or ipv6_addr == '::1':
        print(f"    - 本地回环地址")
    elif ipv6_addr.startswith('fe80:'):
        print(f"    - 链路本地地址 (Link-local)")
    elif ipv6_addr.startswith('fc00:') or ipv6_addr.startswith('fd00:'):
        print(f"    - 唯一本地地址 (ULA)")
    elif ipv6_addr.startswith('2001:') or ipv6_addr.startswith('2003:'):
        print(f"    - 全局单播地址 (Global Unicast)")
    
    # 检查临时地址特征 (通常包含随机生成的部分)
    if 'ff:fe' in ipv6_addr.lower():
        print(f"    - 可能为EUI-64生成的地址 (基于MAC地址)")
    else:
        print(f"    - 可能为临时地址或手动配置")

def test_gethostbyname():
    """测试socket.gethostbyname()和gethostbyname_ex()"""
    print("\n=== 测试gethostbyname_ex() ===")
    
    hostname = socket.gethostname()
    try:
        hostname, aliaslist, ipaddrlist = socket.gethostbyname_ex(hostname)
        print(f"主机名: {hostname}")
        print(f"别名: {aliaslist}")
        print(f"IP地址: {ipaddrlist}")
        
        # 注意：gethostbyname_ex()主要返回IPv4地址
        for ip in ipaddrlist:
            if ':' in ip:  # IPv6
                print(f"IPv6地址: {ip}")
                analyze_ipv6_address(ip)
                
    except socket.gaierror as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    test_socket_getaddrinfo()
    test_gethostbyname()