# 贡献指南

感谢您对本项目的关注！我们欢迎任何形式的贡献。

## 如何贡献

### 报告Bug

如果您发现了bug，请创建一个Issue，并包含以下信息：

1. **问题描述**：清晰描述遇到的问题
2. **复现步骤**：详细的复现步骤
3. **期望行为**：您期望的正确行为
4. **实际行为**：实际发生的情况
5. **环境信息**：
   - 操作系统版本
   - 树莓派型号
   - OpenCV版本
   - Python版本（服务器端）
6. **日志信息**：相关的错误日志
7. **配置文件**：您的配置文件内容（去除敏感信息）

### 提出新功能

如果您有新功能建议，请创建一个Issue，并说明：

1. **功能描述**：详细描述建议的功能
2. **使用场景**：这个功能解决什么问题
3. **实现思路**：如果有的话，简单描述实现思路

### 提交代码

1. **Fork本仓库**

2. **创建特性分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **编写代码**
   - 遵循现有代码风格
   - 添加必要的注释
   - 确保代码可以编译通过

4. **测试**
   - 在树莓派上测试您的修改
   - 确保不会破坏现有功能

5. **提交更改**
   ```bash
   git add .
   git commit -m "Add: 简短描述您的修改"
   ```

   提交信息格式：
   - `Add: 新增功能`
   - `Fix: 修复bug`
   - `Update: 更新功能`
   - `Refactor: 重构代码`
   - `Docs: 文档更新`

6. **推送到您的仓库**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **创建Pull Request**
   - 在GitHub上创建Pull Request
   - 详细描述您的修改
   - 关联相关的Issue

## 代码规范

### C++代码

- 使用4个空格缩进
- 类名使用大驼峰：`MotionDetector`
- 函数名使用小驼峰：`detectMotion`
- 变量名使用下划线：`frame_count_`
- 私有成员变量以下划线结尾：`config_`

### Python代码

- 遵循PEP 8规范
- 使用4个空格缩进
- 类名使用大驼峰：`ImageServer`
- 函数名使用下划线：`handle_client`

### 注释

- 关键算法添加注释说明
- 复杂逻辑添加解释
- 公共接口添加文档注释

## 开发环境设置

### 树莓派端开发

```bash
# 安装依赖
sudo ./scripts/install_dependencies.sh

# 编译
./scripts/build.sh

# 运行测试
./build/motion_detector config/config.ini
```

### 服务器端开发

```bash
# 安装依赖
cd server
pip3 install -r requirements.txt

# 运行
python3 server.py
```

## 测试

在提交PR前，请确保：

- [ ] 代码可以成功编译
- [ ] 在树莓派上测试通过
- [ ] 服务器端可以正常接收图像
- [ ] 没有破坏现有功能
- [ ] 添加了必要的文档

## 文档

如果您的修改涉及：

- 新功能：更新README.md
- 配置变更：更新CONFIGURATION.md
- 部署变更：更新DEPLOYMENT.md
- 常见问题：更新TROUBLESHOOTING.md

## 行为准则

- 尊重所有贡献者
- 保持友好和专业
- 接受建设性批评
- 关注项目目标

## 许可证

提交代码即表示您同意将代码以MIT许可证开源。

## 联系方式

如有疑问，可以通过以下方式联系：

- 创建Issue讨论
- 发送邮件到项目维护者

感谢您的贡献！
