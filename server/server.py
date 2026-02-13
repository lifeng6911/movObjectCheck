#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import struct
import cv2
import numpy as np
import configparser
import os
import sys
from datetime import datetime, timedelta
import threading
import time
from collections import defaultdict

# 消息类型定义
MSG_HEARTBEAT = 0x01
MSG_HEARTBEAT_ACK = 0x02
MSG_IMAGE_DATA = 0x03
MSG_REGISTER = 0x04
MSG_REGISTER_ACK = 0x05

class DeviceInfo:
    """设备信息类"""
    def __init__(self, device_id, device_name, location, address):
        self.device_id = device_id
        self.device_name = device_name
        self.location = location
        self.address = address
        self.last_heartbeat = datetime.now()
        self.connected = True
        self.image_count = 0
        self.register_time = datetime.now()

    def update_heartbeat(self):
        """更新心跳时间"""
        self.last_heartbeat = datetime.now()
        self.connected = True

    def is_alive(self, timeout_seconds):
        """检查设备是否在线"""
        elapsed = (datetime.now() - self.last_heartbeat).total_seconds()
        return elapsed < timeout_seconds

    def get_status(self):
        """获取设备状态信息"""
        elapsed = (datetime.now() - self.last_heartbeat).total_seconds()
        return {
            'device_id': self.device_id,
            'device_name': self.device_name,
            'location': self.location,
            'address': self.address,
            'connected': self.connected,
            'last_heartbeat': self.last_heartbeat.strftime('%Y-%m-%d %H:%M:%S'),
            'elapsed_seconds': int(elapsed),
            'image_count': self.image_count,
            'register_time': self.register_time.strftime('%Y-%m-%d %H:%M:%S')
        }

class ImageServer:
    def __init__(self, config_file='config/server_config.ini'):
        self.config = self.load_config(config_file)
        self.server_socket = None
        self.running = False
        self.save_images = self.config.getboolean('server', 'save_images', fallback=True)
        self.save_dir = self.config.get('server', 'save_dir', fallback='received_images')
        self.heartbeat_timeout = self.config.getint('server', 'heartbeat_timeout', fallback=90)
        self.check_interval = self.config.getint('server', 'check_interval', fallback=10)

        # 设备管理
        self.devices = {}  # device_id -> DeviceInfo
        self.device_lock = threading.Lock()

        if self.save_images and not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

        # 启动设备监控线程
        self.monitor_thread = threading.Thread(target=self.monitor_devices, daemon=True)
        self.monitor_thread.start()

    def load_config(self, config_file):
        config = configparser.ConfigParser()

        # 默认配置
        config['server'] = {
            'host': '0.0.0.0',
            'port': '8888',
            'save_images': 'true',
            'save_dir': 'received_images',
            'display_images': 'true',
            'max_clients': '10',
            'heartbeat_timeout': '90',
            'check_interval': '10'
        }

        if os.path.exists(config_file):
            config.read(config_file, encoding='utf-8')
            print(f"配置文件加载成功: {config_file}")
        else:
            print(f"配置文件不存在，使用默认配置")

        return config

    def start(self):
        host = self.config.get('server', 'host')
        port = self.config.getint('server', 'port')

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((host, port))
            self.server_socket.listen(self.config.getint('server', 'max_clients'))
            self.running = True
            print(f"服务器启动成功，监听 {host}:{port}")
            print(f"心跳超时设置: {self.heartbeat_timeout}秒")
            print(f"设备检查间隔: {self.check_interval}秒")
            print("=" * 60)

            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    print(f"\n新客户端连接: {client_address}")

                    # 为每个客户端创建新线程
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()

                except KeyboardInterrupt:
                    print("\n接收到中断信号，正在关闭服务器...")
                    break
                except Exception as e:
                    if self.running:
                        print(f"接受连接时出错: {e}")

        finally:
            self.stop()

    def handle_client(self, client_socket, client_address):
        """处理单个客户端连接"""
        device_id = None
        try:
            while self.running:
                # 接收消息头（8字节）
                header_data = self.recv_all(client_socket, 8)
                if not header_data:
                    break

                msg_type, reserved, dev_id, data_length = struct.unpack('!BBHI', header_data)
                device_id = dev_id

                # 处理不同类型的消息
                if msg_type == MSG_REGISTER:
                    self.handle_register(client_socket, device_id, data_length, client_address)

                elif msg_type == MSG_HEARTBEAT:
                    self.handle_heartbeat(client_socket, device_id)

                elif msg_type == MSG_IMAGE_DATA:
                    self.handle_image_data(client_socket, device_id, data_length, client_address)

                else:
                    print(f"[设备{device_id}] 未知消息类型: {msg_type}")
                    break

        except Exception as e:
            print(f"[设备{device_id}] 处理客户端时出错: {e}")

        finally:
            client_socket.close()
            if device_id:
                with self.device_lock:
                    if device_id in self.devices:
                        self.devices[device_id].connected = False
                print(f"[设备{device_id}] 客户端断开连接")

    def handle_register(self, client_socket, device_id, data_length, client_address):
        """处理设备注册"""
        # 接收设备信息
        device_data = self.recv_all(client_socket, data_length)
        if not device_data:
            return

        # 解析设备名称和位置
        device_name = device_data[:32].decode('utf-8').strip('\x00')
        location = device_data[32:96].decode('utf-8').strip('\x00')

        # 注册设备
        with self.device_lock:
            if device_id in self.devices:
                # 设备重新连接
                device = self.devices[device_id]
                device.address = client_address
                device.connected = True
                device.update_heartbeat()
                print(f"[设备{device_id}] 重新连接: {device_name} ({location})")
            else:
                # 新设备注册
                device = DeviceInfo(device_id, device_name, location, client_address)
                self.devices[device_id] = device
                print(f"[设备{device_id}] 新设备注册: {device_name} ({location})")

        # 发送注册响应
        ack_header = struct.pack('!BBHI', MSG_REGISTER_ACK, 0, device_id, 0)
        client_socket.send(ack_header)

        # 显示当前在线设备
        self.print_device_status()

    def handle_heartbeat(self, client_socket, device_id):
        """处理心跳消息"""
        with self.device_lock:
            if device_id in self.devices:
                self.devices[device_id].update_heartbeat()
                # print(f"[设备{device_id}] 收到心跳")  # 可选：减少日志输出

        # 发送心跳响应
        ack_header = struct.pack('!BBHI', MSG_HEARTBEAT_ACK, 0, device_id, 0)
        client_socket.send(ack_header)

    def handle_image_data(self, client_socket, device_id, data_length, client_address):
        """处理图像数据"""
        # 接收图像数据
        image_data = self.recv_all(client_socket, data_length)
        if not image_data:
            return

        # 解码图像
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is not None:
            print(f"[设备{device_id}] 成功接收图像: {frame.shape}, 大小: {data_length} 字节")

            # 更新设备信息
            with self.device_lock:
                if device_id in self.devices:
                    self.devices[device_id].image_count += 1
                    self.devices[device_id].update_heartbeat()

            self.process_frame(frame, device_id, client_address)
        else:
            print(f"[设备{device_id}] 图像解码失败")

    def recv_all(self, sock, size):
        """接收指定大小的数据"""
        data = b''
        while len(data) < size:
            packet = sock.recv(size - len(data))
            if not packet:
                return None
            data += packet
        return data

    def process_frame(self, frame, device_id, client_address):
        """处理接收到的图像"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        # 保存图像
        if self.save_images:
            device_dir = f"{self.save_dir}/device_{device_id}"
            if not os.path.exists(device_dir):
                os.makedirs(device_dir)

            filename = f"{device_dir}/motion_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(f"[设备{device_id}] 图像已保存: {filename}")

        # 显示图像
        if self.config.getboolean('server', 'display_images', fallback=True):
            window_name = f'设备{device_id} - {client_address[0]}'
            cv2.imshow(window_name, frame)
            cv2.waitKey(1)

    def monitor_devices(self):
        """监控设备状态"""
        print("设备监控线程启动")

        while self.running:
            time.sleep(self.check_interval)

            with self.device_lock:
                offline_devices = []

                for device_id, device in self.devices.items():
                    if not device.is_alive(self.heartbeat_timeout):
                        if device.connected:
                            device.connected = False
                            offline_devices.append(device_id)

                # 报告离线设备
                if offline_devices:
                    print("\n" + "=" * 60)
                    print("⚠️  检测到设备离线:")
                    for device_id in offline_devices:
                        device = self.devices[device_id]
                        elapsed = (datetime.now() - device.last_heartbeat).total_seconds()
                        print(f"  - 设备{device_id} ({device.device_name})")
                        print(f"    位置: {device.location}")
                        print(f"    最后心跳: {int(elapsed)}秒前")
                    print("=" * 60)

                    # 显示当前设备状态
                    self.print_device_status()

    def print_device_status(self):
        """打印设备状态"""
        with self.device_lock:
            if not self.devices:
                print("\n当前无设备连接")
                return

            print("\n" + "=" * 60)
            print("设备状态列表:")
            print("-" * 60)

            online_count = 0
            offline_count = 0

            for device_id, device in sorted(self.devices.items()):
                status = device.get_status()
                status_icon = "✓" if status['connected'] else "✗"
                status_text = "在线" if status['connected'] else "离线"

                if status['connected']:
                    online_count += 1
                else:
                    offline_count += 1

                print(f"{status_icon} 设备{device_id}: {status['device_name']}")
                print(f"  位置: {status['location']}")
                print(f"  状态: {status_text}")
                print(f"  地址: {status['address']}")
                print(f"  最后心跳: {status['last_heartbeat']} ({status['elapsed_seconds']}秒前)")
                print(f"  接收图像: {status['image_count']}张")
                print(f"  注册时间: {status['register_time']}")
                print("-" * 60)

            print(f"总计: {len(self.devices)}台设备 (在线: {online_count}, 离线: {offline_count})")
            print("=" * 60 + "\n")

    def stop(self):
        """停止服务器"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        cv2.destroyAllWindows()
        print("服务器已关闭")

def main():
    config_file = 'config/server_config.ini'

    if len(sys.argv) > 1:
        config_file = sys.argv[1]

    server = ImageServer(config_file)

    try:
        server.start()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"服务器错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        server.stop()

if __name__ == '__main__':
    main()
