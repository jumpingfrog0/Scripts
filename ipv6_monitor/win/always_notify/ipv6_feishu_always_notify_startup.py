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

def get_current_ipv6():
    """
    获取本机的全球单播IPv6地址（优先获取临时地址）
    返回: 字符串形式的IP地址，如果未找到则返回None
    """
    try:
        # 方法1：通过socket获取（简单，但可能不准确，可能会得到临时地址或稳定地址）
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
    except:
        return None

    # 如果需要更精确地通过网卡获取，可以使用netifaces库（需额外安装: pip install netifaces）
    """
    try:
        import netifaces
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            if TARGET_INTERFACE and interface != TARGET_INTERFACE:
                continue
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET6 in addrs:
                for addr_info in addrs[netifaces.AF_INET6]:
                    addr = addr_info['addr'].split('%')[0] # 去除%号后的区域ID
                    # 检查是否是全球单播地址
                    if addr.startswith(('2001:', '240', '2a', '2b', '2c')):
                        return addr
        return None
    except ImportError:
        print("未找到netifaces库，使用socket方法。请执行 'pip install netifaces' 安装以获得更准确的结果。")
        return None
    """

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
        title = "✅ 开机启动任务-IPv6地址已获取"
        content = f"**主机名:** {hostname}\n**时间:** {current_time}\n**新的IPv6地址:** {new_ip}"
    elif new_ip and old_ip:
        title = "🔄 开机启动任务-IPv6地址已变更"
        content = f"**主机名:** {hostname}\n**时间:** {current_time}\n**原地址:** {old_ip}\n**新地址:** {new_ip}"
    elif not new_ip and old_ip:
        title = "❌ 开机启动任务-IPv6地址已丢失"
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
    print("检测到IP变化，准备发送通知...")
    if send_feishu_notification(hostname, last_ip, current_ip):
        # 只有通知发送成功（或不需要发送）时才保存新的IP
        save_current_ip(current_ip)

if __name__ == '__main__':
    main()