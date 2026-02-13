# 详细部署指南

本文档提供移动物体检测系统的详细部署步骤。

## 目录

1. [树莓派系统准备](#树莓派系统准备)
2. [4G模块配置](#4g模块配置)
3. [摄像头配置](#摄像头配置)
4. [软件部署](#软件部署)
5. [服务器部署](#服务器部署)
6. [网络配置](#网络配置)

## 树莓派系统准备

### 1. 安装操作系统

推荐使用 Raspberry Pi OS Lite（无桌面版本，节省资源）

```bash
# 下载镜像
# https://www.raspberrypi.org/software/operating-systems/

# 使用 Raspberry Pi Imager 烧录到SD卡
```

### 2. 启用SSH

在SD卡boot分区创建空文件 `ssh`：

```bash
touch /boot/ssh
```

### 3. 配置WiFi（可选）

在boot分区创建 `wpa_supplicant.conf`：

```
country=CN
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="你的WiFi名称"
    psk="你的WiFi密码"
    key_mgmt=WPA-PSK
}
```

### 4. 首次启动配置

```bash
# SSH连接到树莓派
ssh pi@raspberrypi.local
# 默认密码：raspberry

# 修改密码
passwd

# 更新系统
sudo apt-get update
sudo apt-get upgrade -y

# 配置时区
sudo raspi-config
# 选择 Localisation Options -> Timezone -> Asia -> Shanghai
```

## 4G模块配置

### 支持的4G模块

- 华为 ME909s
- 移远 EC20
- SIMCom SIM7600
- 其他支持PPP拨号的4G模块

### 配置步骤

#### 1. 硬件连接

将4G模块通过USB连接到树莓派

#### 2. 安装PPP工具

```bash
sudo apt-get install ppp
```

#### 3. 配置拨号脚本

创建 `/etc/ppp/peers/gprs`：

```bash
sudo nano /etc/ppp/peers/gprs
```

内容：

```
# 串口设备（根据实际情况修改）
/dev/ttyUSB0
115200

# 运营商APN（根据实际情况修改）
# 中国移动：cmnet
# 中国联通：3gnet
# 中国电信：ctnet
connect "/usr/sbin/chat -v -f /etc/ppp/chat-connect"

# 其他选项
noauth
defaultroute
usepeerdns
persist
noipdefault
```

创建 `/etc/ppp/chat-connect`：

```bash
sudo nano /etc/ppp/chat-connect
```

内容：

```
TIMEOUT 15
ABORT "BUSY"
ABORT "NO CARRIER"
ABORT "ERROR"
"" AT
OK ATE0
OK ATI
OK AT+CGDCONT=1,"IP","cmnet"
OK ATDT*99#
CONNECT
```

#### 4. 启动4G连接

```bash
# 手动拨号
sudo pppd call gprs

# 检查连接
ifconfig ppp0

# 测试网络
ping -I ppp0 8.8.8.8
```

#### 5. 开机自动连接

编辑 `/etc/rc.local`，在 `exit 0` 前添加：

```bash
sudo pppd call gprs &
```

## 摄像头配置

### USB摄像头

```bash
# 检测摄像头
ls /dev/video*

# 查看摄像头信息
v4l2-ctl --list-devices

# 测试摄像头
sudo apt-get install fswebcam
fswebcam test.jpg
```

### 树莓派官方摄像头

```bash
# 启用摄像头
sudo raspi-config
# 选择 Interface Options -> Camera -> Enable

# 重启
sudo reboot

# 测试
raspistill -o test.jpg
```

**注意**：如果使用官方摄像头，需要修改代码使用 `raspicam` 库而不是 OpenCV 的 VideoCapture。

## 软件部署

### 方式1：自动部署（推荐）

```bash
# 1. 克隆代码
git clone https://github.com/your-username/movObjectCheck.git
cd movObjectCheck

# 2. 安装依赖
chmod +x scripts/*.sh
sudo ./scripts/install_dependencies.sh

# 3. 编译
./scripts/build.sh

# 4. 配置
nano config/config.ini
# 修改 server_ip 为实际服务器地址

# 5. 测试运行
./build/motion_detector config/config.ini

# 6. 部署为服务
sudo ./scripts/deploy.sh
sudo systemctl start motion-detector
```

### 方式2：手动部署

```bash
# 1. 安装依赖
sudo apt-get update
sudo apt-get install -y build-essential cmake git pkg-config
sudo apt-get install -y libopencv-dev

# 2. 克隆代码
git clone https://github.com/your-username/movObjectCheck.git
cd movObjectCheck

# 3. 编译
mkdir build && cd build
cmake ..
make -j4

# 4. 运行
./motion_detector ../config/config.ini
```

## 服务器部署

### Linux服务器

```bash
# 1. 安装Python和依赖
sudo apt-get install python3 python3-pip
pip3 install opencv-python numpy

# 2. 上传代码
scp -r server/ user@server:/opt/motion-server/

# 3. 配置
cd /opt/motion-server
nano config/server_config.ini

# 4. 运行
python3 server.py

# 5. 配置systemd服务
sudo nano /etc/systemd/system/motion-server.service
```

服务文件内容：

```ini
[Unit]
Description=Motion Detection Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/opt/motion-server
ExecStart=/usr/bin/python3 server.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start motion-server
sudo systemctl enable motion-server
```

### Windows服务器

```bash
# 1. 安装Python
# 从 https://www.python.org/ 下载安装

# 2. 安装依赖
pip install opencv-python numpy

# 3. 运行
python server.py
```

### 云服务器部署

#### 阿里云/腾讯云

1. 购买云服务器（最低配置即可）
2. 配置安全组，开放8888端口
3. 按照Linux服务器步骤部署

#### 使用Docker部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libopencv-dev \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/ .
COPY config/server_config.ini config/

EXPOSE 8888

CMD ["python", "server.py"]
```

构建和运行：

```bash
docker build -t motion-server .
docker run -d -p 8888:8888 -v $(pwd)/received_images:/app/received_images motion-server
```

## 网络配置

### 防火墙配置

#### 服务器端（Linux）

```bash
# UFW防火墙
sudo ufw allow 8888/tcp

# iptables
sudo iptables -A INPUT -p tcp --dport 8888 -j ACCEPT
```

#### 云服务器

在云服务商控制台配置安全组规则：
- 协议：TCP
- 端口：8888
- 来源：0.0.0.0/0（或指定树莓派IP）

### 内网穿透（可选）

如果服务器在内网，可使用内网穿透工具：

#### 使用frp

服务器端：

```bash
# 下载frp
wget https://github.com/fatedier/frp/releases/download/v0.51.0/frp_0.51.0_linux_amd64.tar.gz
tar -xzf frp_0.51.0_linux_amd64.tar.gz

# 配置 frps.ini
[common]
bind_port = 7000

# 启动
./frps -c frps.ini
```

客户端（树莓派）：

```bash
# 配置 frpc.ini
[common]
server_addr = 公网服务器IP
server_port = 7000

[motion]
type = tcp
local_ip = 127.0.0.1
local_port = 8888
remote_port = 8888

# 启动
./frpc -c frpc.ini
```

## 性能优化

### 1. 降低功耗

```bash
# 禁用HDMI
sudo /opt/vc/bin/tvservice -o

# 禁用蓝牙
sudo systemctl disable bluetooth

# 禁用WiFi（使用4G时）
sudo ifconfig wlan0 down
```

### 2. 提高性能

```bash
# 超频（谨慎使用）
sudo nano /boot/config.txt
# 添加：
# over_voltage=2
# arm_freq=1750
```

### 3. 自动重启

添加到 crontab：

```bash
crontab -e
# 添加：每天凌晨3点重启
0 3 * * * sudo reboot
```

## 验证部署

### 1. 检查服务状态

```bash
# 树莓派端
sudo systemctl status motion-detector

# 服务器端
sudo systemctl status motion-server
```

### 2. 查看日志

```bash
# 树莓派端
tail -f /opt/motion_detector/logs/output.log

# 服务器端
journalctl -u motion-server -f
```

### 3. 测试功能

1. 在摄像头前挥手
2. 观察树莓派日志是否显示"检测到移动物体"
3. 检查服务器是否接收到图像

## 常见问题

见 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
