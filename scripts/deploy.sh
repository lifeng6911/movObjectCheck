#!/bin/bash

echo "=== 部署移动物体检测系统 ==="
echo ""

# 获取项目根目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# 安装目录
INSTALL_DIR="/opt/motion_detector"
SERVICE_NAME="motion-detector"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用 sudo 运行此脚本"
    exit 1
fi

echo "步骤 1/4: 创建安装目录..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/config"
mkdir -p "$INSTALL_DIR/logs"

echo ""
echo "步骤 2/4: 复制文件..."
if [ -f "build/motion_detector" ]; then
    cp build/motion_detector "$INSTALL_DIR/"
    chmod +x "$INSTALL_DIR/motion_detector"
    echo "已复制可执行文件"
else
    echo "错误: 找不到编译后的可执行文件"
    echo "请先运行 ./scripts/build.sh 编译项目"
    exit 1
fi

# 复制配置文件
if [ -f "config/config.ini" ]; then
    cp config/config.ini "$INSTALL_DIR/config/"
    echo "已复制配置文件"
fi

echo ""
echo "步骤 3/4: 创建 systemd 服务..."
cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=Motion Detection System
After=network.target

[Service]
Type=simple
User=$SUDO_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/motion_detector $INSTALL_DIR/config/config.ini
Restart=on-failure
RestartSec=10
StandardOutput=append:$INSTALL_DIR/logs/output.log
StandardError=append:$INSTALL_DIR/logs/error.log

[Install]
WantedBy=multi-user.target
EOF

echo "已创建 systemd 服务文件"

echo ""
echo "步骤 4/4: 设置权限..."
chown -R $SUDO_USER:$SUDO_USER "$INSTALL_DIR"

echo ""
echo "=== 部署完成 ==="
echo ""
echo "安装位置: $INSTALL_DIR"
echo ""
echo "服务管理命令："
echo "  启动服务: sudo systemctl start ${SERVICE_NAME}"
echo "  停止服务: sudo systemctl stop ${SERVICE_NAME}"
echo "  查看状态: sudo systemctl status ${SERVICE_NAME}"
echo "  开机自启: sudo systemctl enable ${SERVICE_NAME}"
echo "  查看日志: tail -f $INSTALL_DIR/logs/output.log"
echo ""
echo "手动运行："
echo "  cd $INSTALL_DIR"
echo "  ./motion_detector config/config.ini"
echo ""
