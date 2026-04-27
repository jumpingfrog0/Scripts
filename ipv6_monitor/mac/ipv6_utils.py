#!/usr/bin/env python3
"""
IPv6地址工具库 - 不依赖netifaces库
提供获取和区分永久IPv6地址的功能
"""

import socket
import subprocess
import platform
import re
import os
import json
from typing import List, Dict, Optional, Tuple


class IPv6Address:
    """IPv6地址对象"""
    
    def __init__(self, address: str, interface: str = None, source: str = None):
        self.address = address
        self.interface = interface
        self.source = source
        self.address_type = self._determine_type()
        self.is_permanent = None
        self.is_temporary = None
        self.is_eui64 = None
        self.entropy = None
        self.confidence = 0.0
        
        self._analyze_address()
    
    def _determine_type(self) -> str:
        """确定地址类型"""
        if self.address == '::1':
            return 'loopback'
        elif self.address.startswith('fe80:'):
            return 'link_local'
        elif self.address.startswith('fc00:') or self.address.startswith('fd00:'):
            return 'ula'
        elif self.address.startswith('2001:') or self.address.startswith('2003:'):
            return 'global_unicast'
        elif self.address.startswith('ff'):
            return 'multicast'
        else:
            return 'unknown'
    
    def _analyze_address(self):
        """分析地址特征"""
        # 检查EUI-64
        self.is_eui64 = 'ff:fe' in self.address.lower()
        
        # 计算熵值
        self.entropy = self._calculate_entropy()
        
        # 判断临时/永久
        self._determine_temp_permanent()
    
    def _calculate_entropy(self) -> float:
        """计算地址熵值"""
        import math
        
        segments = self.address.split(':')
        all_chars = ''.join(segments)
        
        if not all_chars:
            return 0.0
        
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
    
    def _determine_temp_permanent(self):
        """判断是临时还是永久地址"""
        # 基于规则的分类
        rules_score = 0
        reasons = []
        
        # 规则1: 回环地址是永久的
        if self.address_type == 'loopback':
            self.is_permanent = True
            self.is_temporary = False
            self.confidence = 1.0
            return
        
        # 规则2: 链路本地地址通常是永久的
        if self.address_type == 'link_local':
            if self.is_eui64:
                self.is_permanent = True
                self.is_temporary = False
                self.confidence = 0.8
                reasons.append("链路本地地址含EUI-64")
            else:
                self.is_permanent = True
                self.is_temporary = False
                self.confidence = 0.7
                reasons.append("链路本地地址通常是永久的")
        
        # 规则3: 全局地址分析
        elif self.address_type == 'global_unicast':
            # 高熵值通常表示临时地址
            if self.entropy > 3.5:
                rules_score += 2
                reasons.append("高熵值")
            
            # 不含EUI-64的全局地址可能是临时的
            if not self.is_eui64:
                rules_score += 1
                reasons.append("不含EUI-64")
            
            # 隐私地址格式检查
            if self._is_privacy_address_format():
                rules_score += 2
                reasons.append("符合隐私地址格式")
            
            # 基于规则得分判断
            if rules_score >= 3:
                self.is_temporary = True
                self.is_permanent = False
                self.confidence = min(0.8, 0.4 + rules_score * 0.2)
            elif rules_score == 0:
                self.is_permanent = True
                self.is_temporary = False
                self.confidence = 0.6
            else:
                self.confidence = 0.3
        
        else:
            self.confidence = 0.2
            reasons.append("地址类型不明确")
        
        self.reasons = reasons
    
    def _is_privacy_address_format(self) -> bool:
        """检查是否为隐私地址格式"""
        segments = self.address.split(':')
        if len(segments) >= 4:
            last_4 = segments[-4:]
            # 检查最后64位是否高度随机化
            return self._calculate_entropy_for_segments(last_4) > 3.0
        return False
    
    def _calculate_entropy_for_segments(self, segments: List[str]) -> float:
        """为特定段计算熵值"""
        import math
        
        all_chars = ''.join(segments)
        if not all_chars:
            return 0.0
        
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
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'address': self.address,
            'interface': self.interface,
            'source': self.source,
            'type': self.address_type,
            'is_permanent': self.is_permanent,
            'is_temporary': self.is_temporary,
            'is_eui64': self.is_eui64,
            'entropy': round(self.entropy, 2) if self.entropy else None,
            'confidence': round(self.confidence, 2) if self.confidence else None,
            'reasons': getattr(self, 'reasons', [])
        }
    
    def __str__(self):
        return f"IPv6Address({self.address}, type={self.address_type}, permanent={self.is_permanent}, confidence={self.confidence:.2f})"


class IPv6Utils:
    """IPv6工具类"""
    
    @staticmethod
    def get_ipv6_addresses(include_temporary: bool = True, 
                          include_link_local: bool = True,
                          include_loopback: bool = True) -> List[IPv6Address]:
        """
        获取IPv6地址列表
        
        Args:
            include_temporary: 是否包含临时地址
            include_link_local: 是否包含链路本地地址
            include_loopback: 是否包含回环地址
            
        Returns:
            IPv6Address对象列表
        """
        addresses = []
        
        # 方法1: socket.getaddrinfo
        addresses.extend(IPv6Utils._get_from_socket())
        
        # 方法2: 系统命令
        addresses.extend(IPv6Utils._get_from_system_commands())
        
        # 方法3: 系统文件 (Linux)
        if platform.system() == 'Linux':
            addresses.extend(IPv6Utils._get_from_system_files())
        
        # 去重
        unique_addrs = IPv6Utils._deduplicate_addresses(addresses)
        
        # 过滤
        filtered_addrs = IPv6Utils._filter_addresses(unique_addrs, include_temporary, 
                                                   include_link_local, include_loopback)
        
        return filtered_addrs
    
    @staticmethod
    def get_permanent_ipv6_addresses() -> List[IPv6Address]:
        """获取永久IPv6地址"""
        all_addresses = IPv6Utils.get_ipv6_addresses(include_temporary=False)
        
        # 筛选高可信度的永久地址
        permanent_addresses = []
        for addr in all_addresses:
            if addr.is_permanent and addr.confidence >= 0.5:
                permanent_addresses.append(addr)
            elif addr.confidence >= 0.7:  # 高置信度地址也包含
                permanent_addresses.append(addr)
        
        return permanent_addresses
    
    @staticmethod
    def _get_from_socket() -> List[IPv6Address]:
        """从socket获取地址"""
        addresses = []
        
        try:
            hostname = socket.gethostname()
            addr_info = socket.getaddrinfo(hostname, None, socket.AF_INET6, socket.SOCK_STREAM)
            
            for info in addr_info:
                family, socktype, proto, canonname, sockaddr = info
                if family == socket.AF_INET6:
                    addresses.append(IPv6Address(
                        address=sockaddr[0],
                        source='socket.getaddrinfo'
                    ))
        except Exception as e:
            print(f"socket.getaddrinfo失败: {e}")
        
        return addresses
    
    @staticmethod
    def _get_from_system_commands() -> List[IPv6Address]:
        """从系统命令获取地址"""
        addresses = []
        
        # 尝试ifconfig
        addresses.extend(IPv6Utils._get_from_ifconfig())
        
        # 尝试ip addr
        addresses.extend(IPv6Utils._get_from_ip_addr())
        
        return addresses
    
    @staticmethod
    def _get_from_ifconfig() -> List[IPv6Address]:
        """从ifconfig获取地址"""
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
                        
                        addresses.append(IPv6Address(
                            address=ipv6_addr,
                            interface=current_interface,
                            source='ifconfig'
                        ))
        except Exception:
            pass
        
        return addresses
    
    @staticmethod
    def _get_from_ip_addr() -> List[IPv6Address]:
        """从ip addr获取地址"""
        addresses = []
        
        try:
            result = subprocess.run(['ip', '-6', 'addr', 'show'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                current_interface = None
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('inet6'):
                        parts = line.split()
                        ipv6_addr = parts[1].split('/')[0]
                        
                        addresses.append(IPv6Address(
                            address=ipv6_addr,
                            interface=current_interface,
                            source='ip_addr'
                        ))
                    elif ':' in line and not line.startswith('inet6'):
                        current_interface = line.split(':')[1].strip()
        except Exception:
            pass
        
        return addresses
    
    @staticmethod
    def _get_from_system_files() -> List[IPv6Address]:
        """从系统文件获取地址 (Linux)"""
        addresses = []
        
        try:
            if os.path.exists('/proc/net/if_inet6'):
                with open('/proc/net/if_inet6', 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 6:
                            # 格式化IPv6地址
                            ipv6_addr = IPv6Utils._format_proc_ipv6(parts[0])
                            interface = parts[5]
                            
                            addresses.append(IPv6Address(
                                address=ipv6_addr,
                                interface=interface,
                                source='/proc/net/if_inet6'
                            ))
        except Exception:
            pass
        
        return addresses
    
    @staticmethod
    def _format_proc_ipv6(proc_addr: str) -> str:
        """格式化/proc文件中的IPv6地址"""
        if len(proc_addr) == 32:
            groups = [proc_addr[i:i+4] for i in range(0, 32, 4)]
            return ':'.join(groups)
        return proc_addr
    
    @staticmethod
    def _deduplicate_addresses(addresses: List[IPv6Address]) -> List[IPv6Address]:
        """去重地址列表"""
        seen = set()
        unique = []
        
        for addr in addresses:
            if addr.address not in seen:
                seen.add(addr.address)
                unique.append(addr)
        
        return unique
    
    @staticmethod
    def _filter_addresses(addresses: List[IPv6Address], include_temporary: bool,
                         include_link_local: bool, include_loopback: bool) -> List[IPv6Address]:
        """过滤地址列表"""
        filtered = []
        
        for addr in addresses:
            # 根据类型过滤
            if addr.address_type == 'loopback' and not include_loopback:
                continue
            if addr.address_type == 'link_local' and not include_link_local:
                continue
            if addr.is_temporary and not include_temporary:
                continue
            
            filtered.append(addr)
        
        return filtered
    
    @staticmethod
    def print_address_summary(addresses: List[IPv6Address]):
        """打印地址摘要"""
        print(f"\n找到 {len(addresses)} 个IPv6地址:")
        print("-" * 80)
        
        for addr in addresses:
            info = addr.to_dict()
            print(f"地址: {info['address']}")
            print(f"  类型: {info['type']}")
            print(f"  接口: {info['interface'] or '未知'}")
            print(f"  来源: {info['source']}")
            print(f"  永久地址: {info['is_permanent']} (置信度: {info['confidence']})")
            print(f"  EUI-64: {info['is_eui64']}")
            print(f"  熵值: {info['entropy']}")
            if info['reasons']:
                print(f"  原因: {', '.join(info['reasons'])}")
            print()


def main():
    """主函数示例"""
    print("=== IPv6地址获取工具 ===")
    
    # 获取所有IPv6地址
    print("\n1. 获取所有IPv6地址:")
    all_addresses = IPv6Utils.get_ipv6_addresses()
    IPv6Utils.print_address_summary(all_addresses)
    
    # 获取永久IPv6地址
    print("\n2. 获取永久IPv6地址:")
    permanent_addresses = IPv6Utils.get_permanent_ipv6_addresses()
    IPv6Utils.print_address_summary(permanent_addresses)
    
    # 导出为JSON
    if permanent_addresses:
        print("\n3. 永久地址JSON格式:")
        permanent_data = [addr.to_dict() for addr in permanent_addresses]
        print(json.dumps(permanent_data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()