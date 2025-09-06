@echo off
echo ================================================
echo SEO Agent Pro 依赖安装脚本 (Windows)
echo ================================================

echo.
echo 1. 创建虚拟环境...
if not exist "venv" (
    python -m venv venv
    echo ✅ 虚拟环境创建成功
) else (
    echo ✅ 虚拟环境已存在
)

echo.
echo 2. 激活虚拟环境并安装依赖...
call venv\Scripts\activate.bat

echo.
echo 3. 升级pip...
python -m pip install --upgrade pip

echo.
echo 4. 安装基础依赖...
pip install fastapi uvicorn beautifulsoup4 requests
pip install openai python-whois jinja2 python-multipart aiofiles
pip install pandas lxml python-dotenv

echo.
echo 5. 安装数据分析依赖...
pip install matplotlib seaborn plotly wordcloud
pip install scikit-learn nltk spacy langdetect

echo.
echo 6. 安装其他依赖...
pip install fake-useragent psutil pillow
pip install aiohttp playwright

echo.
echo 7. 安装Playwright浏览器...
python -m playwright install chromium

echo.
echo 8. 下载spaCy模型...
python -m spacy download en_core_web_sm

echo.
echo ================================================
echo ✅ 所有依赖安装完成！
echo.
echo 现在可以运行项目了：
echo python app.py
echo ================================================
pause