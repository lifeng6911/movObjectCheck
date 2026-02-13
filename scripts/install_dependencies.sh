#!/bin/bash

echo "=== 移动物体检测系统 - 依赖安装脚本 ==="
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用 sudo 运行此脚本"
    exit 1
fi

echo "步骤 1/5: 更新系统包列表..."
apt-get update

echo ""
echo "步骤 2/5: 安装编译工具和基础依赖..."
apt-get install -y \
    build-essential \
    cmake \
    git \
    pkg-config \
    wget

echo ""
echo "步骤 3/5: 安装 OpenCV 依赖..."
apt-get install -y \
    libopencv-dev \
    python3-opencv \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    gfortran \
    openexr \
    libatlas-base-dev \
    libtbb2 \
    libtbb-dev \
    libdc1394-22-dev

echo ""
echo "步骤 4/5: 安装 Python 依赖（用于服务器端）..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-dev

pip3 install --upgrade pip
pip3 install opencv-python numpy

echo ""
echo "步骤 5/5: 配置摄像头权限..."
# 将当前用户添加到 video 组
if [ -n "$SUDO_USER" ]; then
    usermod -a -G video $SUDO_USER
    echo "用户 $SUDO_USER 已添加到 video 组"
fi

echo ""
echo "=== 依赖安装完成 ==="
echo ""
echo "注意事项："
echo "1. 如果这是首次安装，请重新登录以使组权限生效"
echo "2. 确保摄像头已正确连接"
echo "3. 可以使用 'ls /dev/video*' 检查摄像头设备"
echo ""
echo "OpenCV 版本信息："
pkg-config --modversion opencv4 2>/dev/null || pkg-config --modversion opencv 2>/dev/null || echo "无法检测 OpenCV 版本"
echo ""
