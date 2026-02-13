# 配置说明文档

本文档详细说明系统的所有配置参数。

## 树莓派端配置 (config/config.ini)

### 摄像头配置

```ini
# 摄像头设备索引，通常为0
# 如果有多个摄像头，可以尝试1、2等
camera_index = 0

# 视频帧宽度（像素）
# 常用值：320, 640, 1280, 1920
frame_width = 640

# 视频帧高度（像素）
# 常用值：240, 480, 720, 1080
frame_height = 480

# 帧率（每秒帧数）
# 推荐值：10-30，越高越流畅但功耗越大
fps = 15
```

### 运动检测参数

```ini
# 运动检测阈值（0-255）
# 值越小越敏感，越容易检测到运动
# 推荐范围：20-30
# - 环境噪声大：增加到30-40
# - 需要高灵敏度：降低到15-20
motion_threshold = 25

# 最小运动区域面积（像素）
# 小于此面积的运动会被忽略，用于过滤噪声
# 推荐范围：500-2000
# - 检测小物体：300-500
# - 只检测大物体：1000-3000
min_area = 500

# 光照变化阈值（0-255）
# 用于过滤光线变化造成的误检测
# 推荐范围：10-20
# - 光线变化频繁：增加到20-30
# - 室内稳定光源：可降低到5-10
lighting_threshold = 15

# 背景更新间隔（帧数）
# 每隔多少帧更新一次背景模型
# 推荐范围：20-50
# - 场景变化快：减小到10-20
# - 场景稳定：增加到50-100
background_update_interval = 30
```

### 网络配置

```ini
# 服务器IP地址
# 局域网示例：192.168.1.100
# 公网示例：123.45.67.89
server_ip = 192.168.1.100

# 服务器端口
# 默认：8888
# 注意：需要与服务器端配置一致
server_port = 8888

# 连接超时时间（毫秒）
# 推荐范围：3000-10000
connection_timeout = 5000
```

### 传输配置

```ini
# JPEG压缩质量（1-100）
# 值越高图像质量越好，但数据量越大
# 推荐范围：70-90
# - 4G网络较慢：60-70
# - WiFi或有线网络：80-95
jpeg_quality = 80

# 连接失败最大重试次数
# 推荐范围：3-10
max_retry = 3
```

## 服务器端配置 (config/server_config.ini)

### 服务器配置

```ini
[server]
# 监听地址
# 0.0.0.0：监听所有网络接口（推荐）
# 127.0.0.1：仅本地访问
# 具体IP：仅监听指定网卡
host = 0.0.0.0

# 监听端口
# 默认：8888
# 注意：需要与客户端配置一致
port = 8888

# 是否保存接收到的图像
# true：保存所有图像
# false：不保存，仅显示
save_images = true

# 图像保存目录
# 相对路径或绝对路径
save_dir = received_images

# 是否显示接收到的图像
# true：弹出窗口显示（需要图形界面）
# false：不显示（适合无图形界面的服务器）
display_images = true

# 最大客户端连接数
# 推荐范围：1-10
max_clients = 5
```

## 配置示例

### 场景1：室外监控（光线变化大）

```ini
# 树莓派端
motion_threshold = 30
min_area = 1000
lighting_threshold = 25
jpeg_quality = 70
fps = 10
```

### 场景2：室内监控（光线稳定）

```ini
# 树莓派端
motion_threshold = 20
min_area = 500
lighting_threshold = 10
jpeg_quality = 85
fps = 15
```

### 场景3：低功耗模式

```ini
# 树莓派端
frame_width = 320
frame_height = 240
fps = 10
jpeg_quality = 60
motion_threshold = 30
```

### 场景4：高质量模式

```ini
# 树莓派端
frame_width = 1280
frame_height = 720
fps = 20
jpeg_quality = 90
motion_threshold = 20
```

## 动态调整配置

### 方法1：修改配置文件后重启

```bash
# 编辑配置
nano config/config.ini

# 重启服务
sudo systemctl restart motion-detector
```

### 方法2：使用不同配置文件

```bash
# 创建多个配置文件
cp config/config.ini config/config_outdoor.ini
cp config/config.ini config/config_indoor.ini

# 使用指定配置运行
./build/motion_detector config/config_outdoor.ini
```

## 配置验证

### 检查配置是否生效

运行程序后，观察输出日志：

```
=== 移动物体检测系统 ===
配置文件加载成功
摄像头初始化成功
成功连接到服务器: 192.168.1.100:8888
系统启动成功，开始监控...
```

### 常见配置错误

1. **服务器IP配置错误**
   ```
   错误信息：连接服务器失败
   解决方案：检查server_ip是否正确
   ```

2. **端口被占用**
   ```
   错误信息：bind: Address already in use
   解决方案：更改端口或关闭占用端口的程序
   ```

3. **摄像头索引错误**
   ```
   错误信息：无法打开摄像头
   解决方案：尝试修改camera_index为1或2
   ```

## 性能优化建议

### 降低CPU占用

- 降低 `fps`
- 降低 `frame_width` 和 `frame_height`
- 增加 `motion_threshold`（减少误检测）

### 降低网络带宽

- 降低 `jpeg_quality`
- 降低 `frame_width` 和 `frame_height`
- 增加 `motion_threshold`（减少发送频率）

### 提高检测准确性

- 根据环境调整 `motion_threshold`
- 调整 `min_area` 过滤噪声
- 调整 `lighting_threshold` 过滤光照变化

## 配置文件模板

完整的配置文件模板已包含在项目中：
- `config/config.ini` - 树莓派端配置
- `config/server_config.ini` - 服务器端配置

可以直接复制修改使用。
