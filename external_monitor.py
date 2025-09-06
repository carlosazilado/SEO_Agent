"""
外部监控脚本
定期检查SEO Agent Pro的健康状态，如果发现问题自动重启或告警
"""

import asyncio
import aiohttp
import time
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceMonitor:
    def __init__(self, service_url):
        self.service_url = service_url.rstrip('/')
        self.health_endpoint = f"{self.service_url}/health"
        self.main_endpoint = f"{self.service_url}/"
        
    async def check_health(self):
        """检查服务健康状态"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                # 检查健康端点
                async with session.get(self.health_endpoint) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ 健康检查通过: {data.get('timestamp')}")
                        return True
                    else:
                        logger.warning(f"⚠️ 健康检查失败: HTTP {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ 健康检查异常: {e}")
            return False
    
    async def wake_up_service(self):
        """唤醒休眠的服务"""
        try:
            logger.info("🔄 尝试唤醒服务...")
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
                async with session.get(self.main_endpoint) as response:
                    if response.status == 200:
                        logger.info("✅ 服务已成功唤醒")
                        return True
                    else:
                        logger.warning(f"⚠️ 服务唤醒失败: HTTP {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ 服务唤醒异常: {e}")
            return False
    
    async def monitor_loop(self, check_interval=300):  # 5分钟检查一次
        """监控循环"""
        logger.info(f"🔍 开始监控服务: {self.service_url}")
        logger.info(f"📅 检查间隔: {check_interval}秒")
        
        consecutive_failures = 0
        max_failures = 3
        
        while True:
            try:
                is_healthy = await self.check_health()
                
                if is_healthy:
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    logger.warning(f"⚠️ 连续失败次数: {consecutive_failures}/{max_failures}")
                    
                    if consecutive_failures >= max_failures:
                        logger.error("🚨 服务可能已崩溃，尝试唤醒...")
                        await self.wake_up_service()
                        consecutive_failures = 0  # 重置计数
                
                # 等待下次检查
                await asyncio.sleep(check_interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 监控已手动停止")
                break
            except Exception as e:
                logger.error(f"❌ 监控循环异常: {e}")
                await asyncio.sleep(60)  # 出错后等待1分钟再继续

async def main():
    """主函数"""
    # 服务URL - 请替换为您的实际URL
    service_url = "https://seo-agent-pro-jsyb.onrender.com"
    
    monitor = ServiceMonitor(service_url)
    await monitor.monitor_loop()

if __name__ == "__main__":
    print("🚀 SEO Agent Pro 外部监控启动")
    print("📝 此脚本将持续监控服务状态并自动唤醒休眠的应用")
    print("⚠️ 请在本地或其他服务器上运行此脚本")
    print("🛑 按 Ctrl+C 停止监控")
    
    asyncio.run(main())
