# 不使用netifaces库获取IPv6永久地址的研究报告

## 研究概述

本研究分析了在不使用netifaces库的情况下，如何区分和获取永久的IPv6地址。通过分析Python标准库、操作系统层面的方法以及IPv6地址的特征模式，提供了一套完整的解决方案。

## 主要发现

### 1. socket.getaddrinfo()的能力和限制

**能力：**
- 可以获取所有类型的IPv6地址（回环、链路本地、全局单播等）
- 提供基本的地址类型信息（通过地址前缀判断）
- 跨平台兼容性好

**限制：**
- 无法直接提供地址的生命周期信息（临时vs永久）
- 无法获取接口级别的详细信息
- 无法访问系统级别的地址标志

**代码示例：**
```python
import socket

def get_ipv6_from_socket():
    hostname = socket.gethostname()
    addr_info = socket.getaddrinfo(hostname, None, socket.AF_INET6, socket.SOCK_STREAM)
    
    for info in addr_info:
        family, socktype, proto, canonname, sockaddr = info
        if family == socket.AF_INET6:
            print(f"IPv6地址: {sockaddr[0]}")
```

### 2. Python标准库替代方案

#### subprocess模块方法

**ifconfig命令（macOS/BSD）：**
```python
import subprocess

def get_ipv6_from_ifconfig():
    try:
        result = subprocess.run(['ifconfig'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            # 解析输出，提取IPv6地址和标志
            lines = result.stdout.split('\n')
            for line in lines:
                if 'inet6' in line and 'prefixlen' in line:
                    parts = line.split()
                    ipv6_addr = parts[1]
                    flags = extract_flags(line)
                    print(f"地址: {ipv6_addr}, 标志: {flags}")
    except Exception as e:
        print(f"ifconfig命令失败: {e}")
```

**ip addr命令（Linux）：**
```python
def get_ipv6_from_ip_addr():
    try:
        result = subprocess.run(['ip', '-6', 'addr', 'show'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            # 解析输出，提取IPv6地址
            print(result.stdout)
    except Exception as e:
        print(f"ip addr命令失败: {e}")
```

### 3. 操作系统层面的方法

#### Linux系统文件

**/proc/net/if_inet6文件：**
```python
def get_ipv6_from_proc():
    try:
        with open('/proc/net/if_inet6', 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 6:
                    ipv6_addr = format_proc_ipv6(parts[0])
                    flags = int(parts[4], 16)
                    interface = parts[5]
                    
                    # 分析标志位
                    is_temporary = bool(flags & 0x80)
                    is_permanent = bool(flags & 0x20)
                    
                    print(f"接口: {interface}, 地址: {ipv6_addr}")
                    print(f"  临时: {is_temporary}, 永久: {is_permanent}")
    except Exception as e:
        print(f"读取proc文件失败: {e}")
```

#### macOS系统命令

**networksetup命令：**
```python
def get_macos_network_info():
    try:
        # 获取硬件端口信息
        result = subprocess.run(['networksetup', '-listallhardwareports'], 
                              capture_output=True, text=True, timeout=10)
        print(result.stdout)
        
        # 获取特定接口的IPv6信息
        interfaces = ['Wi-Fi', 'Ethernet']
        for interface in interfaces:
            ipv6_result = subprocess.run(['networksetup', '-getinfo', interface], 
                                       capture_output=True, text=True, timeout=5)
            if 'IPv6:' in ipv6_result.stdout:
                print(f"{interface} IPv6信息已获取")
    except Exception as e:
        print(f"macOS网络命令失败: {e}")
```

### 4. 临时地址与永久地址的区分规律

#### 地址特征分析

**链路本地地址（fe80::/10）：**
- 通常是永久地址
- 基于MAC地址使用EUI-64生成
- 包含`ff:fe`标识符

**全局单播地址：**
- 永久地址：结构较简单，可能包含EUI-64
- 临时地址：高度随机化（隐私地址）

**判断规则：**
```python
def analyze_ipv6_address(addr):
    entropy = calculate_address_entropy(addr)
    has_eui64 = 'ff:fe' in addr.lower()
    
    if addr.startswith('fe80:'):
        return 'permanent'  # 链路本地通常是永久的
    elif entropy > 3.5 and not has_eui64:
        return 'temporary'  # 高随机性，无EUI-64，可能是临时的
    elif has_eui64:
        return 'permanent'  # 基于MAC地址，通常是永久的
    else:
        return 'uncertain'  # 需要更多信息
```

#### 熵值计算方法

```python
import math

def calculate_address_entropy(ipv6_addr):
    """计算IPv6地址的信息熵"""
    # 移除冒号，统一处理
    clean_addr = ipv6_addr.replace(':', '')
    
    # 统计字符频率
    char_counts = {}
    for char in clean_addr:
        char_counts[char] = char_counts.get(char, 0) + 1
    
    # 计算熵值
    entropy = 0
    total_chars = len(clean_addr)
    
    for count in char_counts.values():
        if count > 0:
            probability = count / total_chars
            entropy -= probability * math.log2(probability)
    
    return entropy
```

## 综合解决方案

### 核心工具类

```python
class IPv6Address:
    """IPv6地址对象，包含详细分析信息"""
    
    def __init__(self, address, interface=None, source=None):
        self.address = address
        self.interface = interface
        self.source = source
        self.address_type = self._determine_type()
        self.entropy = self._calculate_entropy()
        self.is_permanent = self._determine_permanent()
        self.confidence = 0.0  # 置信度评分
    
    def _determine_type(self):
        """根据前缀确定地址类型"""
        if self.address == '::1':
            return 'loopback'
        elif self.address.startswith('fe80:'):
            return 'link_local'
        elif self.address.startswith(('fc00:', 'fd00:')):
            return 'ula'
        elif self.address.startswith(('2001:', '2003:')):
            return 'global_unicast'
        else:
            return 'unknown'
    
    def _calculate_entropy(self):
        """计算地址熵值"""
        # 熵值计算实现
        pass
    
    def _determine_permanent(self):
        """判断是否为永久地址"""
        # 基于规则的分类逻辑
        pass
```

### 工具函数

```python
class IPv6Utils:
    """IPv6工具类"""
    
    @staticmethod
    def get_permanent_ipv6_addresses():
        """获取永久IPv6地址"""
        all_addresses = IPv6Utils.get_ipv6_addresses()
        
        # 筛选高可信度的永久地址
        permanent_addresses = []
        for addr in all_addresses:
            if addr.is_permanent and addr.confidence >= 0.5:
                permanent_addresses.append(addr)
        
        return permanent_addresses
    
    @staticmethod
    def get_ipv6_addresses(include_temporary=True, include_link_local=True, 
                          include_loopback=True):
        """获取IPv6地址列表"""
        addresses = []
        
        # 多种方法获取地址
        addresses.extend(IPv6Utils._get_from_socket())
        addresses.extend(IPv6Utils._get_from_system_commands())
        
        if platform.system() == 'Linux':
            addresses.extend(IPv6Utils._get_from_system_files())
        
        # 去重和过滤
        return IPv6Utils._deduplicate_and_filter(addresses, include_temporary,
                                               include_link_local, include_loopback)
```

## 使用示例

### 基本使用

```python
# 获取永久地址
permanent_addresses = IPv6Utils.get_permanent_ipv6_addresses()

for addr in permanent_addresses:
    print(f"永久地址: {addr.address}")
    print(f"  类型: {addr.address_type}")
    print(f"  置信度: {addr.confidence:.2f}")
    print(f"  接口: {addr.interface}")
```

### 高级过滤

```python
# 只获取全局单播永久地址
global_permanent = IPv6Utils.get_ipv6_addresses(
    include_temporary=False,
    include_link_local=False,
    include_loopback=False
)

# 筛选高置信度地址
reliable_addresses = [
    addr for addr in global_permanent 
    if addr.confidence >= 0.8
]
```

### 数据导出

```python
import json

# 导出为JSON
address_data = [addr.to_dict() for addr in permanent_addresses]
json_output = json.dumps(address_data, indent=2)

# 保存到文件
with open('permanent_ipv6.json', 'w') as f:
    json.dump(address_data, f, indent=2)
```

## 性能考虑

1. **缓存机制**：系统配置通常不会频繁变化，可以缓存结果
2. **超时设置**：系统命令可能较慢，需要设置合理的超时时间
3. **错误处理**：某些系统命令可能不可用，需要有降级方案
4. **平台适配**：不同操作系统使用不同的获取策略

## 局限性

1. **准确性限制**：基于启发式规则的判断可能不完全准确
2. **平台差异**：不同操作系统表现可能不同
3. **权限要求**：某些系统命令可能需要特定权限
4. **动态变化**：网络配置变化时可能需要重新获取

## 最佳实践

1. **多重验证**：使用多种方法交叉验证结果
2. **置信度评估**：使用置信度评分来量化结果可靠性
3. **错误处理**：完善的异常处理机制
4. **定期更新**：网络配置变化时重新获取地址
5. **平台适配**：针对不同操作系统优化获取策略

## 结论

本研究提供了一套完整的、不依赖netifaces库的IPv6地址获取和分类方案。通过结合Python标准库、系统命令和地址特征分析，能够有效区分永久地址和临时地址。虽然在某些情况下准确性可能不如专门的网络库，但对于大多数应用场景来说已经足够使用，并且具有良好的跨平台兼容性。