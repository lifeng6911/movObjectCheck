#!/bin/bash

echo "=== 编译移动物体检测系统 ==="
echo ""

# 获取脚本所在目录的父目录（项目根目录）
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "项目目录: $PROJECT_DIR"
echo ""

# 创建 build 目录
if [ ! -d "build" ]; then
    mkdir build
    echo "创建 build 目录"
fi

cd build

echo "运行 CMake 配置..."
cmake .. || {
    echo "CMake 配置失败"
    exit 1
}

echo ""
echo "开始编译..."
make -j$(nproc) || {
    echo "编译失败"
    exit 1
}

echo ""
echo "=== 编译成功 ==="
echo ""
echo "可执行文件位置: $PROJECT_DIR/build/motion_detector"
echo ""
echo "运行程序："
echo "  cd $PROJECT_DIR"
echo "  ./build/motion_detector"
echo ""
