#!/usr/bin/env python3
"""
SEO Agent Pro 启动脚本
自动检测环境，安装依赖，并启动服务
"""
import os
import sys
import subprocess
import asyncio
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        sys.exit(1)
    print(f"✅ Python版本: {sys.version}")

def check_dependencies():
    """检查并安装依赖"""
    print("\n📦 检查依赖...")
    
    # 检查是否存在虚拟环境
    venv_path = Path("venv")
    if not venv_path.exists():
        print("创建虚拟环境...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])
    
    # 激活虚拟环境并安装依赖
    if os.name == 'nt':  # Windows
        pip_path = venv_path / "Scripts" / "pip"
        python_path = venv_path / "Scripts" / "python"
    else:  # Unix/Linux/Mac
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    print("安装/更新依赖...")
    subprocess.run([str(pip_path), "install", "-r", "requirements.txt"])
    
    # 安装Playwright浏览器
    print("安装Playwright浏览器...")
    subprocess.run([str(python_path), "-m", "playwright", "install", "chromium"])
    
    # 下载spaCy模型
    print("下载spaCy英语模型...")
    subprocess.run([str(python_path), "-m", "spacy", "download", "en_core_web_sm"])
    
    return str(python_path)

def setup_database():
    """初始化数据库"""
    print("\n💾 初始化数据库...")
    from database import init_db
    init_db()
    print("✅ 数据库初始化完成")

def check_environment():
    """检查环境变量"""
    print("\n🔧 检查环境配置...")
    
    # 检查.env文件
    env_file = Path(".env")
    if not env_file.exists():
        print("创建.env文件...")
        with open(env_file, "w") as f:
            f.write("# SiliconFlow API配置\n")
            f.write("SILICONFLOW_API_KEY=your_api_key_here\n")
            f.write("\n# 可选：OpenAI API配置（备用）\n")
            f.write("OPENAI_API_KEY=your_openai_key_here\n")
        print("⚠️  请编辑.env文件，添加您的API密钥")
    
    # 检查API密钥
    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key or api_key == 'your_api_key_here':
        print("⚠️  警告: 未配置SiliconFlow API密钥")
        print("   AI分析功能将不可用")
        print("   请在.env文件中设置SILICONFLOW_API_KEY")
    else:
        print("✅ API密钥已配置")

def create_directories():
    """创建必要的目录"""
    print("\n📁 创建目录...")
    directories = ["reports", "logs", "static/css", "static/js", "static/images"]
    for dir_name in directories:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {dir_name}")

async def test_imports():
    """测试导入"""
    print("\n🧪 测试导入...")
    
    try:
        # 测试基础依赖
        import fastapi
        import uvicorn
        import aiohttp
        import beautifulsoup4
        import requests
        print("✅ 基础依赖导入成功")
        
        # 测试AI相关依赖
        import openai
        print("✅ OpenAI库导入成功")
        
        # 测试数据科学依赖
        import pandas
        import numpy
        import matplotlib
        import seaborn
        print("✅ 数据科学库导入成功")
        
        # 测试NLP依赖
        import nltk
        import spacy
        print("✅ NLP库导入成功")
        
        # 测试增强功能
        from seo_analyzer import EnhancedSEOAgent
        print("✅ SEO分析器导入成功")
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保所有依赖都已正确安装")
        return False
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 SEO Agent Pro 启动器")
    print("=" * 60)
    
    # 检查Python版本
    check_python_version()
    
    # 创建目录
    create_directories()
    
    # 检查依赖
    python_path = check_dependencies()
    
    # 设置数据库
    setup_database()
    
    # 检查环境
    check_environment()
    
    # 测试导入
    if not asyncio.run(test_imports()):
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ 所有检查通过！")
    print("\n🎯 启动选项:")
    print("   1. 标准模式 (python app.py)")
    print("   2. 开发模式 (自动重载)")
    print("   3. Vercel部署 (vercel dev)")
    print("\n📝 文件说明:")
    print("   - main.py: 原始版本")
    print("   - app.py: 主应用文件（推荐）")
    print("   - seo_analyzer.py: SEO分析引擎")
    print("   - batch.html: 批量处理界面")
    print("=" * 60)
    
    # 询问启动模式
    try:
        choice = input("\n请选择启动模式 (1/2/3): ").strip()
        
        if choice == "1":
            print("\n🌟 启动标准模式...")
            subprocess.run([python_path, "app.py"])
        elif choice == "2":
            print("\n🔥 启动开发模式...")
            subprocess.run([
                python_path, "-m", "uvicorn",
                "app:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload"
            ])
        elif choice == "3":
            print("\n☁️  启动Vercel开发模式...")
            print("请确保已安装 vercel CLI: npm i -g vercel")
            subprocess.run(["vercel", "dev"])
        else:
            print("\n默认启动标准模式...")
            subprocess.run([python_path, "app.py"])
            
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")

if __name__ == "__main__":
    main()