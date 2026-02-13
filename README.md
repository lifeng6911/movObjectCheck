# 移动物体检测系统

基于树莓派的实时移动物体检测系统，当检测到移动物体时通过4G模块将画面发送到服务器。

## 功能特点

- ✅ 实时检测视野内的移动物体
- ✅ 智能过滤光照变化干扰
- ✅ 仅在检测到运动时发送图像，降低传输量和功耗
- ✅ 通过4G网络传输图像到远程服务器
- ✅ 低延迟设计，适合偏僻场景实时监控
- ✅ 配置文件灵活调整参数
- ✅ 支持多客户端同时连接

## 系统架构

```
树莓派端 (C++)                    服务器端 (Python)
┌─────────────────┐              ┌──────────────────┐
│   摄像头采集     │              │   接收图像数据    │
│       ↓         │              │        ↓         │
│  运动检测算法    │   4G/网络    │   解码并显示      │
│       ↓         │  =========>  │        ↓         │
│  JPEG压缩编码   │              │   保存到本地      │
│       ↓         │              │                  │
│  TCP Socket发送 │              │   多线程处理      │
└─────────────────┘              └──────────────────┘
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

采用自定义TCP协议：

```
[4字节数据长度][N字节JPEG图像数据]
```

- 数据长度：网络字节序（大端）的32位无符号整数
- 图像数据：JPEG压缩格式，可配置压缩质量

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

#### 2.2 配置参数

编辑配置文件 `config/config.ini`：

```ini
# 修改服务器IP地址为实际服务器地址
server_ip = 192.168.1.100
server_port = 8888

# 根据实际环境调整检测参数
motion_threshold = 25      # 运动检测灵敏度
min_area = 500            # 最小运动区域
lighting_threshold = 15   # 光照过滤阈值
```

#### 2.3 编译程序

```bash
./scripts/build.sh
```

#### 2.4 测试运行

```bash
# 直接运行测试
./build/motion_detector config/config.ini
```

#### 2.5 部署为系统服务（可选）

```bash
# 部署为systemd服务，开机自启
sudo ./scripts/deploy.sh

# 启动服务
sudo systemctl start motion-detector

# 查看运行状态
sudo systemctl status motion-detector

# 查看日志
tail -f /opt/motion_detector/logs/output.log
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
host = 0.0.0.0          # 监听所有网络接口
port = 8888             # 监听端口
save_images = true      # 是否保存图像
save_dir = received_images
display_images = true   # 是否显示图像窗口
```

#### 3.3 启动服务器

```bash
# 方式1：直接运行
python3 server.py

# 方式2：指定配置文件
python3 server.py ../config/server_config.ini

# 方式3：后台运行
nohup python3 server.py > server.log 2>&1 &
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
│   └── config.h
├── server/                   # 服务器端代码
│   ├── server.py            # Python服务器
│   └── requirements.txt     # Python依赖
├── scripts/                  # 部署脚本
│   ├── install_dependencies.sh  # 依赖安装
│   ├── build.sh                 # 编译脚本
│   └── deploy.sh                # 部署脚本
├── config/                   # 配置文件
│   ├── config.ini           # 树莓派端配置
│   └── server_config.ini    # 服务器端配置
├── docs/                     # 文档目录
│   ├── DEPLOYMENT.md        # 详细部署指南
│   ├── CONFIGURATION.md     # 配置说明
│   └── TROUBLESHOOTING.md   # 故障排除
├── CMakeLists.txt           # CMake构建配置
├── README.md                # 本文件
├── LICENSE                  # 开源协议
└── .gitignore              # Git忽略文件
```

## 测试方法

### 1. 摄像头测试

```bash
# 检查摄像头设备
ls /dev/video*

# 使用v4l2工具测试
v4l2-ctl --list-devices
```

### 2. 网络连接测试

```bash
# 在树莓派上测试到服务器的连接
ping <服务器IP>
telnet <服务器IP> 8888
```

### 3. 功能测试

1. 启动服务器端程序
2. 启动树莓派端程序
3. 在摄像头前挥手或移动物体
4. 观察服务器端是否接收到图像

### 4. 性能测试

```bash
# 查看CPU使用率
top

# 查看内存使用
free -h

# 监控网络流量
iftop
```

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

**解决方案**：
```bash
# 检查摄像头设备
ls -l /dev/video*

# 检查用户权限
groups $USER

# 添加到video组
sudo usermod -a -G video $USER
```

### 问题2：连接服务器失败

**解决方案**：
- 检查服务器IP和端口配置
- 确认服务器防火墙允许对应端口
- 测试网络连通性：`ping <服务器IP>`

### 问题3：误检测过多

**解决方案**：
- 增加 `motion_threshold` 值
- 增加 `min_area` 值
- 调整 `lighting_threshold` 过滤光照变化

### 问题4：漏检测

**解决方案**：
- 减小 `motion_threshold` 值
- 减小 `min_area` 值
- 检查摄像头位置和角度

## 性能指标

- **检测延迟**：< 100ms
- **CPU占用**：15-25%（树莓派4B）
- **内存占用**：< 50MB
- **网络带宽**：10-50KB/次（取决于JPEG质量）
- **功耗**：约3-5W（不含4G模块）

## 反馈问题

如果遇到问题或有改进建议，请通过以下方式反馈：

1. **GitHub Issues**：https://github.com/your-username/movObjectCheck/issues
2. **提交Issue时请包含**：
   - 系统版本信息
   - 错误日志
   - 配置文件内容
   - 复现步骤

## 开源协议

本项目采用 MIT 协议开源，详见 [LICENSE](LICENSE) 文件。

## 贡献指南

欢迎提交 Pull Request 或 Issue！

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -am 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 Pull Request

## 作者

- 项目维护者：[Your Name]
- 联系方式：[your-email@example.com]

## 致谢

- OpenCV 计算机视觉库
- 树莓派社区

---

**注意**：本系统设计用于合法的监控场景，使用时请遵守当地法律法规。
