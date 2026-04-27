import requests
import json
import socket
import os
from datetime import datetime

# ################### 配置区域 ###################
# 飞书机器人的Webhook URL
FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/71a05ec5-8c7a-4543-853f-22fd33706dc2"
# 用于存储上一次IP的文件路径
IP_CACHE_FILE = os.path.join(os.getenv('TEMP') or os.getcwd(), 'last_ipv6.txt')
# 获取IPV6的网卡名称（可选，如果为空则获取第一个非本地链接的IPv6）。例如："以太网"、"WLAN"。
TARGET_INTERFACE = ""
# ##############################################

def get_ipv6_netifaces():
    """
    使用netifaces库获取本机的全球单播IPv6地址（优先获取公用地址，排除DHCP地址）
    """
    try:
        import netifaces
        import subprocess

        # 运行netsh命令获取详细地址信息
        try:
            result = subprocess.run(['netsh', 'interface', 'ipv6', 'show', 'address'],
                                  capture_output=True, text=True, encoding='gbk')
            netsh_output = result.stdout
        except:
            netsh_output = ""

        interfaces = netifaces.interfaces()
        public_addrs = []    # 公用地址（非DHCP）
        dhcp_addrs = []      # DHCP地址

        # 从netsh输出中解析地址类型
        dhcp_addresses = set()
        public_addresses = set()
        if netsh_output:
            lines = netsh_output.split('\n')
            current_interface = None
            for line in lines:
                line = line.strip()
                # 查找接口行
                if '接口' in line and ':' in line:
                    # 提取接口名称
                    interface_part = line.split(':', 1)[-1].strip()
                    current_interface = interface_part
                # 查找地址行（包含IPv6地址的行）
                elif current_interface and ':' in line and not line.startswith('---'):
                    # 检查是否是地址行（包含冒号的IPv6地址格式）
                    parts = [part.strip() for part in line.split() if part.strip()]
                    if len(parts) >= 5 and ':' in parts[-1]:
                        addr = parts[-1]
                        addr_type = parts[0]  # 地址类型：DHCP、公用、手动、其他

                        # 根据地址类型分类
                        if addr_type == 'DHCP':
                            dhcp_addresses.add(addr)
                        elif addr_type == '公用':
                            public_addresses.add(addr)

        for interface in interfaces:
            if TARGET_INTERFACE and interface != TARGET_INTERFACE:
                continue

            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET6 in addrs:
                for addr_info in addrs[netifaces.AF_INET6]:
                    addr = addr_info['addr'].split('%')[0]

                    # 筛选全球单播地址
                    if addr.startswith(('2001:', '240', '2a', '2b', '2c')):
                        if addr in dhcp_addresses:
                            dhcp_addrs.append(addr)
                        elif addr in public_addresses:
                            public_addrs.append(addr)
                        else:
                            # 如果在netsh输出中没有找到对应类型，根据地址特征判断
                            if addr.startswith('240'):
                                public_addrs.append(addr)  # 240开头的通常是公用地址

        print(f"找到公用地址: {public_addrs}")
        print(f"找到DHCP地址: {dhcp_addrs}")

        # 优先返回公用地址（非DHCP）
        if public_addrs:
            return public_addrs[0]  # 返回第一个公用地址
        elif dhcp_addrs:
            return dhcp_addrs[0]    # 没有公用地址时返回DHCP地址
        return None

    except ImportError:
        print("未找到netifaces库，请执行 'pip install netifaces' 安装以获得更准确的结果。")
        return None
    except Exception as e:
        print(f"使用netifaces获取IPv6地址时出错: {e}")
        return None

def get_ipv6_socket():
    """
    使用socket库获取本机的全球单播IPv6地址
    """
    try:
        hostname = socket.gethostname()
        # 获取所有IPv6地址
        all_addrs = socket.getaddrinfo(hostname, None, socket.AF_INET6)
        # 过滤出全球单播地址（2000::/3），排除本地链接地址（fe80::/10）和回环地址（::1）
        global_addrs = [
            addr[4][0] for addr in all_addrs
            if not addr[4][0].startswith('fe80:')
            and not addr[4][0] == '::1'
            and addr[4][0].startswith(('2001:', '240', '2a', '2b', '2c'))
        ]
        # 返回找到的第一个IPv6地址
        return global_addrs[0] if global_addrs else None
    except Exception as e:
        print(f"使用socket获取IPv6地址时出错: {e}")
        return None

def get_current_ipv6():
    """
    获取本机的全球单播IPv6地址（优先使用netifaces，回退到socket）
    """
    # 首先尝试使用netifaces方法
    ipv6_addr = get_ipv6_netifaces()

    # 如果netifaces方法失败，使用socket方法作为备选
    if not ipv6_addr:
        print("netifaces方法失败，尝试使用socket方法...")
        ipv6_addr = get_ipv6_socket()

    return ipv6_addr

def read_last_ip():
    """读取上一次记录的IP地址"""
    if os.path.exists(IP_CACHE_FILE):
        with open(IP_CACHE_FILE, 'r') as f:
            return f.read().strip()
    return None

def save_current_ip(ip):
    """将当前的IP地址保存到文件"""
    with open(IP_CACHE_FILE, 'w') as f:
        f.write(ip if ip else '')

def send_feishu_notification(hostname, old_ip, new_ip):
    """发送飞书通知"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if new_ip and not old_ip:
        title = "✅ IPv6地址已获取"
        content = f"**主机名:** {hostname}\n**时间:** {current_time}\n**新的IPv6地址:** {new_ip}"
    elif new_ip and old_ip:
        title = "🔄 IPv6地址已变更"
        content = f"**主机名:** {hostname}\n**时间:** {current_time}\n**原地址:** {old_ip}\n**新地址:** {new_ip}"
    elif not new_ip and old_ip:
        title = "❌ IPv6地址已丢失"
        content = f"**主机名:** {hostname}\n**时间:** {current_time}\n**原地址:** {old_ip}\n**新地址:** 无"
    else:
        # 一直都没有IP，不发通知
        return False

    message = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "content": content,
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "content": "💡 长按下方内容即可复制IP地址",
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "hr"  # 分隔线
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": new_ip or '无'
                        }
                    ]
                }
            ],
            "header": {
                "title": {
                    "content": title,
                    "tag": "plain_text"
                }
            }
        }
    }

    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(FEISHU_WEBHOOK_URL, data=json.dumps(message), headers=headers, timeout=10)
        result = response.json()
        if result.get('code') == 0:
            print(f"[{current_time}] 飞书通知发送成功")
            return True
        else:
            print(f"[{current_time}] 飞书通知发送失败: {result}")
            return False
    except Exception as e:
        print(f"[{current_time}] 发送请求时出错: {e}")
        return False

def main():
    hostname = socket.gethostname()
    current_ip = get_current_ipv6()
    last_ip = read_last_ip()

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 当前IP: {current_ip}, 上次IP: {last_ip}")

    # 如果IP地址发生变化（包括从无到有，从有到无）
    if current_ip != last_ip:
        print("检测到IP变化，准备发送通知...")
        if send_feishu_notification(hostname, last_ip, current_ip):
            # 只有通知发送成功（或不需要发送）时才保存新的IP
            save_current_ip(current_ip)
    else:
        print("IP地址未变化。")

if __name__ == '__main__':
    main()