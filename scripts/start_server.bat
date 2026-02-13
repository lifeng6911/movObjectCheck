@echo off
chcp 65001 >nul
echo ============================================================
echo 心跳机制测试 - 服务器端
echo ============================================================
echo.

echo 检查Python依赖...
python -c "import cv2, numpy" 2>nul
if errorlevel 1 (
    echo [ERROR] Python依赖未安装
    echo 请运行: pip install opencv-python numpy
    pause
    exit /b 1
)
echo [OK] Python依赖已安装
echo.

echo ============================================================
echo 启动服务器
echo ============================================================
echo.
echo 服务器将监听 0.0.0.0:8888
echo 心跳超时: 90秒
echo 检查间隔: 10秒
echo.
echo 按 Ctrl+C 停止服务器
echo.

cd /d "%~dp0.."
python server\server.py

pause
