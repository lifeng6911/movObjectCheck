# 移动物体检测系统

基于树莓派的实时移动物体检测系统，当检测到移动物体时通过4G模块将画面发送到服务器。

> **快速开始**：如果您想快速部署系统，请查看 [快速入门指南 (QUICKSTART.md)](QUICKSTART.md)，10分钟即可完成部署和测试。

## 功能特点

- ✅ 实时检测视野内的移动物体
- ✅ 智能过滤光照变化干扰
- ✅ 仅在检测到运动时发送图像，降低传输量和功耗
- ✅ 通过4G网络传输图像到远程服务器
- ✅ 低延迟设计，适合偏僻场景实时监控
- ✅ 心跳机制保持长连接，自动检测设备离线
- ✅ 支持多设备管理，实时显示设备状态
- ✅ 配置文件灵活调整参数
- ✅ 支持多客户端同时连接

## 系统架构

```
树莓派端 (C++)                           服务器端 (Python)
┌──────────────────────┐              ┌──────────────────────┐
│   摄像头采集          │              │   设备注册管理        │
│       ↓              │              │        ↓             │
│  运动检测算法         │              │   心跳监控线程        │
│       ↓              │   4G/网络    │        ↓             │
│  JPEG压缩编码        │  =========>  │   接收图像数据        │
│       ↓              │              │        ↓             │
│  TCP Socket发送      │              │   解码并显示          │
│       ↓              │              │        ↓             │
│  心跳线程(30秒)      │  <========>  │   保存到本地          │
│  自动重连机制         │              │   多线程处理          │
└──────────────────────┘              └──────────────────────┘
```

## 技术方案

### 运动检测算法

采用**帧差法 + 背景建模**的混合方案：

1. **帧差检测**：计算连续帧之间的差异
2. **高斯模糊**：减少噪声干扰
3. **二值化处理**：提取运动区域
4. **轮廓分析**：过滤小面积噪声
5. **光照过滤**：智能识别并过滤光线变化

### 通信协议

采用自定义TCP协议，支持多种消息类型：

#### 消息头结构（8字节）
```c
struct MessageHeader {
    uint8_t type;              // 消息类型
    uint8_t reserved;          // 保留字段
    uint16_t device_id;        // 设备ID（网络字节序）
    uint32_t data_length;      // 数据长度（网络字节序）
}
```

#### 消息类型
- `MSG_REGISTER (0x04)`: 设备注册
- `MSG_REGISTER_ACK (0x05)`: 注册响应
- `MSG_HEARTBEAT (0x01)`: 心跳消息
- `MSG_HEARTBEAT_ACK (0x02)`: 心跳响应
- `MSG_IMAGE_DATA (0x03)`: 图像数据

### 心跳机制

解决边缘设备长时间不通讯导致的连接中断问题：

- **客户端**：每30秒发送心跳消息
- **服务器**：监控设备状态，90秒无心跳标记为离线
- **自动重连**：心跳失败时自动尝试重新连接
- **设备管理**：支持多设备注册，显示设备编号、名称、位置
- **离线告警**：实时显示离线设备信息

详细说明请参考 [docs/HEARTBEAT.md](docs/HEARTBEAT.md)

## 环境要求

### 树莓派端

- 硬件：树莓派 3B+ 或更高版本
- 系统：Raspbian / Raspberry Pi OS
- 摄像头：USB摄像头或树莓派官方摄像头
- 网络：4G模块或WiFi/以太网

### 服务器端

- 系统：Linux / Windows / macOS
- Python：3.6 或更高版本

## 快速开始

### 1. 从GitHub下载代码

```bash
# 克隆仓库
git clone https://github.com/your-username/movObjectCheck.git
cd movObjectCheck
```

### 2. 树莓派端部署

#### 2.1 安装依赖

```bash
# 赋予脚本执行权限
chmod +x scripts/*.sh

# 安装系统依赖（需要sudo权限）
sudo ./scripts/install_dependencies.sh
```

安装过程会自动完成：
- 更新系统软件包
- 安装OpenCV及其依赖
- 安装CMake和编译工具
- 配置摄像头权限

#### 2.2 配置参数

编辑配置文件 `config/config.ini`：

```ini
# 设备信息（每台设备必须唯一）
device_id = 1
device_name = RaspberryPi-001
device_location = Building-A-Floor-1

# 服务器地址
server_ip = 192.168.1.100
server_port = 8888

# 心跳配置
heartbeat_interval = 30    # 心跳间隔（秒）

# 运动检测参数
motion_threshold = 25      # 运动检测灵敏度
min_area = 500            # 最小运动区域
lighting_threshold = 15   # 光照过滤阈值

# 摄像头参数
camera_index = 0          # 摄像头索引
frame_width = 640         # 图像宽度
frame_height = 480        # 图像高度
fps = 15                  # 帧率

# 传输参数
jpeg_quality = 80         # JPEG压缩质量(1-100)
```

#### 2.3 编译程序

```bash
./scripts/build.sh
```

编译成功后，可执行文件位于 `build/motion_detector`

#### 2.4 测试运行

```bash
# 直接运行测试
./build/motion_detector config/config.ini
```

正常运行时会显示：
```
摄像头初始化成功
连接到服务器成功
设备注册成功
心跳线程已启动
开始检测运动...
```

#### 2.5 部署为系统服务（推荐）

```bash
# 部署为systemd服务，开机自启
sudo ./scripts/deploy.sh

# 启动服务
sudo systemctl start motion-detector

# 查看运行状态
sudo systemctl status motion-detector

# 查看日志
tail -f /opt/motion_detector/logs/output.log

# 停止服务
sudo systemctl stop motion-detector

# 禁用开机自启
sudo systemctl disable motion-detector
```

### 3. 服务器端部署

#### 3.1 安装Python依赖

```bash
cd server
pip3 install -r requirements.txt
```

#### 3.2 配置服务器

编辑配置文件 `config/server_config.ini`：

```ini
[server]
host = 0.0.0.0              # 监听所有网络接口
port = 8888                 # 监听端口
save_images = true          # 是否保存图像
save_dir = received_images  # 图像保存目录
display_images = true       # 是否显示图像窗口
max_clients = 10            # 最大客户端连接数

# 心跳配置
heartbeat_timeout = 90      # 心跳超时时间（秒），建议为客户端间隔的3倍
check_interval = 10         # 设备状态检查间隔（秒）
```

#### 3.3 启动服务器

```bash
# 方式1：直接运行
cd server
python3 server.py

# 方式2：指定配置文件
python3 server.py ../config/server_config.ini

# 方式3：后台运行
nohup python3 server.py > server.log 2>&1 &
```

服务器启动后会显示：
```
服务器启动在 0.0.0.0:8888
等待客户端连接...
心跳超时: 90秒
设备检查间隔: 10秒
```

当设备连接时会显示：
```
新客户端连接: ('192.168.1.101', 54321)
[设备1] 新设备注册: RaspberryPi-001 (Building-A-Floor-1)

============================================================
设备状态列表:
------------------------------------------------------------
✓ 设备1: RaspberryPi-001
  位置: Building-A-Floor-1
  状态: 在线
  最后心跳: 0秒前
  接收图像: 0张
------------------------------------------------------------
总计: 1台设备 (在线: 1, 离线: 0)
============================================================
```

#### 3.4 使用systemd管理（Linux服务器）

创建服务文件 `/etc/systemd/system/motion-server.service`：

```ini
[Unit]
Description=Motion Detection Server
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/movObjectCheck/server
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

## 多设备部署

系统支持多个树莓派设备同时连接到一个服务器。

### 配置多个设备

为每台设备创建独立的配置文件，确保 `device_id` 唯一：

**设备1配置** (`config/device1.ini`):
```ini
device_id = 1
device_name = RaspberryPi-001
device_location = Building-A-Floor-1
server_ip = 192.168.1.100
```

**设备2配置** (`config/device2.ini`):
```ini
device_id = 2
device_name = RaspberryPi-002
device_location = Building-A-Floor-2
server_ip = 192.168.1.100
```

**设备3配置** (`config/device3.ini`):
```ini
device_id = 3
device_name = RaspberryPi-003
device_location = Building-B-Entrance
server_ip = 192.168.1.100
```

### 启动多个设备

```bash
# 在设备1上
./build/motion_detector config/device1.ini

# 在设备2上
./build/motion_detector config/device2.ini

# 在设备3上
./build/motion_detector config/device3.ini
```

服务器会自动管理所有设备，实时显示设备状态。

## 目录结构

```
movObjectCheck/
├── src/                      # 树莓派端源代码
│   ├── main.cpp             # 主程序入口
│   ├── motion_detector.cpp  # 运动检测实现
│   ├── motion_detector.h
│   ├── network_sender.cpp   # 网络传输实现
│   ├── network_sender.h
│   ├── config.cpp           # 配置文件解析
│   ├── config.h
│   └── protocol.h           # 通信协议定义
├── server/                   # 服务器端代码
│   ├── server.py            # Python服务器
│   └── requirements.txt     # Python依赖
├── scripts/                  # 部署脚本
│   ├── install_dependencies.sh  # 依赖安装
│   ├── build.sh                 # 编译脚本
│   ├── deploy.sh                # 部署脚本
│   ├── check_build.sh           # 编译检查
│   ├── mock_client.py           # 模拟客户端（测试用）
│   └── test_heartbeat.py        # 心跳测试脚本
├── config/                   # 配置文件
│   ├── config.ini           # 树莓派端配置
│   └── server_config.ini    # 服务器端配置
├── docs/                     # 文档目录
│   ├── DEPLOYMENT.md        # 详细部署指南
│   ├── CONFIGURATION.md     # 配置说明
│   ├── TROUBLESHOOTING.md   # 故障排除
│   ├── HEARTBEAT.md         # 心跳机制详解
│   └── TESTING.md           # 测试指南
├── CMakeLists.txt           # CMake构建配置
├── README.md                # 本文件
├── LICENSE                  # 开源协议
└── .gitignore              # Git忽略文件
```

## 测试方法

### 1. 快速测试（无需树莓派）

使用Python模拟客户端测试服务器和心跳机制：

```bash
# 启动服务器
cd server
python3 server.py

# 在另一个终端启动模拟客户端
cd scripts
python3 mock_client.py

# 运行自动化测试
python3 test_heartbeat.py
```

### 2. 摄像头测试

```bash
# 检查摄像头设备
ls /dev/video*

# 使用v4l2工具测试
v4l2-ctl --list-devices

# 测试摄像头是否可用
v4l2-ctl --device=/dev/video0 --all
```

### 3. 网络连接测试

```bash
# 在树莓派上测试到服务器的连接
ping <服务器IP>

# 测试端口是否开放
telnet <服务器IP> 8888

# 或使用nc命令
nc -zv <服务器IP> 8888
```

### 4. 完整功能测试

**步骤1：启动服务器**
```bash
cd server
python3 server.py
```

**步骤2：启动树莓派客户端**
```bash
./build/motion_detector config/config.ini
```

**步骤3：测试运动检测**
- 在摄像头前挥手或移动物体
- 观察客户端输出：`检测到运动！发送图像...`
- 观察服务器端是否接收到图像

**步骤4：测试心跳机制**
- 观察客户端每30秒输出：`心跳发送成功`
- 观察服务器每10秒显示设备状态
- 停止客户端，观察服务器是否在90秒后标记设备离线

**步骤5：测试多设备**
- 启动多个客户端（使用不同配置文件）
- 观察服务器显示所有设备状态
- 停止其中一个客户端，观察离线检测

### 5. 性能测试

```bash
# 查看CPU使用率
top

# 查看内存使用
free -h

# 监控网络流量
iftop

# 查看进程详细信息
ps aux | grep motion_detector
```

详细测试指南请参考 [docs/TESTING.md](docs/TESTING.md)

## 参数调优指南

### 运动检测参数

| 参数 | 默认值 | 说明 | 调优建议 |
|------|--------|------|----------|
| motion_threshold | 25 | 帧差阈值 | 环境噪声大时增加，需要更敏感时减小 |
| min_area | 500 | 最小运动区域 | 过滤小物体时增加，检测小物体时减小 |
| lighting_threshold | 15 | 光照变化阈值 | 光线变化频繁时增加 |
| background_update_interval | 30 | 背景更新间隔 | 场景变化快时减小 |

### 传输参数

| 参数 | 默认值 | 说明 | 调优建议 |
|------|--------|------|----------|
| jpeg_quality | 80 | JPEG压缩质量 | 网络带宽小时降低，需要高清晰度时提高 |
| fps | 15 | 采集帧率 | 降低可减少功耗和带宽 |
| frame_width | 640 | 图像宽度 | 根据需求调整 |
| frame_height | 480 | 图像高度 | 根据需求调整 |

## 故障排除

### 问题1：无法打开摄像头

**错误信息**：`无法打开摄像头`

**解决方案**：
```bash
# 检查摄像头设备
ls -l /dev/video*

# 检查用户权限
groups $USER

# 添加到video组
sudo usermod -a -G video $USER

# 重新登录使权限生效
```

### 问题2：连接服务器失败

**错误信息**：`连接到服务器失败`

**解决方案**：
1. 检查服务器IP和端口配置是否正确
2. 确认服务器程序正在运行
3. 检查服务器防火墙设置：
   ```bash
   # Ubuntu/Debian
   sudo ufw allow 8888

   # CentOS/RHEL
   sudo firewall-cmd --add-port=8888/tcp --permanent
   sudo firewall-cmd --reload
   ```
4. 测试网络连通性：
   ```bash
   ping <服务器IP>
   telnet <服务器IP> 8888
   ```

### 问题3：设备频繁离线

**现象**：服务器频繁显示设备离线警告

**可能原因**：
- 网络不稳定
- 心跳间隔设置过大
- 心跳超时设置过小

**解决方案**：
```ini
# 树莓派端 config.ini：减小心跳间隔
heartbeat_interval = 20

# 服务器端 server_config.ini：增加超时时间
heartbeat_timeout = 120
```

### 问题4：心跳失败导致重连

**错误信息**：`心跳响应超时` 或 `心跳失败，尝试重新连接...`

**解决方案**：
1. 检查网络连接稳定性
2. 检查服务器是否正常运行
3. 检查防火墙是否阻止连接
4. 增加连接超时时间：
   ```ini
   connection_timeout = 10000
   ```

### 问题5：设备ID冲突

**现象**：服务器显示设备重新连接，但设备信息不匹配

**解决方案**：
确保每台设备的 `device_id` 唯一，不要重复。检查所有配置文件。

### 问题6：误检测过多

**现象**：没有明显运动也频繁发送图像

**解决方案**：
```ini
# 增加运动检测阈值
motion_threshold = 30

# 增加最小运动区域
min_area = 800

# 调整光照过滤阈值
lighting_threshold = 20
```

### 问题7：漏检测

**现象**：有运动但未检测到

**解决方案**：
```ini
# 减小运动检测阈值
motion_threshold = 20

# 减小最小运动区域
min_area = 300
```
同时检查：
- 摄像头位置和角度是否合适
- 光线条件是否充足
- 运动物体是否在视野范围内

### 问题8：编译失败

**错误信息**：`OpenCV not found` 或编译错误

**解决方案**：
```bash
# 重新安装依赖
sudo ./scripts/install_dependencies.sh

# 检查OpenCV安装
pkg-config --modversion opencv4

# 清理并重新编译
rm -rf build
./scripts/build.sh
```

### 问题9：图像传输失败

**错误信息**：`图像发送失败`

**解决方案**：
1. 检查网络连接
2. 检查图像大小是否过大：
   ```ini
   # 降低图像分辨率
   frame_width = 320
   frame_height = 240

   # 降低JPEG质量
   jpeg_quality = 60
   ```

### 问题10：服务器无法显示图像

**错误信息**：`cv2.imshow error` 或窗口无法打开

**解决方案**：
```ini
# 在server_config.ini中禁用图像显示
display_images = false
```
或安装X11支持（Linux服务器）：
```bash
sudo apt-get install python3-opencv
```

更多故障排除信息请参考 [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## 性能指标

- **检测延迟**：< 100ms
- **CPU占用**：15-25%（树莓派4B）
- **内存占用**：< 50MB
- **网络带宽**：10-50KB/次（取决于JPEG质量）
- **心跳开销**：每次仅8字节，30秒间隔时约0.27字节/秒
- **功耗**：约3-5W（不含4G模块）

## 文档导航

- [快速入门指南 (QUICKSTART.md)](QUICKSTART.md) - 10分钟快速部署
- [心跳机制详解 (docs/HEARTBEAT.md)](docs/HEARTBEAT.md) - 设备管理和离线检测
- [配置参数说明 (docs/CONFIGURATION.md)](docs/CONFIGURATION.md) - 参数调优指南
- [测试指南 (docs/TESTING.md)](docs/TESTING.md) - 完整测试流程
- [部署指南 (docs/DEPLOYMENT.md)](docs/DEPLOYMENT.md) - 详细部署步骤
- [故障排除 (docs/TROUBLESHOOTING.md)](docs/TROUBLESHOOTING.md) - 常见问题解决

## 应用场景

- 偏远地区野生动物监控
- 仓库、工地安全监控
- 农田作物保护
- 停车场车辆监控
- 家庭安防系统
- 任何需要低功耗、低带宽的运动检测场景

## 系统特点

### 低功耗设计
- 仅在检测到运动时传输数据
- 可配置的检测灵敏度和帧率
- 适合太阳能供电的偏远场景

### 智能检测
- 帧差法结合背景建模
- 自动过滤光照变化
- 可调节的检测参数

### 可靠连接
- 心跳机制保持长连接
- 自动重连机制
- TCP保活机制
- 多设备管理

### 易于部署
- 一键安装脚本
- 配置文件管理
- systemd服务支持
- 详细的文档和示例

## 技术栈

**树莓派端**：
- C++17
- OpenCV 4.x
- CMake 3.10+
- POSIX Threads

**服务器端**：
- Python 3.6+
- OpenCV (cv2)
- ConfigParser
- Socket编程

## 反馈问题

如果遇到问题或有改进建议，请通过以下方式反馈：

1. **GitHub Issues**：https://github.com/your-username/movObjectCheck/issues
2. **提交Issue时请包含**：
   - 系统版本信息（`uname -a`）
   - Python版本（`python3 --version`）
   - OpenCV版本（`pkg-config --modversion opencv4`）
   - 错误日志（完整的错误输出）
   - 配置文件内容
   - 复现步骤

## 开源协议

本项目采用 MIT 协议开源，详见 [LICENSE](LICENSE) 文件。

## 贡献指南

欢迎提交 Pull Request 或 Issue！详见 [CONTRIBUTING.md](CONTRIBUTING.md)

贡献流程：
1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -am 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 Pull Request

## 路线图

- [ ] 添加Web管理界面
- [ ] 支持RTSP视频流
- [ ] 添加邮件/短信告警
- [ ] 支持AI目标识别（人、车、动物分类）
- [ ] 添加录像功能
- [ ] 支持云存储（阿里云OSS、AWS S3）
- [ ] 移动端App

## 致谢

- [OpenCV](https://opencv.org/) - 计算机视觉库
- [树莓派基金会](https://www.raspberrypi.org/) - 硬件平台
- 所有贡献者和使用者

## Star History

如果这个项目对您有帮助，请给我们一个 Star ⭐

---

**注意**：本系统设计用于合法的监控场景，使用时请遵守当地法律法规，尊重他人隐私。
