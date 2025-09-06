"""
紧急重启和恢复脚本
当应用出现502错误时的快速恢复方案
"""

import requests
import time
import sys
from datetime import datetime

class EmergencyRecovery:
    def __init__(self, app_url):
        self.app_url = app_url.rstrip('/')
        
    def check_status(self):
        """检查应用状态"""
        try:
            response = requests.get(f"{self.app_url}/health", timeout=30)
            if response.status_code == 200:
                return True, "应用正常运行"
            else:
                return False, f"应用返回状态码: {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "连接被拒绝 - 应用可能休眠或崩溃"
        except requests.exceptions.Timeout:
            return False, "请求超时"
        except Exception as e:
            return False, f"检查失败: {str(e)}"
    
    def wake_up(self):
        """唤醒应用"""
        print("🔄 正在尝试唤醒应用...")
        try:
            # 访问主页来唤醒应用
            response = requests.get(self.app_url, timeout=60)
            if response.status_code == 200:
                print("✅ 应用唤醒成功!")
                return True
            else:
                print(f"⚠️ 唤醒失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 唤醒失败: {e}")
            return False
    
    def force_restart(self):
        """强制重启应用（通过触发新部署）"""
        print("🚨 开始强制重启流程...")
        print("📝 请手动执行以下步骤:")
        print("1. 登录 render.com")
        print("2. 进入 SEO Agent Pro 服务页面")
        print("3. 点击 'Manual Deploy' 按钮")
        print("4. 等待重新部署完成")
        
    def recovery_loop(self, max_attempts=5):
        """恢复循环"""
        print(f"🚀 开始应用恢复流程...")
        print(f"📊 目标应用: {self.app_url}")
        print(f"🔄 最大尝试次数: {max_attempts}")
        print("-" * 50)
        
        for attempt in range(1, max_attempts + 1):
            print(f"\n📍 尝试 {attempt}/{max_attempts} - {datetime.now().strftime('%H:%M:%S')}")
            
            # 检查状态
            is_healthy, message = self.check_status()
            print(f"📊 状态检查: {message}")
            
            if is_healthy:
                print("🎉 应用已恢复正常！")
                return True
            
            # 尝试唤醒
            if self.wake_up():
                # 再次检查
                time.sleep(10)
                is_healthy, message = self.check_status()
                if is_healthy:
                    print("🎉 应用唤醒成功！")
                    return True
            
            if attempt < max_attempts:
                print(f"⏳ 等待30秒后重试...")
                time.sleep(30)
            else:
                print("❌ 自动恢复失败")
                self.force_restart()
                return False
        
        return False

def main():
    """主函数"""
    app_url = "https://seo-agent-pro-jsyb.onrender.com"
    
    if len(sys.argv) > 1:
        app_url = sys.argv[1]
    
    print("🆘 SEO Agent Pro 紧急恢复工具")
    print("=" * 50)
    
    recovery = EmergencyRecovery(app_url)
    success = recovery.recovery_loop()
    
    if success:
        print("\n✅ 恢复成功！应用现在应该可以正常访问。")
    else:
        print("\n❌ 自动恢复失败，需要手动干预。")
        print("\n📞 联系方案:")
        print("1. 检查 Render 控制台的部署日志")
        print("2. 手动触发重新部署")
        print("3. 检查环境变量配置")

if __name__ == "__main__":
    main()
