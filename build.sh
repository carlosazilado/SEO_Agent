#!/bin/bash

# Render部署脚本
echo "🚀 开始部署SEO Agent Pro..."

# 安装Python依赖
echo "📦 安装Python依赖..."
pip install -r requirements.txt

# 安装Playwright浏览器
echo "🌐 安装Playwright浏览器..."
playwright install chromium

echo "✅ 部署准备完成！"
