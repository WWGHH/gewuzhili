# 动态密钥加密页面系统

## 项目介绍

本项目实现了一个基于Flask的动态密钥加密页面系统，用于保护HTML内容，防止AI破解和内容泄露。

### 核心特点

- **动态密钥管理**：密钥存储在服务器端，每次请求动态生成
- **密钥自动过期**：密钥60秒后自动失效，限制攻击窗口
- **强加密算法**：采用AES-256 CBC加密，安全性高
- **前端安全防护**：
  - 开发者工具检测
  - 禁止右键菜单
  - 禁止文本选择和复制
- **易于部署**：支持多种部署方式，包括开发环境和生产环境

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行开发服务器

```bash
python server.py
```

服务器将在 `http://127.0.0.1:5000` 启动。

### 3. 访问页面

在浏览器中输入 `http://127.0.0.1:5000` 即可访问加密页面。

## 部署指南

### 生产环境部署

#### 使用Gunicorn（推荐）

```bash
# 安装Gunicorn
pip install gunicorn

# 启动Gunicorn
# -w 4: 使用4个worker进程
# -b 127.0.0.1:8000: 绑定到本地8000端口
gunicorn -w 4 -b 127.0.0.1:8000 server:app
```

#### 使用Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件配置
    location /static/ {
        alias /path/to/your/project/static/;
        expires 30d;
    }
}
```

## 文件说明

| 文件名 | 作用 |
|--------|------|
| `server.py` | Flask服务器主程序，实现动态密钥生成和管理 |
| `dynamic_encrypted_index.html` | 加密页面模板，包含前端解密逻辑和安全防护 |
| `encrypted_index.html` | 原始加密页面文件 |
| `decrypt.py` | 本地解密脚本，用于解密HTML内容 |
| `requirements.txt` | Python依赖列表 |
| `.gitignore` | Git忽略配置 |
| `README.md` | 项目说明文档 |

## 安全特性

### 1. 动态密钥管理
- 每次请求生成新的AES-256密钥和IV
- 密钥存储在服务器端，永不直接暴露给用户
- 密钥60秒后自动失效，由后台线程定期清理

### 2. 前端安全防护
- **开发者工具检测**：检测到开发者工具时锁定页面
- **禁止右键菜单**：防止通过右键菜单查看源代码
- **禁止文本选择**：防止直接复制页面内容
- **禁止复制操作**：拦截剪贴板事件

### 3. 传输安全
- 建议在生产环境使用HTTPS，确保传输安全
- 支持通过Nginx配置SSL证书

## 工作流程

1. **用户访问**：用户访问网站首页
2. **密钥生成**：服务器生成随机AES-256密钥和IV
3. **内容加密**：服务器使用密钥加密原始HTML内容
4. **页面返回**：服务器将加密内容、IV和密钥ID嵌入模板返回给浏览器
5. **密钥获取**：浏览器使用密钥ID向服务器请求密钥
6. **内容解密**：浏览器使用密钥和IV解密HTML内容
7. **页面显示**：解密后替换当前页面内容，显示原始页面

## 自定义配置

### 修改密钥有效期

在 `server.py` 中修改 `KEY_EXPIRY` 变量：

```python
# 密钥有效期（秒）
KEY_EXPIRY = 60  # 默认60秒
```

### 修改加密算法参数

在 `server.py` 中修改加密相关参数：

```python
# 生成随机密钥和IV
key = get_random_bytes(32)  # AES-256，可改为16（AES-128）或24（AES-192）
iv = get_random_bytes(16)   # CBC模式需要16字节IV
```

## 常见问题

### 1. 页面显示"检测到开发者工具，页面已锁定"

这是正常的安全防护机制，关闭开发者工具后刷新页面即可。

### 2. 页面显示"页面加载失败，请刷新重试"

可能的原因：
- 密钥已过期
- 网络连接问题
- 服务器错误

请检查服务器日志，查看具体错误信息。

### 3. 如何更新加密内容

1. 更新 `original_index.html` 文件
2. 重启服务器或等待密钥自动更新

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件到 [your-email@example.com]
