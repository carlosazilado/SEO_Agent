#!/bin/bash

# Render部署脚本
echo "🚀 开始部署SEO Agent Pro..."

# 安装Python依赖
echo "📦 安装Python依赖..."
pip install -r requirements.txt

# 安装Playwright浏览器和依赖
echo "🌐 安装Playwright浏览器..."
playwright install chromium
playwright install-deps

# 创建必要的目录
echo "📁 创建目录结构..."
mkdir -p reports
mkdir -p static/images

# 初始化数据库
echo "🗄️ 初始化数据库..."
python -c "from database import init_db; init_db(); print('✅ 数据库初始化完成')"

echo "✅ 部署准备完成！"
