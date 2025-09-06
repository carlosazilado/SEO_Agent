"""
应用保活和健康检查系统
防止Render应用休眠，确保服务稳定性
"""

import asyncio
import aiohttp
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class KeepAliveService:
    """保活服务，防止应用休眠"""
    
    def __init__(self, app_url=None, interval=900):  # 15分钟ping一次
        self.app_url = app_url or os.getenv('RENDER_EXTERNAL_URL', 'http://localhost:8000')
        self.interval = interval
        self.running = False
        
    async def ping_self(self):
        """定期ping自己保持活跃"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.app_url}/health") as response:
                    if response.status == 200:
                        logger.info(f"✅ Keep-alive ping successful at {datetime.now()}")
                    else:
                        logger.warning(f"⚠️ Keep-alive ping returned {response.status}")
        except Exception as e:
            logger.error(f"❌ Keep-alive ping failed: {e}")
    
    async def start(self):
        """启动保活服务"""
        if self.running:
            return
            
        self.running = True
        logger.info(f"🟢 Keep-alive service started, pinging every {self.interval/60} minutes")
        
        while self.running:
            await asyncio.sleep(self.interval)
            if self.running:
                await self.ping_self()
    
    def stop(self):
        """停止保活服务"""
        self.running = False
        logger.info("🔴 Keep-alive service stopped")

# 全局保活服务实例
keep_alive_service = KeepAliveService()

async def start_keep_alive():
    """启动保活服务"""
    # 只在生产环境启动
    if os.getenv('RENDER_EXTERNAL_URL'):
        asyncio.create_task(keep_alive_service.start())
        logger.info("🚀 Production keep-alive service activated")
    else:
        logger.info("🔧 Development mode, keep-alive service disabled")

def stop_keep_alive():
    """停止保活服务"""
    keep_alive_service.stop()
