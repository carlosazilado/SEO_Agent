@echo off
chcp 65001 >nul
echo ================================================
echo 🚀 SEO Agent Pro 启动器 (Windows)
echo ================================================

echo.
echo 📦 正在检查环境...

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python
    echo 请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

:: 检查虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

:: 激活虚拟环境
call venv\Scripts\activate.bat

:: 安装依赖
echo 安装/更新依赖...
pip install -r requirements.txt

:: 安装Playwright
echo 安装Playwright浏览器...
python -m playwright install chromium

:: 下载spaCy模型
echo 下载spaCy模型...
python -m spacy download en_core_web_sm

:: 检查.env文件
if not exist ".env" (
    echo 创建.env文件...
    echo # SiliconFlow API配置> .env
    echo SILICONFLOW_API_KEY=your_api_key_here>> .env
    echo.
    echo ⚠️  请编辑.env文件，添加您的API密钥
)

echo.
echo ================================================
echo ✅ 准备完成！
echo.
echo 🎯 启动选项:
echo    1. 标准模式
echo    2. 开发模式（自动重载）
echo ================================================

set /p choice="请选择启动模式 (1/2): "

if "%choice%"=="1" (
    echo.
    echo 🌟 启动标准模式...
    python app.py
) else if "%choice%"=="2" (
    echo.
    echo 🔥 启动开发模式...
    uvicorn app:app --host 0.0.0.0 --port 8000 --reload
) else (
    echo.
    echo 默认启动标准模式...
    python app.py
)

pause