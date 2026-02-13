# 快速入门指南

本指南帮助您在10分钟内完成系统的下载、编译、测试和部署。

## 前提条件

- 树莓派 3B+ 或更高版本（已安装 Raspberry Pi OS）
- USB摄像头或树莓派官方摄像头
- 服务器（Linux/Windows/macOS，已安装 Python 3.6+）
- 树莓派和服务器在同一网络或通过4G模块连接

## 第一步：下载代码

```bash
# 克隆仓库
git clone https://github.com/your-username/movObjectCheck.git
cd movObjectCheck
```

## 第二步：服务器端设置（5分钟）

### 1. 安装Python依赖

```bash
cd server
pip3 install -r requirements.txt
```

### 2. 配置服务器

编辑 `config/server_config.ini`，通常默认配置即可使用：

```ini
[server]
host = 0.0.0.0
port = 8888
heartbeat_timeout = 90
check_interval = 10
```

### 3. 启动服务器

```bash
python3 server.py
```

看到以下输出表示服务器启动成功：
```
服务器启动在 0.0.0.0:8888
等待客户端连接...
心跳超时: 90秒
设备检查间隔: 10秒
```

## 第三步：树莓派端设置（5分钟）

### 1. 安装依赖

```bash
# 赋予脚本执行权限
chmod +x scripts/*.sh

# 安装系统依赖（需要5-10分钟）
sudo ./scripts/install_dependencies.sh
```

### 2. 配置设备

编辑 `config/config.ini`，修改以下关键参数：

```ini
# 设备信息（必须修改）
device_id = 1
device_name = RaspberryPi-001
device_location = Building-A-Floor-1

# 服务器地址（必须修改为实际服务器IP）
server_ip = 192.168.1.100
server_port = 8888

# 其他参数通常使用默认值即可
```

### 3. 编译程序

```bash
./scripts/build.sh
```

编译成功后会显示：
```
编译完成！可执行文件位于: build/motion_detector
```

### 4. 测试运行

```bash
./build/motion_detector config/config.ini
```

看到以下输出表示运行成功：
```
摄像头初始化成功
连接到服务器成功
设备注册成功
心跳线程已启动
开始检测运动...
```

### 5. 测试运动检测

在摄像头前挥手，应该看到：
```
检测到运动！发送图像...
图像发送成功
```

同时服务器端会显示：
```
[设备1] 接收到图像数据 (12345 字节)
图像已保存: received_images/device_1_20260213_103045.jpg
```

## 第四步：部署为系统服务（可选）

如果测试成功，可以将程序部署为系统服务，实现开机自启：

```bash
sudo ./scripts/deploy.sh
sudo systemctl start motion-detector
sudo systemctl enable motion-detector
```

查看服务状态：
```bash
sudo systemctl status motion-detector
```

查看日志：
```bash
tail -f /opt/motion_detector/logs/output.log
```

## 验证心跳机制

### 1. 观察正常心跳

客户端每30秒会输出：
```
心跳发送成功
```

服务器每10秒会显示设备状态：
```
============================================================
设备状态列表:
------------------------------------------------------------
✓ 设备1: RaspberryPi-001
  位置: Building-A-Floor-1
  状态: 在线
  最后心跳: 5秒前
  接收图像: 3张
------------------------------------------------------------
总计: 1台设备 (在线: 1, 离线: 0)
============================================================
```

### 2. 测试离线检测

停止客户端程序（Ctrl+C），等待90秒后，服务器会显示：
```
============================================================
⚠️  检测到设备离线:
  - 设备1 (RaspberryPi-001)
    位置: Building-A-Floor-1
    最后心跳: 95秒前
============================================================
```

## 多设备部署

如果需要部署多个树莓派设备：

### 1. 为每个设备创建配置文件

```bash
# 复制配置文件
cp config/config.ini config/device1.ini
cp config/config.ini config/device2.ini
cp config/config.ini config/device3.ini
```

### 2. 修改每个配置文件

确保每个设备的 `device_id`、`device_name` 和 `device_location` 都不同：

**device1.ini**:
```ini
device_id = 1
device_name = RaspberryPi-001
device_location = Building-A-Floor-1
```

**device2.ini**:
```ini
device_id = 2
device_name = RaspberryPi-002
device_location = Building-A-Floor-2
```

**device3.ini**:
```ini
device_id = 3
device_name = RaspberryPi-003
device_location = Building-B-Entrance
```

### 3. 在各设备上启动

```bash
# 设备1
./build/motion_detector config/device1.ini

# 设备2
./build/motion_detector config/device2.ini

# 设备3
./build/motion_detector config/device3.ini
```

服务器会自动管理所有设备并显示状态。

## 常见问题快速解决

### 无法打开摄像头

```bash
# 检查摄像头
ls /dev/video*

# 添加用户权限
sudo usermod -a -G video $USER
# 重新登录
```

### 连接服务器失败

```bash
# 测试网络连通性
ping <服务器IP>

# 检查防火墙
sudo ufw allow 8888
```

### 编译失败

```bash
# 重新安装依赖
sudo ./scripts/install_dependencies.sh

# 清理并重新编译
rm -rf build
./scripts/build.sh
```

## 下一步

- 阅读 [README.md](README.md) 了解完整功能
- 查看 [docs/CONFIGURATION.md](docs/CONFIGURATION.md) 学习参数调优
- 参考 [docs/HEARTBEAT.md](docs/HEARTBEAT.md) 深入了解心跳机制
- 查阅 [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) 解决更多问题

## 获取帮助

如果遇到问题：

1. 查看 [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
2. 提交 Issue：https://github.com/your-username/movObjectCheck/issues
3. 包含以下信息：
   - 系统版本
   - 错误日志
   - 配置文件内容
   - 复现步骤

---

恭喜！您已经成功部署了移动物体检测系统。
