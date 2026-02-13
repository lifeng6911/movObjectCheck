# 故障排除指南

本文档列出常见问题及解决方案。

## 目录

1. [摄像头问题](#摄像头问题)
2. [网络连接问题](#网络连接问题)
3. [检测问题](#检测问题)
4. [编译问题](#编译问题)
5. [性能问题](#性能问题)
6. [4G模块问题](#4g模块问题)

## 摄像头问题

### 问题1：无法打开摄像头

**错误信息**：
```
无法打开摄像头
```

**可能原因及解决方案**：

1. **摄像头未连接**
   ```bash
   # 检查摄像头设备
   ls /dev/video*
   # 应该看到 /dev/video0 或类似设备
   ```

2. **权限不足**
   ```bash
   # 检查当前用户组
   groups

   # 添加到video组
   sudo usermod -a -G video $USER

   # 重新登录使权限生效
   ```

3. **设备索引错误**
   ```bash
   # 查看所有视频设备
   v4l2-ctl --list-devices

   # 修改config.ini中的camera_index
   camera_index = 0  # 尝试0, 1, 2等
   ```

4. **摄像头被其他程序占用**
   ```bash
   # 查找占用摄像头的进程
   sudo lsof /dev/video0

   # 结束占用进程
   sudo kill -9 <PID>
   ```

### 问题2：图像质量差

**解决方案**：

1. **调整分辨率**
   ```ini
   frame_width = 1280
   frame_height = 720
   ```

2. **提高JPEG质量**
   ```ini
   jpeg_quality = 90
   ```

3. **检查摄像头焦距**
   - 手动调整摄像头焦距
   - 清洁镜头

### 问题3：帧率过低

**解决方案**：

1. **降低分辨率**
   ```ini
   frame_width = 320
   frame_height = 240
   ```

2. **检查CPU占用**
   ```bash
   top
   # 如果CPU占用过高，考虑优化代码或升级硬件
   ```

## 网络连接问题

### 问题4：连接服务器失败

**错误信息**：
```
连接服务器失败: 192.168.1.100:8888
```

**解决方案**：

1. **检查网络连通性**
   ```bash
   # 测试ping
   ping 192.168.1.100

   # 测试端口
   telnet 192.168.1.100 8888
   # 或
   nc -zv 192.168.1.100 8888
   ```

2. **检查服务器是否运行**
   ```bash
   # 在服务器上检查
   sudo netstat -tlnp | grep 8888
   ```

3. **检查防火墙**
   ```bash
   # 服务器端（Linux）
   sudo ufw status
   sudo ufw allow 8888/tcp

   # 或使用iptables
   sudo iptables -L -n | grep 8888
   ```

4. **检查配置文件**
   ```ini
   # 确认IP和端口正确
   server_ip = 192.168.1.100
   server_port = 8888
   ```

### 问题5：连接频繁断开

**解决方案**：

1. **检查网络稳定性**
   ```bash
   # 持续ping测试
   ping -c 100 192.168.1.100
   ```

2. **增加超时时间**
   ```ini
   connection_timeout = 10000
   ```

3. **增加重试次数**
   ```ini
   max_retry = 5
   ```

### 问题6：发送图像失败

**错误信息**：
```
发送图像数据失败
```

**解决方案**：

1. **检查网络带宽**
   ```bash
   # 测试网速
   iperf3 -c 192.168.1.100
   ```

2. **降低图像质量**
   ```ini
   jpeg_quality = 60
   frame_width = 320
   frame_height = 240
   ```

## 检测问题

### 问题7：误检测过多

**现象**：没有运动也频繁检测到

**解决方案**：

1. **增加检测阈值**
   ```ini
   motion_threshold = 35
   min_area = 1000
   ```

2. **增加光照过滤**
   ```ini
   lighting_threshold = 25
   ```

3. **检查摄像头位置**
   - 避免对着窗户（光线变化大）
   - 避免对着风扇、窗帘等易动物体
   - 固定摄像头，避免晃动

### 问题8：漏检测

**现象**：有明显运动但未检测到

**解决方案**：

1. **降低检测阈值**
   ```ini
   motion_threshold = 15
   min_area = 300
   ```

2. **检查摄像头视野**
   - 确保运动物体在视野内
   - 调整摄像头角度

3. **检查光照条件**
   - 确保有足够光线
   - 避免逆光

### 问题9：光线变化误检测

**现象**：日出日落、云层变化时频繁误报

**解决方案**：

1. **调整光照过滤参数**
   ```ini
   lighting_threshold = 30
   ```

2. **调整背景更新频率**
   ```ini
   background_update_interval = 20
   ```

## 编译问题

### 问题10：找不到OpenCV

**错误信息**：
```
CMake Error: Could not find OpenCV
```

**解决方案**：

```bash
# 安装OpenCV开发包
sudo apt-get install libopencv-dev

# 或手动指定OpenCV路径
cmake -DOpenCV_DIR=/usr/local/lib/cmake/opencv4 ..
```

### 问题11：编译错误

**错误信息**：
```
error: 'CV_BGR2GRAY' was not declared
```

**解决方案**：

这是OpenCV版本差异，修改代码：
```cpp
// OpenCV 4.x
cv::COLOR_BGR2GRAY

// OpenCV 3.x
CV_BGR2GRAY
```

### 问题12：链接错误

**错误信息**：
```
undefined reference to `cv::VideoCapture::VideoCapture()'
```

**解决方案**：

```bash
# 检查OpenCV安装
pkg-config --modversion opencv4

# 重新编译
cd build
rm -rf *
cmake ..
make
```

## 性能问题

### 问题13：CPU占用过高

**解决方案**：

1. **降低帧率**
   ```ini
   fps = 10
   ```

2. **降低分辨率**
   ```ini
   frame_width = 320
   frame_height = 240
   ```

3. **优化检测参数**
   ```ini
   motion_threshold = 30  # 减少处理次数
   ```

### 问题14：内存占用过高

**解决方案**：

1. **检查内存泄漏**
   ```bash
   # 使用valgrind检测
   valgrind --leak-check=full ./motion_detector
   ```

2. **降低图像缓存**
   - 修改代码，及时释放Mat对象

### 问题15：延迟过大

**解决方案**：

1. **优化网络**
   - 使用有线网络代替WiFi
   - 降低图像质量减少传输时间

2. **优化处理流程**
   ```ini
   fps = 20  # 提高采样率
   jpeg_quality = 70  # 降低压缩时间
   ```

## 4G模块问题

### 问题16：4G模块无法识别

**解决方案**：

```bash
# 检查USB设备
lsusb

# 检查串口设备
ls /dev/ttyUSB*

# 安装USB串口驱动
sudo apt-get install usb-modeswitch
```

### 问题17：无法拨号上网

**解决方案**：

1. **检查SIM卡**
   - 确认SIM卡已激活
   - 确认有流量套餐

2. **检查APN配置**
   ```bash
   # 编辑拨号配置
   sudo nano /etc/ppp/peers/gprs

   # 修改APN（根据运营商）
   # 中国移动：cmnet
   # 中国联通：3gnet
   # 中国电信：ctnet
   ```

3. **手动拨号测试**
   ```bash
   sudo pppd call gprs

   # 查看连接状态
   ifconfig ppp0
   ```

### 问题18：4G网络不稳定

**解决方案**：

1. **检查信号强度**
   ```bash
   # 使用AT命令查询信号
   echo "AT+CSQ" > /dev/ttyUSB2
   cat /dev/ttyUSB2
   ```

2. **调整天线位置**
   - 移动到信号更好的位置
   - 使用外置天线

3. **配置自动重连**
   ```bash
   # 编辑/etc/ppp/peers/gprs
   # 添加：
   persist
   maxfail 0
   ```

## 系统问题

### 问题19：服务无法启动

**解决方案**：

```bash
# 查看服务状态
sudo systemctl status motion-detector

# 查看详细日志
sudo journalctl -u motion-detector -n 50

# 检查配置文件路径
ls -l /opt/motion_detector/config/config.ini
```

### 问题20：开机不自启

**解决方案**：

```bash
# 启用服务
sudo systemctl enable motion-detector

# 检查是否已启用
sudo systemctl is-enabled motion-detector
```

## 日志分析

### 查看日志

```bash
# 树莓派端
tail -f /opt/motion_detector/logs/output.log

# 服务器端
tail -f /var/log/motion-server.log

# systemd日志
sudo journalctl -u motion-detector -f
```

### 常见日志信息

1. **正常运行**
   ```
   系统启动成功，开始监控...
   监控中... (无运动)
   ```

2. **检测到运动**
   ```
   检测到移动物体！
   成功发送图像，大小: 15234 字节
   ```

3. **网络问题**
   ```
   发送图像失败
   尝试重新连接... (1/3)
   ```

## 获取帮助

如果以上方案无法解决问题，请：

1. **收集信息**
   ```bash
   # 系统信息
   uname -a
   cat /etc/os-release

   # OpenCV版本
   pkg-config --modversion opencv4

   # 错误日志
   tail -n 100 /opt/motion_detector/logs/error.log
   ```

2. **提交Issue**
   - 访问：https://github.com/your-username/movObjectCheck/issues
   - 包含：系统信息、错误日志、配置文件、复现步骤

3. **社区求助**
   - 树莓派论坛
   - OpenCV社区
   - Stack Overflow
