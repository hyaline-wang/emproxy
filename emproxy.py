from proxy import Proxy
import psutil
import socket
import time 
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import threading
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich import box

def welcome_page():
    console = Console()

    # 创建标题
    title = Text("emNavi网络共享工具V1.0", style="bold magenta", justify="center")
    subtitle = Text("帮助无人机从其他设备上获取互联网连接", style="italic white", justify="center")

    # 创建一个面板以美化显示
    panel = Panel(
        renderable=title,
        title_align="center",
        border_style="bright_green",
        box=box.ROUNDED,
        padding=(1, 2)
    )

    # 打印面板和副标题
    console.print(panel)
    console.print(subtitle)

    console.print("\n[bold yellow]可用于以下场景:[/bold yellow]")
    console.print("1. usb直连至Host设备，Host设备可以访问互联网")
    console.print("2. 无人机为AP模式，Host设备连接至无人机的wifi，Host设备可以访问互联网")
    console.print("3. 无人机为STA模式，但是路由器无法连接互联网，有其他电脑可以通过有线或者无线连接到互联网")

    # 额外信息
    console.print("\n[bold yellow]你需要:[/bold yellow]")
    console.print("1. 保证无人机和此设备在同一个局域网内")
    console.print("2. 保证此设备能够访问互联网")
    console.print("3. 与emNavi控制台配合使用")
    console.print("\n[bold cyan]按Enter键继续...[/bold cyan]")
    input()  # 等待用户按回车键


class InputWithTimeout:
    def __init__(self, timeout):
        self.timeout = timeout
        self.input_value = None
        self.finished = threading.Event()

    def get_input(self):
        self.input_value = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4"])
        self.finished.set()

    def wait_for_input(self):
        input_thread = threading.Thread(target=self.get_input)
        input_thread.start()
        input_thread.join(timeout=self.timeout)

        if not self.finished.is_set():
            print("\n[bold red]Timeout! No input received.[/bold red]")
            return None
        return self.input_value
def display_info(ip_list):
    console = Console()

    # 创建表格
    table = Table(title="Network Interfaces")

    table.add_column("index", justify="center", style="cyan")
    table.add_column("Interface", justify="left", style="green")
    table.add_column("IPv4 Address", justify="center", style="magenta")
    # table.add_column("IPv6 Address", justify="center", style="magenta")


    # 添加数据（这里你可以替换为实际的数据）
    for i,ip_dict in enumerate(ip_list):
        table.add_row(str(i), ip_list[i]['interface'], ip_list[i]['IPv4'])
    # table.add_row("eth0", "192.168.1.10", "fe80::1")
    # table.add_row("lo", "127.0.0.1", "::1")

    # 打印表格
    console.print(table)
def get_ip_addresses():
    # 获取所有网络接口信息
    interfaces = psutil.net_if_addrs()
    ip_list = []
    ip_list.append({'interface': 'ALL', 'IPv4': '0.0.0.0', 'IPv6': ''})

    for interface_name, addresses in interfaces.items():
        ip_dict = {}
        ip_dict['interface'] = interface_name
        ip_dict['IPv4'] = ''
        ip_dict['IPv6'] = ''
        # print(f"Interface: {interface_name}")
        for addr in addresses:
            if addr.family == socket.AF_INET:  # IPv4 地址
                # print(f"  IPv4: {addr.address}")
                ip_dict['IPv4'] = addr.address
            elif addr.family == socket.AF_INET6:  # IPv6 地址
                # print(f"  IPv6: {addr.address}")
                ip_dict['IPv6'] = addr.address
        ip_list.append(ip_dict)
    return ip_list

import sys
if __name__ == '__main__':
    welcome_page()
    ip_dicts = get_ip_addresses()
    display_info(ip_dicts)    
    choice = Prompt.ask("选择你希望实现转发的网卡，默认为全部", choices=[str(i) for i in range(0, len(ip_dicts))])
    print(f"转发来自: {choice}   {ip_dicts[int(choice)]['interface']} {ip_dicts[int(choice)]['IPv4']} 的数据包")
    print("############################################")
    # 创建代理服务器
    # args = sys.argv
    arg = [ '--hostname', ip_dicts[int(choice)]['IPv4'], '--port', '8899']
    # print(arg)
    with Proxy(arg) as p:
        while True:
            try:
                time.sleep(0.5)
            except KeyboardInterrupt:
                break