"""
异步分析任务管理器
用于处理耗时的SEO分析任务，提供进度跟踪和后台处理
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import json
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AnalysisTask:
    id: str
    url: str
    status: TaskStatus
    progress: int  # 0-100
    current_step: str
    result: Optional[Dict[Any, Any]] = None
    error: Optional[str] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, AnalysisTask] = {}
        self.max_tasks = 50  # 最多保存50个任务
    
    def create_task(self, url: str) -> str:
        """创建新的分析任务"""
        task_id = str(uuid.uuid4())
        task = AnalysisTask(
            id=task_id,
            url=url,
            status=TaskStatus.PENDING,
            progress=0,
            current_step="初始化分析任务..."
        )
        
        self.tasks[task_id] = task
        self._cleanup_old_tasks()
        
        logger.info(f"创建分析任务: {task_id} for URL: {url}")
        return task_id
    
    def get_task(self, task_id: str) -> Optional[AnalysisTask]:
        """获取任务状态"""
        return self.tasks.get(task_id)
    
    def update_progress(self, task_id: str, progress: int, step: str):
        """更新任务进度"""
        if task_id in self.tasks:
            self.tasks[task_id].progress = progress
            self.tasks[task_id].current_step = step
            if progress > 0:
                self.tasks[task_id].status = TaskStatus.RUNNING
            logger.info(f"任务 {task_id} 进度: {progress}% - {step}")
    
    def complete_task(self, task_id: str, result: Dict[Any, Any]):
        """标记任务完成"""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.COMPLETED
            self.tasks[task_id].progress = 100
            self.tasks[task_id].current_step = "分析完成"
            self.tasks[task_id].result = result
            self.tasks[task_id].completed_at = datetime.now()
            logger.info(f"任务 {task_id} 完成")
    
    def fail_task(self, task_id: str, error: str):
        """标记任务失败"""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.FAILED
            self.tasks[task_id].current_step = f"分析失败: {error}"
            self.tasks[task_id].error = error
            self.tasks[task_id].completed_at = datetime.now()
            logger.error(f"任务 {task_id} 失败: {error}")
    
    def get_task_dict(self, task_id: str) -> Optional[Dict]:
        """获取任务的字典表示"""
        task = self.get_task(task_id)
        if task:
            task_dict = asdict(task)
            # 转换枚举和日期时间为字符串
            task_dict['status'] = task.status.value
            task_dict['created_at'] = task.created_at.isoformat() if task.created_at else None
            task_dict['completed_at'] = task.completed_at.isoformat() if task.completed_at else None
            return task_dict
        return None
    
    def _cleanup_old_tasks(self):
        """清理旧任务，保持任务数量在限制内"""
        if len(self.tasks) > self.max_tasks:
            # 按创建时间排序，删除最旧的任务
            sorted_tasks = sorted(
                self.tasks.items(),
                key=lambda x: x[1].created_at
            )
            
            # 删除最旧的任务
            tasks_to_remove = len(self.tasks) - self.max_tasks + 1
            for i in range(tasks_to_remove):
                task_id = sorted_tasks[i][0]
                del self.tasks[task_id]
                logger.info(f"清理旧任务: {task_id}")

# 全局任务管理器实例
task_manager = TaskManager()

async def analyze_url_async(task_id: str, url: str):
    """异步分析URL"""
    try:
        from seo_analyzer import batch_analyze_urls
        
        # 更新进度
        task_manager.update_progress(task_id, 10, "初始化数据收集...")
        
        # 开始分析 - 使用线程池来运行同步函数
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(batch_analyze_urls, [url])
            
            # 模拟进度更新
            for i in range(20, 90, 10):
                await asyncio.sleep(5)  # 每5秒更新一次进度
                task_manager.update_progress(task_id, i, f"分析进行中... {i}%")
            
            # 获取结果
            result = future.result()
        
        if result and len(result) > 0:
            # 提取结果
            analysis_result = result[0]
            if analysis_result.get('status') == 'success':
                actual_result = analysis_result.get('result', {})
                task_manager.complete_task(task_id, actual_result)
            else:
                error_msg = analysis_result.get('error', '分析失败')
                task_manager.fail_task(task_id, error_msg)
        else:
            task_manager.fail_task(task_id, "分析返回空结果")
            
    except Exception as e:
        error_msg = f"分析过程出错: {str(e)}"
        logger.error(error_msg, exc_info=True)
        task_manager.fail_task(task_id, error_msg)

def start_analysis_task(url: str) -> str:
    """启动异步分析任务"""
    task_id = task_manager.create_task(url)
    
    # 在后台运行分析
    asyncio.create_task(analyze_url_async(task_id, url))
    
    return task_id
