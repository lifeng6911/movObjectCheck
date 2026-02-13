@echo off
chcp 65001 >nul
echo ============================================================
echo 心跳机制测试 - 客户端（模拟设备）
echo ============================================================
echo.

echo 创建测试配置...

cd /d "%~dp0.."

(
echo # 测试设备配置
echo device_id = 101
echo device_name = TestDevice-001
echo device_location = Test-Location-1
echo.
echo camera_index = 0
echo frame_width = 320
echo frame_height = 240
echo fps = 10
echo.
echo motion_threshold = 25
echo min_area = 500
echo lighting_threshold = 15
echo background_update_interval = 30
echo.
echo server_ip = 127.0.0.1
echo server_port = 8888
echo connection_timeout = 5000
echo.
echo heartbeat_interval = 10
echo.
echo jpeg_quality = 70
echo max_retry = 3
) > config\test_device.ini

echo [OK] 测试配置已创建: config\test_device.ini
echo   - 设备ID: 101
echo   - 设备名称: TestDevice-001
echo   - 心跳间隔: 10秒
echo.

echo ============================================================
echo 测试说明
echo ============================================================
echo.
echo 注意: 此测试需要摄像头或修改代码跳过摄像头检查
echo.
echo 如果没有摄像头，请先编译程序并修改代码：
echo   1. 在 src\motion_detector.cpp 的 initialize() 函数中
echo   2. 注释掉摄像头初始化代码
echo   3. 重新编译: scripts\build.sh
echo.
echo 如果已编译且有摄像头，按任意键启动客户端...
pause >nul

echo.
echo 启动客户端...
echo.

if exist build\motion_detector.exe (
    build\motion_detector.exe config\test_device.ini
) else if exist build\motion_detector (
    build\motion_detector config\test_device.ini
) else (
    echo [ERROR] 未找到编译后的程序
    echo 请先运行: scripts\build.sh
    pause
    exit /b 1
)

pause
