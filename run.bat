@echo off
chcp 65001 >nul
echo ================================================
echo 🚀 SEO Agent Pro 启动器 (Windows)
echo ================================================

echo.
echo 📦 正在检查环境...

:: 检查虚拟环境
if not exist "venv" (
    echo ❌ 虚拟环境不存在，请先运行 install.bat
    pause
    exit /b 1
)

:: 激活虚拟环境
echo ✅ 激活虚拟环境...
call venv\Scripts\activate.bat

:: 检查依赖
echo 📋 检查依赖...
python -c "import plotly" 2>nul
if errorlevel 1 (
    echo ⚠️  依赖未完全安装，请先运行 install.bat
    pause
    exit /b 1
)

echo.
echo ================================================
echo ✅ 准备完成！启动 SEO Agent Pro...
echo ================================================

:: 启动应用
python app.py

pause