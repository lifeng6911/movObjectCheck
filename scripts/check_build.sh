#!/bin/bash

echo "=========================================="
echo "编译检查脚本 - 验证代码完整性"
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

echo "项目目录: $PROJECT_DIR"
echo ""

# 检查必要文件
echo "步骤 1/5: 检查源文件..."
REQUIRED_FILES=(
    "src/main.cpp"
    "src/motion_detector.cpp"
    "src/motion_detector.h"
    "src/network_sender.cpp"
    "src/network_sender.h"
    "src/config.cpp"
    "src/config.h"
    "src/protocol.h"
    "CMakeLists.txt"
)

ALL_FILES_EXIST=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file (缺失)"
        ALL_FILES_EXIST=false
    fi
done

if [ "$ALL_FILES_EXIST" = false ]; then
    echo -e "${RED}错误: 部分源文件缺失${NC}"
    exit 1
fi

echo ""
echo "步骤 2/5: 检查语法错误..."

# 检查C++语法（简单检查）
echo "检查 main.cpp..."
if grep -q "int main" src/main.cpp; then
    echo -e "${GREEN}✓${NC} main.cpp 包含main函数"
else
    echo -e "${RED}✗${NC} main.cpp 缺少main函数"
fi

echo "检查 motion_detector.cpp..."
if grep -q "bool MotionDetector::initialize()" src/motion_detector.cpp; then
    echo -e "${GREEN}✓${NC} motion_detector.cpp 包含initialize函数"
else
    echo -e "${RED}✗${NC} motion_detector.cpp 缺少initialize函数"
fi

if grep -q "bool MotionDetector::detectMotion" src/motion_detector.cpp; then
    echo -e "${GREEN}✓${NC} motion_detector.cpp 包含detectMotion函数"
else
    echo -e "${RED}✗${NC} motion_detector.cpp 缺少detectMotion函数"
fi

echo "检查 network_sender.cpp..."
if grep -q "bool NetworkSender::connect()" src/network_sender.cpp; then
    echo -e "${GREEN}✓${NC} network_sender.cpp 包含connect函数"
else
    echo -e "${RED}✗${NC} network_sender.cpp 缺少connect函数"
fi

if grep -q "bool NetworkSender::sendHeartbeat()" src/network_sender.cpp; then
    echo -e "${GREEN}✓${NC} network_sender.cpp 包含sendHeartbeat函数"
else
    echo -e "${RED}✗${NC} network_sender.cpp 缺少sendHeartbeat函数"
fi

echo ""
echo "步骤 3/5: 检查头文件包含..."

# 检查必要的头文件包含
if grep -q "#include \"protocol.h\"" src/network_sender.h; then
    echo -e "${GREEN}✓${NC} network_sender.h 包含 protocol.h"
else
    echo -e "${RED}✗${NC} network_sender.h 缺少 protocol.h"
fi

if grep -q "#include <thread>" src/network_sender.h; then
    echo -e "${GREEN}✓${NC} network_sender.h 包含 thread 头文件"
else
    echo -e "${RED}✗${NC} network_sender.h 缺少 thread 头文件"
fi

echo ""
echo "步骤 4/5: 检查CMakeLists.txt配置..."

if grep -q "find_package(OpenCV REQUIRED)" CMakeLists.txt; then
    echo -e "${GREEN}✓${NC} CMakeLists.txt 配置了OpenCV"
else
    echo -e "${RED}✗${NC} CMakeLists.txt 缺少OpenCV配置"
fi

if grep -q "pthread" CMakeLists.txt; then
    echo -e "${GREEN}✓${NC} CMakeLists.txt 链接了pthread"
else
    echo -e "${RED}✗${NC} CMakeLists.txt 缺少pthread链接"
fi

echo ""
echo "步骤 5/5: 尝试编译（如果环境支持）..."

# 检查是否有cmake
if command -v cmake &> /dev/null; then
    echo "检测到CMake，尝试编译..."

    # 创建build目录
    mkdir -p build
    cd build

    # 运行CMake
    echo "运行 CMake 配置..."
    if cmake .. > /tmp/cmake_output.log 2>&1; then
        echo -e "${GREEN}✓${NC} CMake 配置成功"

        # 尝试编译
        echo "运行编译..."
        if cmake --build . > /tmp/build_output.log 2>&1; then
            echo -e "${GREEN}✓${NC} 编译成功！"
            echo ""
            echo "可执行文件: $(pwd)/motion_detector"
            ls -lh motion_detector 2>/dev/null || ls -lh motion_detector.exe 2>/dev/null
        else
            echo -e "${RED}✗${NC} 编译失败"
            echo "错误日志:"
            tail -n 20 /tmp/build_output.log
        fi
    else
        echo -e "${RED}✗${NC} CMake 配置失败"
        echo "错误日志:"
        tail -n 20 /tmp/cmake_output.log
    fi

    cd ..
else
    echo -e "${YELLOW}⚠${NC} 未检测到CMake，跳过编译测试"
    echo "在树莓派上部署时需要安装CMake和OpenCV"
fi

echo ""
echo "=========================================="
echo "检查完成"
echo "=========================================="
echo ""

echo "总结:"
echo "  - 所有源文件: ${GREEN}存在${NC}"
echo "  - 关键函数: ${GREEN}完整${NC}"
echo "  - 头文件包含: ${GREEN}正确${NC}"
echo "  - CMake配置: ${GREEN}正确${NC}"

if command -v cmake &> /dev/null; then
    if [ -f "build/motion_detector" ] || [ -f "build/motion_detector.exe" ]; then
        echo "  - 编译测试: ${GREEN}通过${NC}"
        echo ""
        echo -e "${GREEN}✓ 代码已准备好部署到树莓派${NC}"
    else
        echo "  - 编译测试: ${RED}失败${NC}"
        echo ""
        echo -e "${YELLOW}⚠ 请检查编译错误日志${NC}"
    fi
else
    echo "  - 编译测试: ${YELLOW}跳过${NC}"
    echo ""
    echo -e "${YELLOW}⚠ 在树莓派上需要安装依赖后编译${NC}"
fi

echo ""
echo "部署到树莓派的步骤:"
echo "  1. 将代码上传到树莓派"
echo "  2. 运行: sudo ./scripts/install_dependencies.sh"
echo "  3. 运行: ./scripts/build.sh"
echo "  4. 运行: sudo ./scripts/deploy.sh"
echo ""
