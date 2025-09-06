# 🚀 Render.com 部署指南

## 快速部署步骤

### 1. 准备代码
确保所有文件已准备完毕：
- ✅ `app.py` - 主应用文件
- ✅ `start.py` - 启动脚本
- ✅ `build.sh` - 构建脚本
- ✅ `requirements.txt` - 依赖列表
- ✅ `README.md` - 项目说明

### 2. 推送到GitHub
```bash
git add .
git commit -m "准备Render部署"
git push origin main
```

### 3. 在Render创建服务

#### 3.1 登录Render
- 访问 [render.com](https://render.com)
- 使用GitHub账号登录

#### 3.2 创建Web Service
1. 点击 "New +" → "Web Service"
2. 选择你的GitHub仓库 `SEO_Agent`
3. 配置服务：

**基本设置：**
- Name: `seo-agent-pro`
- Region: `Oregon (US West)` 或 `Frankfurt (EU)` 
- Branch: `main`
- Root Directory: 留空
- Runtime: `Python 3`

**构建设置：**
- Build Command: `./build.sh`
- Start Command: `python start.py`

**计划选择：**
- Free tier（免费，有限制）
- Starter（$7/月，推荐）

### 4. 环境变量配置

在Render控制台的 "Environment" 标签页添加：

```
SILICONFLOW_API_KEY=your_api_key_here
PYTHON_VERSION=3.11.0
```

### 5. 部署完成

部署完成后，你将获得：
- 🌐 **公网URL**: `https://seo-agent-pro.onrender.com`
- 🔒 **HTTPS**: 自动配置SSL证书
- 📊 **监控**: 实时性能监控
- 🔄 **自动部署**: GitHub推送自动更新

## 🎯 Render优势

### ✅ 完美支持
- **Python 3.11+**: 完整Python生态支持
- **Playwright**: 原生支持浏览器自动化
- **SQLite**: 持久化数据存储
- **环境变量**: 安全的配置管理

### 🚀 生产特性
- **自动扩缩容**: 根据流量自动调整
- **健康检查**: 自动故障恢复
- **日志管理**: 实时日志查看
- **性能监控**: 详细性能指标

### 💰 费用透明
- **Free Tier**: 
  - 750小时/月免费
  - 15分钟无活动后休眠
  - 适合测试和展示

- **Starter ($7/月)**:
  - 无休眠限制
  - 更多计算资源
  - 数据持久化
  - 推荐生产使用

## 🔧 高级配置

### 自定义域名
在Render控制台可以绑定自定义域名：
1. "Settings" → "Custom Domains"
2. 添加你的域名
3. 配置DNS记录

### 数据库升级
如果需要PostgreSQL等数据库：
1. 在Render创建数据库服务
2. 修改`database.py`配置
3. 更新环境变量

### 监控告警
设置健康检查和告警：
1. "Settings" → "Health Check Path": `/`
2. 配置Slack/Email通知

## 🐛 故障排除

### 常见问题

**1. 构建失败**
```bash
# 检查build.sh权限
chmod +x build.sh
```

**2. Playwright安装失败**
- 确保使用Starter计划或以上
- Free tier内存可能不足

**3. 启动超时**
- 检查start.py脚本
- 确保端口配置正确

**4. API密钥问题**
- 在Environment中设置SILICONFLOW_API_KEY
- 确保API密钥有效

### 日志查看
在Render控制台的"Logs"标签页可以查看：
- 构建日志
- 运行时日志
- 错误信息

## 🎉 部署完成后

### 测试功能
1. 访问部署URL
2. 测试网站分析功能
3. 检查AI分析是否正常
4. 验证历史记录保存

### 性能优化
1. 监控响应时间
2. 查看资源使用情况
3. 根据需要升级计划

### 维护更新
1. GitHub推送自动部署
2. 定期检查日志
3. 监控API额度使用

---

🌟 **恭喜！你的SEO Agent Pro现在已经部署到云端，可以为全世界提供智能SEO分析服务了！**
