#!/bin/bash

echo "=========================================="
echo "心跳机制测试脚本"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取项目根目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# 检查是否已编译
if [ ! -f "build/motion_detector" ]; then
    echo -e "${RED}错误: 未找到编译后的程序${NC}"
    echo "请先运行: ./scripts/build.sh"
    exit 1
fi

# 检查配置文件
if [ ! -f "config/config.ini" ]; then
    echo -e "${RED}错误: 未找到配置文件${NC}"
    exit 1
fi

echo "测试步骤："
echo "1. 启动服务器"
echo "2. 启动客户端（模拟设备）"
echo "3. 观察心跳消息"
echo "4. 测试设备离线检测"
echo ""

# 询问是否继续
read -p "是否继续测试? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
fi

echo ""
echo "=========================================="
echo "步骤1: 启动服务器"
echo "=========================================="
echo ""

# 检查Python依赖
python3 -c "import cv2, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}错误: Python依赖未安装${NC}"
    echo "请运行: pip3 install opencv-python numpy"
    exit 1
fi

# 启动服务器（后台运行）
echo "启动服务器..."
python3 server/server.py > /tmp/motion_server.log 2>&1 &
SERVER_PID=$!
echo -e "${GREEN}服务器已启动 (PID: $SERVER_PID)${NC}"
echo "日志文件: /tmp/motion_server.log"

# 等待服务器启动
sleep 2

# 检查服务器是否正常运行
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo -e "${RED}服务器启动失败${NC}"
    cat /tmp/motion_server.log
    exit 1
fi

echo ""
echo "=========================================="
echo "步骤2: 创建测试配置"
echo "=========================================="
echo ""

# 创建测试配置文件
cat > config/test_device1.ini << EOF
# 测试设备1配置
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
EOF

echo -e "${GREEN}测试配置已创建: config/test_device1.ini${NC}"
echo "  - 设备ID: 101"
echo "  - 设备名称: TestDevice-001"
echo "  - 心跳间隔: 10秒"

echo ""
echo "=========================================="
echo "步骤3: 启动测试客户端"
echo "=========================================="
echo ""

echo "启动客户端（将在30秒后自动停止）..."
timeout 30 ./build/motion_detector config/test_device1.ini > /tmp/motion_client.log 2>&1 &
CLIENT_PID=$!

echo -e "${GREEN}客户端已启动 (PID: $CLIENT_PID)${NC}"
echo "日志文件: /tmp/motion_client.log"

echo ""
echo "观察心跳消息（10秒）..."
sleep 10

echo ""
echo "=========================================="
echo "步骤4: 检查服务器日志"
echo "=========================================="
echo ""

echo "服务器日志（最后20行）:"
echo "----------------------------------------"
tail -n 20 /tmp/motion_server.log
echo "----------------------------------------"

echo ""
echo "客户端日志（最后20行）:"
echo "----------------------------------------"
tail -n 20 /tmp/motion_client.log
echo "----------------------------------------"

echo ""
echo "=========================================="
echo "步骤5: 测试设备离线检测"
echo "=========================================="
echo ""

echo "停止客户端以模拟设备离线..."
kill $CLIENT_PID 2>/dev/null
wait $CLIENT_PID 2>/dev/null

echo -e "${YELLOW}客户端已停止${NC}"
echo ""
echo "等待服务器检测到设备离线（需要等待心跳超时）..."
echo "心跳超时设置: 90秒"
echo "检查间隔: 10秒"
echo ""

# 等待一段时间让服务器检测到离线
for i in {1..12}; do
    echo -n "."
    sleep 5
done
echo ""

echo ""
echo "=========================================="
echo "步骤6: 查看最终状态"
echo "=========================================="
echo ""

echo "服务器日志（最后30行）:"
echo "----------------------------------------"
tail -n 30 /tmp/motion_server.log
echo "----------------------------------------"

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="
echo ""

# 清理
echo "清理测试环境..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

echo -e "${GREEN}服务器已停止${NC}"
echo ""

# 测试结果分析
echo "=========================================="
echo "测试结果分析"
echo "=========================================="
echo ""

# 检查关键日志
if grep -q "设备注册成功" /tmp/motion_client.log; then
    echo -e "${GREEN}✓ 设备注册成功${NC}"
else
    echo -e "${RED}✗ 设备注册失败${NC}"
fi

if grep -q "心跳线程启动" /tmp/motion_client.log; then
    echo -e "${GREEN}✓ 心跳线程启动${NC}"
else
    echo -e "${RED}✗ 心跳线程未启动${NC}"
fi

if grep -q "新设备注册.*TestDevice-001" /tmp/motion_server.log; then
    echo -e "${GREEN}✓ 服务器接收到设备注册${NC}"
else
    echo -e "${RED}✗ 服务器未接收到设备注册${NC}"
fi

if grep -q "检测到设备离线" /tmp/motion_server.log; then
    echo -e "${GREEN}✓ 服务器检测到设备离线${NC}"
else
    echo -e "${YELLOW}⚠ 服务器未检测到设备离线（可能需要更长时间）${NC}"
fi

echo ""
echo "日志文件保存在:"
echo "  - 服务器: /tmp/motion_server.log"
echo "  - 客户端: /tmp/motion_client.log"
echo ""
echo "如需查看完整日志，请使用:"
echo "  cat /tmp/motion_server.log"
echo "  cat /tmp/motion_client.log"
echo ""
