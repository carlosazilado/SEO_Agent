# SEO Agent Pro - 项目部署指南

## 📋 项目概述

SEO Agent Pro 是一个基于AI的智能SEO分析系统，集成了硅基流动API、Playwright浏览器自动化和FastAPI后端。

## 🏁 快速部署到Render

### 1. 准备工作
```bash
# 确保你的代码已经推送到GitHub
git add .
git commit -m "准备部署到Render"
git push origin main
```

### 2. 在Render创建新服务
1. 访问 [Render.com](https://render.com)
2. 连接你的GitHub账户
3. 选择 "New Web Service"
4. 选择你的SEO_Agent仓库

### 3. 配置部署设置
- **Name**: `seo-agent-pro`
- **Environment**: `Python 3`
- **Region**: 选择离你最近的区域
- **Branch**: `main`
- **Build Command**: `./build.sh`
- **Start Command**: `python start.py`

### 4. 环境变量配置
在Render的Environment Variables中添加：
```
SILICONFLOW_API_KEY=sk-fxeehbzkospkgoluchoqgxgkszkjaluozkohofghkzrqianx
PORT=8000
PYTHON_VERSION=3.11.5
```

### 5. 等待部署完成
- 部署时间约5-10分钟
- 查看Build Logs确保无错误
- 部署成功后会得到一个 `.onrender.com` 域名

## 🛠️ 本地开发设置

### 1. 克隆项目
```bash
git clone https://github.com/你的用户名/SEO_Agent.git
cd SEO_Agent
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
playwright install
```

### 3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，添加你的API密钥
```

### 4. 启动开发服务器
```bash
python app.py
```

### 5. 访问应用
- 主页: http://localhost:8000
- 历史记录: http://localhost:8000/history

## 🔧 故障排除

### Playwright问题
如果遇到Playwright错误：
```bash
playwright install --with-deps
```

### 数据库问题
如果数据库文件丢失：
```bash
python -c "from database import init_db; init_db()"
```

### 端口占用
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

## 📊 监控和维护

### 日志查看
- 应用日志: `seo_agent.log`
- Render控制台的 Logs 选项卡

### 性能监控
- 内存使用: 建议512MB以上
- CPU使用: 基础版本足够
- 磁盘空间: 建议1GB以上

### 更新部署
```bash
git add .
git commit -m "更新功能"
git push origin main
# Render会自动检测并重新部署
```

## 🔐 安全建议

1. **API密钥安全**
   - 不要将API密钥提交到GitHub
   - 使用环境变量存储敏感信息

2. **访问控制**
   - 考虑添加用户认证
   - 限制API调用频率

3. **数据保护**
   - 定期备份数据库
   - 清理敏感日志信息

## 💰 成本估算

### Render免费版本
- 750小时/月免费运行时间
- 睡眠机制：15分钟无活动后休眠
- 512MB内存限制

### 升级建议
- 如果需要24/7运行，考虑升级到付费版本
- 付费版本：$7/月起，无睡眠限制

## 📞 技术支持

### 常见问题
1. **部署失败**: 检查build.sh权限和依赖版本
2. **API调用失败**: 验证硅基流动API密钥
3. **页面无法访问**: 检查防火墙和端口设置

### 联系方式
- GitHub Issues: 在项目仓库提交问题
- 邮件支持: 添加你的联系邮箱

---

🎉 **部署成功后，你的SEO Agent Pro就可以在线使用了！**

访问你的Render域名开始使用智能SEO分析功能。
