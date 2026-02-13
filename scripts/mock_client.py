#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟客户端 - 用于测试心跳机制
无需编译C++代码，直接使用Python模拟设备
"""

import socket
import struct
import time
import sys
import signal
import threading

# 消息类型定义
MSG_HEARTBEAT = 0x01
MSG_HEARTBEAT_ACK = 0x02
MSG_IMAGE_DATA = 0x03
MSG_REGISTER = 0x04
MSG_REGISTER_ACK = 0x05

class MockClient:
    def __init__(self, device_id, device_name, location, server_ip='127.0.0.1', server_port=8888):
        self.device_id = device_id
        self.device_name = device_name
        self.location = location
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = None
        self.running = False
        self.heartbeat_interval = 10  # 10秒心跳间隔（用于测试）

    def connect(self):
        """连接到服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_ip, self.server_port))
            print(f"[OK] 成功连接到服务器: {self.server_ip}:{self.server_port}")
            return True
        except Exception as e:
            print(f"[ERROR] 连接失败: {e}")
            return False

    def register(self):
        """注册设备"""
        try:
            # 构造注册消息
            device_name_bytes = self.device_name.encode('utf-8')[:32].ljust(32, b'\x00')
            location_bytes = self.location.encode('utf-8')[:64].ljust(64, b'\x00')

            data = device_name_bytes + location_bytes
            data_length = len(data)

            # 发送消息头
            header = struct.pack('!BBHI', MSG_REGISTER, 0, self.device_id, data_length)
            self.socket.send(header)

            # 发送数据
            self.socket.send(data)

            # 接收响应
            ack_header = self.socket.recv(8)
            if len(ack_header) == 8:
                msg_type, _, _, _ = struct.unpack('!BBHI', ack_header)
                if msg_type == MSG_REGISTER_ACK:
                    print(f"[OK] 设备注册成功 [ID: {self.device_id}, 名称: {self.device_name}]")
                    return True

            print("[ERROR] 注册响应无效")
            return False

        except Exception as e:
            print(f"[ERROR] 注册失败: {e}")
            return False

    def send_heartbeat(self):
        """发送心跳"""
        try:
            # 发送心跳消息
            header = struct.pack('!BBHI', MSG_HEARTBEAT, 0, self.device_id, 0)
            self.socket.send(header)

            # 接收响应
            self.socket.settimeout(5)
            ack_header = self.socket.recv(8)

            if len(ack_header) == 8:
                msg_type, _, _, _ = struct.unpack('!BBHI', ack_header)
                if msg_type == MSG_HEARTBEAT_ACK:
                    return True

            print("[WARNING] 心跳响应无效")
            return False

        except socket.timeout:
            print("[ERROR] 心跳响应超时")
            return False
        except Exception as e:
            print(f"[ERROR] 发送心跳失败: {e}")
            return False

    def heartbeat_thread(self):
        """心跳线程"""
        print(f"[OK] 心跳线程启动，间隔: {self.heartbeat_interval}秒")

        while self.running:
            time.sleep(self.heartbeat_interval)

            if self.running:
                if not self.send_heartbeat():
                    print("[ERROR] 心跳失败")
                    break

    def start(self):
        """启动客户端"""
        if not self.connect():
            return False

        if not self.register():
            return False

        # 启动心跳线程
        self.running = True
        heartbeat_thread = threading.Thread(target=self.heartbeat_thread, daemon=True)
        heartbeat_thread.start()

        print("[OK] 系统启动成功，开始监控...")
        print("按 Ctrl+C 停止客户端")

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[INFO] 接收到中断信号，正在退出...")

        self.stop()
        return True

    def stop(self):
        """停止客户端"""
        self.running = False
        if self.socket:
            self.socket.close()
        print("[OK] 客户端已停止")

def main():
    print("=" * 60)
    print("模拟客户端 - 心跳机制测试")
    print("=" * 60)
    print()

    # 创建模拟客户端
    client = MockClient(
        device_id=101,
        device_name="TestDevice-001",
        location="Test-Location-1",
        server_ip="127.0.0.1",
        server_port=8888
    )

    print(f"设备信息:")
    print(f"  - 设备ID: {client.device_id}")
    print(f"  - 设备名称: {client.device_name}")
    print(f"  - 设备位置: {client.location}")
    print(f"  - 服务器: {client.server_ip}:{client.server_port}")
    print(f"  - 心跳间隔: {client.heartbeat_interval}秒")
    print()

    # 启动客户端
    client.start()

if __name__ == '__main__':
    main()
