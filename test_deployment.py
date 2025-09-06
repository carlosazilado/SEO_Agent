"""
部署前测试脚本
测试所有核心功能是否正常工作
"""

import requests
import time
import json

def test_application():
    base_url = "http://localhost:8000"
    
    print("🧪 开始SEO Agent Pro功能测试...")
    
    # 1. 测试主页
    print("\n1. 测试主页访问...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ 主页访问成功")
        else:
            print(f"❌ 主页访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 主页访问异常: {e}")
        return False
    
    # 2. 测试异步分析
    print("\n2. 测试异步分析...")
    try:
        # 启动异步分析
        response = requests.post(f"{base_url}/analyze/async", 
                               data={"url": "https://example.com"})
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get('task_id')
            print(f"✅ 异步分析启动成功，任务ID: {task_id}")
            
            # 检查任务状态
            print("   监控任务进度...")
            for i in range(10):  # 最多等待10次
                status_response = requests.get(f"{base_url}/task/{task_id}/status")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    progress = status_data.get('progress', 0)
                    status = status_data.get('status', 'unknown')
                    step = status_data.get('current_step', '')
                    
                    print(f"   进度: {progress}% - {status} - {step}")
                    
                    if status in ['completed', 'failed']:
                        break
                        
                    time.sleep(3)  # 等待3秒
                else:
                    print(f"   ❌ 状态检查失败: {status_response.status_code}")
                    break
            
        else:
            print(f"❌ 异步分析启动失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 异步分析测试异常: {e}")
        return False
    
    # 3. 测试历史记录
    print("\n3. 测试历史记录...")
    try:
        response = requests.get(f"{base_url}/history")
        if response.status_code == 200:
            print("✅ 历史记录页面访问成功")
        else:
            print(f"❌ 历史记录访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 历史记录测试异常: {e}")
        return False
    
    # 4. 测试API统计
    print("\n4. 测试API统计...")
    try:
        response = requests.get(f"{base_url}/api/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 统计API成功: {stats}")
        else:
            print(f"❌ 统计API失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 统计API测试异常: {e}")
        return False
    
    print("\n🎉 所有测试通过！应用可以正常部署。")
    return True

if __name__ == "__main__":
    print("请确保应用正在运行在 http://localhost:8000")
    print("运行命令: python app.py")
    input("按回车键开始测试...")
    
    success = test_application()
    
    if success:
        print("\n✅ 测试完成，应用准备就绪！")
    else:
        print("\n❌ 测试失败，请检查应用状态。")
