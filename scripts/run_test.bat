@echo off
chcp 65001 >nul
echo ============================================================
echo 心跳机制完整测试
echo ============================================================
echo.

echo 此脚本将：
echo 1. 启动服务器（后台）
echo 2. 等待3秒
echo 3. 启动模拟客户端（前台）
echo 4. 观察心跳消息
echo.

cd /d "%~dp0.."

echo 步骤1: 启动服务器...
start "Motion Server" cmd /c "python server\server.py"

echo 等待服务器启动...
timeout /t 3 /nobreak >nul

echo.
echo 步骤2: 启动模拟客户端...
echo ============================================================
echo.

python scripts\mock_client.py

echo.
echo ============================================================
echo 测试完成
echo ============================================================
pause
