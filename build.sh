#!/bin/bash

# Render部署脚本
echo "🚀 开始部署SEO Agent Pro..."
echo "Python版本: $(python --version)"
echo "Pip版本: $(pip --version)"

# 升级pip
echo "⬆️ 升级pip..."
pip install --upgrade pip

# 安装Python依赖
echo "📦 安装Python依赖..."
pip install -r requirements.txt

# 验证关键依赖
echo "🔍 验证依赖安装..."
python -c "import fastapi; print('✅ FastAPI已安装')"
python -c "import uvicorn; print('✅ Uvicorn已安装')"
python -c "import playwright; print('✅ Playwright已安装')"

# 安装Playwright浏览器和依赖
echo "🌐 安装Playwright浏览器..."
playwright install --with-deps chromium

# 验证Playwright安装
echo "🔍 验证Playwright浏览器..."
python -c "
import playwright
print('✅ Playwright Python包已安装')
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        browser.close()
    print('✅ Playwright浏览器可以正常启动')
except Exception as e:
    print(f'⚠️ Playwright浏览器启动失败: {e}')
"

# 创建必要的目录
echo "📁 创建目录结构..."
mkdir -p reports
mkdir -p static/images
mkdir -p templates

# 验证文件存在
echo "� 验证关键文件..."
for file in app.py start.py seo_analyzer.py database.py; do
    if [ -f "$file" ]; then
        echo "✅ $file 存在"
    else
        echo "❌ $file 不存在"
        exit 1
    fi
done

echo "✅ 部署准备完成！"
