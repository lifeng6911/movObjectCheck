#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import struct
import cv2
import numpy as np
import configparser
import os
import sys
from datetime import datetime
import threading

class ImageServer:
    def __init__(self, config_file='config/server_config.ini'):
        self.config = self.load_config(config_file)
        self.server_socket = None
        self.running = False
        self.save_images = self.config.getboolean('server', 'save_images', fallback=True)
        self.save_dir = self.config.get('server', 'save_dir', fallback='received_images')

        if self.save_images and not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def load_config(self, config_file):
        config = configparser.ConfigParser()

        # 默认配置
        config['server'] = {
            'host': '0.0.0.0',
            'port': '8888',
            'save_images': 'true',
            'save_dir': 'received_images',
            'display_images': 'true',
            'max_clients': '5'
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
        try:
            while self.running:
                # 接收数据大小（4字节）
                size_data = self.recv_all(client_socket, 4)
                if not size_data:
                    break

                data_size = struct.unpack('!I', size_data)[0]
                print(f"[{client_address}] 准备接收图像，大小: {data_size} 字节")

                # 接收图像数据
                image_data = self.recv_all(client_socket, data_size)
                if not image_data:
                    break

                # 解码图像
                nparr = np.frombuffer(image_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if frame is not None:
                    print(f"[{client_address}] 成功接收图像: {frame.shape}")
                    self.process_frame(frame, client_address)
                else:
                    print(f"[{client_address}] 图像解码失败")

        except Exception as e:
            print(f"[{client_address}] 处理客户端时出错: {e}")

        finally:
            client_socket.close()
            print(f"[{client_address}] 客户端断开连接")

    def recv_all(self, sock, size):
        """接收指定大小的数据"""
        data = b''
        while len(data) < size:
            packet = sock.recv(size - len(data))
            if not packet:
                return None
            data += packet
        return data

    def process_frame(self, frame, client_address):
        """处理接收到的图像"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        # 保存图像
        if self.save_images:
            filename = f"{self.save_dir}/motion_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(f"图像已保存: {filename}")

        # 显示图像
        if self.config.getboolean('server', 'display_images', fallback=True):
            cv2.imshow(f'Motion Detection - {client_address[0]}', frame)
            cv2.waitKey(1)

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
    finally:
        server.stop()

if __name__ == '__main__':
    main()
