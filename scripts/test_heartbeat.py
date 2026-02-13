#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
心跳机制测试脚本
用于验证设备注册、心跳发送和离线检测功能
"""

import subprocess
import time
import os
import sys
import signal
import io

# 设置Windows控制台编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def print_header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60 + "\n")

def print_success(text):
    # Windows兼容的符号
    if sys.platform == 'win32':
        print(f"[OK] {text}")
    else:
        print(f"✓ {text}")

def print_error(text):
    # Windows兼容的符号
    if sys.platform == 'win32':
        print(f"[ERROR] {text}")
    else:
        print(f"✗ {text}")

def print_warning(text):
    # Windows兼容的符号
    if sys.platform == 'win32':
        print(f"[WARNING] {text}")
    else:
        print(f"⚠ {text}")

def check_dependencies():
    """检查依赖"""
    print_header("检查依赖")

    # 检查Python模块
    try:
        import cv2
        import numpy
        print_success("Python依赖已安装")
        return True
    except ImportError as e:
        print_error(f"Python依赖缺失: {e}")
        print("请运行: pip install opencv-python numpy")
        return False

def create_test_config():
    """创建测试配置文件"""
    print_header("创建测试配置")

    config_content = """# 测试设备配置
device_id = 101
device_name = TestDevice-001
device_location = Test-Location-1

camera_index = 0
frame_width = 320
frame_height = 240
fps = 10

motion_threshold = 25
min_area = 500
lighting_threshold = 15
background_update_interval = 30

server_ip = 127.0.0.1
server_port = 8888
connection_timeout = 5000

heartbeat_interval = 10

jpeg_quality = 70
max_retry = 3
"""

    config_path = "config/test_device.ini"
    with open(config_path, 'w') as f:
        f.write(config_content)

    print_success(f"测试配置已创建: {config_path}")
    print("  - 设备ID: 101")
    print("  - 设备名称: TestDevice-001")
    print("  - 心跳间隔: 10秒")

    return config_path

def start_server():
    """启动服务器"""
    print_header("启动服务器")

    try:
        # Windows使用不同的方式启动后台进程
        if sys.platform == 'win32':
            server_process = subprocess.Popen(
                ['python', 'server/server.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            server_process = subprocess.Popen(
                ['python3', 'server/server.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

        print_success(f"服务器已启动 (PID: {server_process.pid})")
        time.sleep(3)  # 等待服务器启动

        # 检查服务器是否还在运行
        if server_process.poll() is not None:
            print_error("服务器启动失败")
            stdout, stderr = server_process.communicate()
            print("错误信息:", stderr.decode())
            return None

        return server_process

    except Exception as e:
        print_error(f"启动服务器失败: {e}")
        return None

def run_test():
    """运行测试"""
    print_header("心跳机制测试")

    # 检查依赖
    if not check_dependencies():
        return False

    # 创建测试配置
    config_path = create_test_config()

    # 启动服务器
    server_process = start_server()
    if not server_process:
        return False

    try:
        print_header("测试说明")
        print("本测试将执行以下步骤：")
        print("1. 服务器已启动并监听连接")
        print("2. 手动启动客户端进行测试")
        print("3. 观察心跳消息和设备状态")
        print("4. 停止客户端测试离线检测")
        print()

        print_header("手动测试步骤")
        print("请在另一个终端窗口执行以下命令：")
        print()

        if sys.platform == 'win32':
            print("  # Windows (需要先编译)")
            print("  .\\build\\motion_detector.exe config\\test_device.ini")
        else:
            print("  # Linux/Mac")
            print("  ./build/motion_detector config/test_device.ini")

        print()
        print("观察要点：")
        print("  1. 客户端是否成功连接到服务器")
        print("  2. 设备是否成功注册（显示设备ID、名称、位置）")
        print("  3. 心跳线程是否启动")
        print("  4. 每10秒是否发送心跳")
        print("  5. 服务器是否显示设备状态列表")
        print()

        print_warning("服务器正在运行中...")
        print("按 Ctrl+C 停止服务器")
        print()

        # 保持服务器运行，显示输出
        while True:
            line = server_process.stdout.readline()
            if line:
                print(line.decode().strip())
            time.sleep(0.1)

    except KeyboardInterrupt:
        print()
        print_header("停止测试")

    finally:
        # 清理
        print("正在停止服务器...")
        if sys.platform == 'win32':
            server_process.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            server_process.terminate()

        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()

        print_success("服务器已停止")

    return True

def main():
    """主函数"""
    print_header("心跳机制测试工具")
    print("此工具用于测试设备注册、心跳和离线检测功能")

    # 检查是否在项目根目录
    if not os.path.exists('server/server.py'):
        print_error("请在项目根目录运行此脚本")
        return 1

    # 运行测试
    if run_test():
        print()
        print_header("测试完成")
        print("如果看到以下内容，说明心跳机制工作正常：")
        print("  ✓ 设备注册成功")
        print("  ✓ 心跳线程启动")
        print("  ✓ 定期发送心跳")
        print("  ✓ 服务器显示设备状态")
        print("  ✓ 停止客户端后服务器检测到离线")
        return 0
    else:
        print()
        print_header("测试失败")
        return 1

if __name__ == '__main__':
    sys.exit(main())
