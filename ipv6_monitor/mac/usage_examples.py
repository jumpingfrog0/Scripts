#!/usr/bin/env python3
"""
IPv6地址工具使用示例
"""

import json
from ipv6_utils import IPv6Utils, IPv6Address


def example_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 获取所有IPv6地址
    all_addresses = IPv6Utils.get_ipv6_addresses()
    print(f"找到 {len(all_addresses)} 个IPv6地址")
    
    # 获取永久地址
    permanent_addresses = IPv6Utils.get_permanent_ipv6_addresses()
    print(f"找到 {len(permanent_addresses)} 个永久IPv6地址")
    
    # 打印详细信息
    for addr in permanent_addresses:
        print(f"\n永久地址: {addr.address}")
        print(f"  类型: {addr.address_type}")
        print(f"  置信度: {addr.confidence:.2f}")
        print(f"  是否为EUI-64: {addr.is_eui64}")
        if hasattr(addr, 'reasons') and addr.reasons:
            print(f"  判断依据: {', '.join(addr.reasons)}")


def example_filter_usage():
    """过滤功能示例"""
    print("\n=== 过滤功能示例 ===")
    
    # 只获取全局单播地址
    global_addresses = IPv6Utils.get_ipv6_addresses(
        include_temporary=True,
        include_link_local=False,
        include_loopback=False
    )
    
    print(f"全局单播地址数量: {len(global_addresses)}")
    for addr in global_addresses:
        print(f"  {addr.address} - 类型: {addr.address_type}")


def example_confidence_filter():
    """置信度过滤示例"""
    print("\n=== 置信度过滤示例 ===")
    
    # 获取所有地址
    all_addresses = IPv6Utils.get_ipv6_addresses()
    
    # 筛选高置信度的永久地址
    high_confidence_permanent = [
        addr for addr in all_addresses 
        if addr.is_permanent and addr.confidence >= 0.8
    ]
    
    print(f"高置信度永久地址 (置信度 >= 0.8): {len(high_confidence_permanent)}")
    for addr in high_confidence_permanent:
        print(f"  {addr.address} (置信度: {addr.confidence:.2f})")
    
    # 中等置信度地址
    medium_confidence = [
        addr for addr in all_addresses
        if addr.is_permanent and 0.5 <= addr.confidence < 0.8
    ]
    
    print(f"中等置信度永久地址: {len(medium_confidence)}")
    for addr in medium_confidence:
        print(f"  {addr.address} (置信度: {addr.confidence:.2f})")


def example_json_export():
    """JSON导出示例"""
    print("\n=== JSON导出示例 ===")
    
    # 获取永久地址
    permanent_addresses = IPv6Utils.get_permanent_ipv6_addresses()
    
    # 转换为字典列表
    address_data = [addr.to_dict() for addr in permanent_addresses]
    
    # 导出为JSON
    json_output = json.dumps(address_data, indent=2, ensure_ascii=False)
    print("永久地址JSON数据:")
    print(json_output)
    
    # 保存到文件
    try:
        with open('permanent_ipv6_addresses.json', 'w', encoding='utf-8') as f:
            json.dump(address_data, f, indent=2, ensure_ascii=False)
        print("\n数据已保存到 permanent_ipv6_addresses.json")
    except Exception as e:
        print(f"保存文件失败: {e}")


def example_custom_analysis():
    """自定义分析示例"""
    print("\n=== 自定义分析示例 ===")
    
    # 获取所有地址
    all_addresses = IPv6Utils.get_ipv6_addresses()
    
    # 按类型分组
    address_groups = {}
    for addr in all_addresses:
        addr_type = addr.address_type
        if addr_type not in address_groups:
            address_groups[addr_type] = []
        address_groups[addr_type].append(addr)
    
    # 分析每种类型
    for addr_type, addresses in address_groups.items():
        print(f"\n{addr_type} 类型地址分析:")
        print(f"  总数: {len(addresses)}")
        
        permanent_count = sum(1 for addr in addresses if addr.is_permanent)
        temporary_count = sum(1 for addr in addresses if addr.is_temporary)
        
        print(f"  永久地址: {permanent_count}")
        print(f"  临时地址: {temporary_count}")
        
        # 平均熵值
        if addresses:
            avg_entropy = sum(addr.entropy for addr in addresses if addr.entropy) / len(addresses)
            print(f"  平均熵值: {avg_entropy:.2f}")
        
        # EUI-64地址数量
        eui64_count = sum(1 for addr in addresses if addr.is_eui64)
        print(f"  EUI-64地址: {eui64_count}")


def example_manual_address_analysis():
    """手动地址分析示例"""
    print("\n=== 手动地址分析示例 ===")
    
    # 手动创建地址对象进行分析
    test_addresses = [
        "2001:db8::1",
        "2001:db8:a1b2:c3d4:e5f6:7890:1234:5678",
        "fe80::1",
        "fe80::8f6:3dbd:d3bd:e589",
        "::1"
    ]
    
    for addr_str in test_addresses:
        addr = IPv6Address(addr_str, source="manual")
        print(f"\n分析地址: {addr_str}")
        print(f"  类型: {addr.address_type}")
        print(f"  永久地址: {addr.is_permanent} (置信度: {addr.confidence:.2f})")
        print(f"  EUI-64: {addr.is_eui64}")
        print(f"  熵值: {addr.entropy:.2f}")


def example_interface_based_filtering():
    """基于接口的过滤示例"""
    print("\n=== 基于接口的过滤示例 ===")
    
    # 获取所有地址
    all_addresses = IPv6Utils.get_ipv6_addresses()
    
    # 按接口分组
    interface_groups = {}
    for addr in all_addresses:
        interface = addr.interface or "unknown"
        if interface not in interface_groups:
            interface_groups[interface] = []
        interface_groups[interface].append(addr)
    
    # 分析每个接口
    for interface, addresses in interface_groups.items():
        print(f"\n接口 {interface}:")
        print(f"  地址数量: {len(addresses)}")
        
        for addr in addresses:
            print(f"    {addr.address} ({addr.address_type}, 永久: {addr.is_permanent})")


def example_best_practices():
    """最佳实践示例"""
    print("\n=== 最佳实践示例 ===")
    
    print("""
建议的使用模式:

1. 获取高可信度的永久地址:
   permanent_addrs = IPv6Utils.get_permanent_ipv6_addresses()
   
2. 获取特定类型的地址:
   global_addrs = IPv6Utils.get_ipv6_addresses(
       include_temporary=False,
       include_link_local=False,
       include_loopback=False
   )
   
3. 进一步筛选:
   reliable_addrs = [addr for addr in permanent_addrs if addr.confidence >= 0.8]
   
4. 错误处理:
   try:
       addresses = IPv6Utils.get_ipv6_addresses()
   except Exception as e:
       print(f"获取地址失败: {e}")
       addresses = []
   
5. 性能考虑:
   - 结果可以缓存，避免重复调用
   - 系统命令可能较慢，考虑超时设置
   - 不同平台使用不同的获取策略
""")


if __name__ == "__main__":
    # 运行所有示例
    example_basic_usage()
    example_filter_usage()
    example_confidence_filter()
    example_json_export()
    example_custom_analysis()
    example_manual_address_analysis()
    example_interface_based_filtering()
    example_best_practices()