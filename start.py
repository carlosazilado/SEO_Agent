#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SEO Agent Pro 启动脚本
适用于 Render.com 部署
"""

import os
import sys
import uvicorn
from pathlib import Path

def main():
    """主启动函数"""
    print("🚀 SEO Agent Pro 启动中...")
    
    # 检查环境
    print(f"🐍 Python版本: {sys.version}")
    print(f"📁 工作目录: {os.getcwd()}")
    
    # 列出当前目录文件
    print("📁 当前目录文件:")
    for item in os.listdir('.'):
        print(f"  - {item}")
    
    # 检查必要文件
    required_files = ['app.py', 'seo_analyzer.py', 'seo_agents.py', 'database.py']
    missing_files = []
    for file in required_files:
        if Path(file).exists():
            print(f"✅ 找到文件: {file}")
        else:
            print(f"❌ 缺少文件: {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {missing_files}")
        sys.exit(1)
    
    # 环境变量检查
    api_key = os.getenv('SILICONFLOW_API_KEY')
    if api_key:
        print(f"✅ 检测到API密钥: {api_key[:10]}...{api_key[-5:] if len(api_key) > 15 else ''}")
    else:
        print("⚠️  未检测到API密钥，将使用基础分析模式")
    
    # 获取端口（Render自动设置）
    port = int(os.getenv('PORT', 8000))
    host = "0.0.0.0"
    
    print(f"🌐 启动服务器: {host}:{port}")
    
    # 初始化数据库
    try:
        print("🗄️  初始化数据库...")
        from database import init_db
        init_db()
        print("✅ 数据库初始化成功")
    except Exception as e:
        print(f"⚠️  数据库初始化警告: {e}")
    
    print("📊 SEO Agent Pro 已就绪！")
    
    # 启动应用
    try:
        uvicorn.run(
            "app:app",
            host=host,
            port=port,
            reload=False,  # 生产模式
            log_level="info",
            access_log=True,
            timeout_keep_alive=30
        )
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
