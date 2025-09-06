from fastapi import FastAPI, Request, Form, UploadFile, File, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
import uvicorn
import asyncio
import json
import sqlite3
from pathlib import Path
import uuid
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
import logging
import traceback
from typing import List, Optional

# 导入SEO分析器
from seo_analyzer import EnhancedSEOAnalyzer, BatchSEOAnalyzer
from database import init_db, save_analysis, get_analysis_history
from task_manager import task_manager, start_analysis_task
from keep_alive import start_keep_alive, stop_keep_alive

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('seo_agent.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SEO Agent Pro",
    description="智能SEO分析系统 - 增强版",
    version="2.0.0"
)

# 静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 初始化数据库
init_db()

# AI配置
AI_CONFIG = {
    'provider': 'siliconflow',
    'model': 'Qwen/Qwen2.5-VL-72B-Instruct',
    'api_key': os.getenv('SILICONFLOW_API_KEY', 'sk-fxeehbzkospkgoluchoqgxgkszkjaluozkohofghkzrqianx')
}

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "服务器内部错误", "message": str(exc)}
    )

# 应用生命周期事件
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("🚀 SEO Agent Pro 启动中...")
    # 启动保活服务
    await start_keep_alive()
    logger.info("✅ 应用启动完成")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("🔄 SEO Agent Pro 正在关闭...")
    # 停止保活服务
    stop_keep_alive()
    logger.info("✅ 应用关闭完成")

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "SEO Agent Pro",
        "version": "2.0.0"
    }

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """首页"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze")
async def analyze_url(
    request: Request,
    url: str = Form(...),
    batch_urls: str = Form(default=""),
    use_ai: bool = Form(default=True)
):
    """单个或批量URL分析"""
    logger.info(f"开始分析URL: {url}")
    
    urls = [url.strip()]
    
    # 处理批量URL
    if batch_urls:
        batch_list = [u.strip() for u in batch_urls.split('\n') if u.strip()]
        urls.extend(batch_list)
        logger.info(f"批量分析模式，共{len(urls)}个URL")
    
    results = []
    
    # 使用批量分析器
    batch_analyzer = BatchSEOAnalyzer(use_ai=use_ai)
    
    try:
        # 执行批量分析
        analysis_results = await batch_analyzer.analyze_multiple(urls)
        
        # 处理结果并保存到数据库
        for i, result in enumerate(analysis_results):
            target_url = urls[i]
            
            if result.get('status') == 'error':
                results.append({
                    "url": target_url,
                    "error": result.get('error', '分析失败'),
                    "status": "error"
                })
            else:
                # 从批量分析结果中提取实际的分析数据
                actual_result = result.get('result', {})
                
                # 保存到数据库
                analysis_id = str(uuid.uuid4())
                
                # 修正评分获取逻辑
                seo_score = actual_result.get('overall_score', 0)
                if seo_score == 0:
                    # 尝试从summary中获取
                    seo_score = actual_result.get('summary', {}).get('overall_score', 0)
                
                # 调试信息
                logger.info(f"调试 - result类型: {type(result)}")
                logger.info(f"调试 - result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                logger.info(f"调试 - actual_result类型: {type(actual_result)}")
                if isinstance(actual_result, dict):
                    logger.info(f"调试 - actual_result keys: {list(actual_result.keys())}")
                    logger.info(f"调试 - overall_score: {actual_result.get('overall_score', '未找到')}")
                    if 'summary' in actual_result:
                        logger.info(f"调试 - summary内容: {actual_result['summary']}")
                
                save_analysis(analysis_id, target_url, actual_result, seo_score, use_ai)
                
                logger.info(f"分析完成: {target_url}, SEO评分: {seo_score}")
                
                results.append({
                    "url": target_url,
                    "analysis_id": analysis_id,
                    "result": actual_result,
                    "status": "success"
                })
                
    except Exception as e:
        logger.error(f"批量分析失败: {str(e)}", exc_info=True)
        results.append({
            "url": url,
            "error": str(e),
            "status": "error"
        })
    
    logger.info("所有URL分析完成")
    return templates.TemplateResponse("results.html", {
        "request": request,
        "results": results
    })

@app.get("/report/{analysis_id}")
async def get_report(analysis_id: str):
    """获取详细报告"""
    # 从数据库获取分析结果
    conn = sqlite3.connect("seo_analysis.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return JSONResponse(content={"error": "Report not found"}, status_code=404)
    
    analysis_data = json.loads(result[3])  # analysis_result字段
    
    # 生成增强的HTML报告
    html_report = generate_enhanced_report(analysis_data)
    
    return HTMLResponse(content=html_report)

@app.get("/download/{analysis_id}")
async def download_report(analysis_id: str):
    """下载报告"""
    # 从数据库获取分析结果
    conn = sqlite3.connect("seo_analysis.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return JSONResponse(content={"error": "Report not found"}, status_code=404)
    
    analysis_data = json.loads(result[3])
    
    # 生成HTML报告并保存到文件
    html_report = generate_enhanced_report(analysis_data)
    
    # 确保reports目录存在
    os.makedirs("reports", exist_ok=True)
    
    report_path = f"reports/seo_report_{analysis_id}.html"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    return FileResponse(
        report_path,
        media_type='text/html',
        filename=f"seo_report_{analysis_data.get('url', 'unknown').replace('https://', '').replace('http://', '')}.html"
    )

@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    """历史记录页面"""
    try:
        # 获取历史记录
        history_data = get_analysis_history()
        
        # 计算统计信息
        total_analyses = len(history_data)
        successful_analyses = len([h for h in history_data if h.get('seo_score')])
        avg_score = 0
        
        if successful_analyses > 0:
            scores = [h.get('seo_score', 0) for h in history_data if h.get('seo_score')]
            avg_score = sum(scores) / len(scores)
        
        return templates.TemplateResponse("history.html", {
            "request": request,
            "history": history_data,
            "stats": {
                "total": total_analyses,
                "successful": successful_analyses,
                "failed": total_analyses - successful_analyses,
                "avg_score": round(avg_score, 1)
            }
        })
    except Exception as e:
        logger.error(f"获取历史记录失败: {str(e)}", exc_info=True)
        return templates.TemplateResponse("history.html", {
            "request": request,
            "history": [],
            "stats": {"total": 0, "successful": 0, "failed": 0, "avg_score": 0},
            "error": str(e)
        })

# ============ 新增异步分析端点 ============

@app.post("/analyze/async")
async def analyze_url_async(url: str = Form(...)):
    """启动异步URL分析"""
    try:
        # 创建异步分析任务
        task_id = start_analysis_task(url)
        
        return JSONResponse(content={
            "task_id": task_id,
            "message": "分析任务已启动",
            "status": "started"
        })
    except Exception as e:
        logger.error(f"启动异步分析失败: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "启动分析失败", "message": str(e)}
        )

@app.get("/task/{task_id}/status")
async def get_task_status(task_id: str):
    """获取任务状态和进度"""
    task_dict = task_manager.get_task_dict(task_id)
    
    if not task_dict:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )
    
    return JSONResponse(content=task_dict)

@app.get("/progress", response_class=HTMLResponse)
async def progress_page(request: Request):
    """进度页面"""
    return templates.TemplateResponse("progress.html", {"request": request})

@app.get("/task/{task_id}/result")
async def get_task_result(task_id: str):
    """获取完成的任务结果"""
    task = task_manager.get_task(task_id)
    
    if not task:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )
    
    if task.status.value != "completed":
        return JSONResponse(
            status_code=400,
            content={
                "error": "Task not completed",
                "status": task.status.value,
                "progress": task.progress
            }
        )
    
    # 只在首次完成时保存结果到数据库
    analysis_id = None
    if task.result and not hasattr(task, 'analysis_id'):
        analysis_id = str(uuid.uuid4())
        seo_score = task.result.get('overall_score', 0)
        
        try:
            save_analysis(analysis_id, task.url, task.result, seo_score, True)
            # 将analysis_id保存到task对象，避免重复保存
            task.analysis_id = analysis_id
            logger.info(f"异步分析结果已保存: {task.url}, 评分: {seo_score}")
        except Exception as e:
            logger.error(f"保存异步分析结果失败: {str(e)}")
    else:
        # 使用已保存的analysis_id
        analysis_id = getattr(task, 'analysis_id', None)
    
    return JSONResponse(content={
        "task_id": task_id,
        "result": task.result,
        "analysis_id": analysis_id if task.result else None
    })

@app.get("/api/stats")
async def get_stats():
    """获取统计信息API"""
    try:
        conn = sqlite3.connect("seo_analysis.db")
        cursor = conn.cursor()
        
        # 总分析数
        cursor.execute("SELECT COUNT(*) FROM analyses")
        total = cursor.fetchone()[0]
        
        # 成功分析数
        cursor.execute("SELECT COUNT(*) FROM analyses WHERE json_extract(analysis_result, '$.seo_score') IS NOT NULL")
        successful = cursor.fetchone()[0]
        
        # 平均分
        cursor.execute("SELECT AVG(json_extract(analysis_result, '$.seo_score')) FROM analyses WHERE json_extract(analysis_result, '$.seo_score') IS NOT NULL")
        avg_score = cursor.fetchone()[0] or 0
        
        # 今日分析数
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM analyses WHERE date(timestamp) = ?", (today,))
        today_count = cursor.fetchone()[0]
        
        conn.close()
        
        return JSONResponse({
            "total": total,
            "successful": successful,
            "failed": total - successful,
            "avg_score": round(avg_score, 1),
            "today": today_count
        })
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)

@app.delete("/api/history/{analysis_id}")
async def delete_history(analysis_id: str):
    """删除历史记录"""
    try:
        conn = sqlite3.connect("seo_analysis.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
        conn.commit()
        conn.close()
        
        return JSONResponse({"success": True})
    except Exception as e:
        logger.error(f"删除历史记录失败: {str(e)}", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)

# 添加兼容性路由，匹配前端模板中的路径
@app.get("/view_report/{analysis_id}")
async def view_report_compat(analysis_id: str):
    """查看报告 - 兼容路由"""
    return await get_report(analysis_id)

@app.get("/download_report/{analysis_id}")
async def download_report_compat(analysis_id: str):
    """下载报告 - 兼容路由"""
    return await download_report(analysis_id)

@app.post("/delete_record/{analysis_id}")
async def delete_record_compat(analysis_id: str):
    """删除记录 - 兼容路由"""
    return await delete_history(analysis_id)

@app.post("/clear_history")
async def clear_history():
    """清空历史记录"""
    try:
        conn = sqlite3.connect("seo_analysis.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analyses")
        conn.commit()
        conn.close()
        
        return JSONResponse({"success": True, "message": "历史记录已清空"})
    except Exception as e:
        logger.error(f"清空历史记录失败: {str(e)}", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/batch-report")
async def get_batch_report(request: Request, ids: str):
    """生成批量分析报告"""
    try:
        analysis_ids = ids.split(',')
        reports = []
        
        for analysis_id in analysis_ids:
            conn = sqlite3.connect("seo_analysis.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id.strip(),))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                analysis_data = json.loads(result[3])
                reports.append(analysis_data)
        
        # 生成批量对比报告
        batch_report_html = generate_batch_report(reports)
        
        return HTMLResponse(content=batch_report_html)
        
    except Exception as e:
        logger.error(f"生成批量报告失败: {str(e)}", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)

def generate_enhanced_report(data: dict) -> str:
    """生成增强的HTML报告"""
    # 基础信息
    url = data.get('url', '')
    
    # 修正评分获取逻辑
    seo_score = data.get('overall_score', 0)
    if seo_score == 0:
        # 尝试从summary中获取
        seo_score = data.get('summary', {}).get('overall_score', 0)
    if seo_score == 0:
        # 尝试从其他可能的位置获取
        seo_score = data.get('seo_score', 0)
    
    timestamp = data.get('timestamp', '')
    
    # 基础数据
    basic_data = data.get('basic_data', {})
    title = basic_data.get('title', {}).get('text', '无标题')
    meta_desc = basic_data.get('meta_description', {}).get('text', '无描述')
    
    # 技术SEO
    technical_seo = data.get('technical_seo', {})
    mobile_friendly = technical_seo.get('mobile_friendly', {}).get('score', 0)
    
    # 内容分析
    content_analysis = data.get('content_analysis', {})
    word_count = content_analysis.get('word_count', 0)
    readability = content_analysis.get('readability', {}).get('level', '未知')
    
    # 性能数据
    performance = data.get('performance', {})
    load_time = performance.get('total_load_time', 0)
    
    # 流量数据
    traffic_data = data.get('traffic_data', {})
    global_rank = traffic_data.get('global_rank', 'N/A')
    monthly_visits = traffic_data.get('monthly_visits', 0)
    
    # AI分析结果 - 修正字段名称
    ai_analysis = {}
    
    # 从数据中提取AI分析结果
    if 'analysis' in data:
        ai_analysis['analysis'] = data['analysis']
    if 'strategy' in data:
        ai_analysis['strategy'] = data['strategy'] 
    if 'html_report' in data:
        ai_analysis['html_report'] = data['html_report']
    
    # 如果没有AI分析数据，尝试从其他字段获取
    if not ai_analysis and 'ai_analysis' in data:
        ai_analysis = data['ai_analysis']
    
    # 生成HTML
    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO分析报告 - {url}</title>
    <style>
        {get_report_styles()}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="report-container">
        <header class="report-header">
            <h1>SEO分析报告</h1>
            <div class="report-info">
                <div class="url">{url}</div>
                <div class="timestamp">分析时间: {timestamp[:19]}</div>
            </div>
        </header>
        
        <section class="summary">
            <h2>执行摘要</h2>
            <div class="score-circle">
                <div class="score-value {get_score_class(seo_score)}">{seo_score}</div>
                <div class="score-label">SEO评分</div>
            </div>
            <div class="metrics">
                <div class="metric">
                    <div class="metric-value">{word_count}</div>
                    <div class="metric-label">内容字数</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{load_time:.2f}s</div>
                    <div class="metric-label">加载时间</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{global_rank}</div>
                    <div class="metric-label">全球排名</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{monthly_visits:,}</div>
                    <div class="metric-label">月访问量</div>
                </div>
            </div>
        </section>
        
        <section class="details">
            <h2>详细分析</h2>
            
            <div class="card">
                <h3>基础SEO</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="label">页面标题:</span>
                        <span class="value">{title}</span>
                    </div>
                    <div class="info-item">
                        <span class="label">Meta描述:</span>
                        <span class="value">{meta_desc}</span>
                    </div>
                    <div class="info-item">
                        <span class="label">移动友好:</span>
                        <span class="value">{mobile_friendly}%</span>
                    </div>
                    <div class="info-item">
                        <span class="label">内容可读性:</span>
                        <span class="value">{readability}</span>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>技术SEO</h3>
                <div class="tech-info">
                    <div class="tech-item">
                        <i class="fas fa-lock"></i>
                        <span>HTTPS: {'✓' if technical_seo.get('https') else '✗'}</span>
                    </div>
                    <div class="tech-item">
                        <i class="fas fa-link"></i>
                        <span>Canonical: {'✓' if technical_seo.get('canonical') else '✗'}</span>
                    </div>
                    <div class="tech-item">
                        <i class="fas fa-globe"></i>
                        <span>Hreflang: {len(technical_seo.get('hreflang', []))} 个</span>
                    </div>
                    <div class="tech-item">
                        <i class="fas fa-code"></i>
                        <span>结构化数据: {len(technical_seo.get('structured_data', []))} 个</span>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>性能指标</h3>
                <canvas id="performanceChart"></canvas>
                <script>
                    {get_performance_chart(performance)}
                </script>
            </div>
            
            <div class="card">
                <h3>关键词分析</h3>
                <div class="keywords">
                    {generate_keyword_cloud(content_analysis.get('keyword_density', {}))}
                </div>
            </div>
            
            {'<div class="card"><h3>AI智能分析</h3><div class="ai-analysis">' + format_ai_analysis(ai_analysis) + '</div></div>' if ai_analysis else ''}
            
            <div class="card">
                <h3>优化建议</h3>
                <div class="recommendations">
    """
    
    # 添加优化建议
    for rec in data.get('recommendations', []):
        priority_class = rec.get('priority', 'medium')
        html += f"""
                    <div class="recommendation priority-{priority_class}">
                        <div class="priority">{priority_class.upper()}</div>
                        <div class="issue">{rec.get('issue', '')}</div>
                        <div class="solution">{rec.get('solution', '')}</div>
                    </div>
        """
    
    html += """
                </div>
            </div>
        </section>
        
        <footer class="report-footer">
            <p>由 SEO Agent Pro 生成 | 基于AI智能分析技术</p>
        </footer>
    </div>
</body>
</html>
    """
    
    return html

def get_report_styles() -> str:
    """报告CSS样式"""
    return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }
        
        .report-container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        
        .report-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem;
            text-align: center;
        }
        
        .report-header h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        
        .report-info {
            margin-top: 2rem;
        }
        
        .url {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .timestamp {
            margin-top: 0.5rem;
            opacity: 0.8;
        }
        
        .summary {
            padding: 3rem;
            text-align: center;
            background: #fafafa;
        }
        
        .score-circle {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            margin: 0 auto 2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            font-weight: bold;
        }
        
        .score-value {
            font-size: 3rem;
        }
        
        .score-excellent {
            background: linear-gradient(135deg, #10b981, #34d399);
            color: white;
        }
        
        .score-good {
            background: linear-gradient(135deg, #f59e0b, #fbbf24);
            color: white;
        }
        
        .score-poor {
            background: linear-gradient(135deg, #ef4444, #f87171);
            color: white;
        }
        
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }
        
        .metric {
            text-align: center;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .metric-label {
            color: #666;
            margin-top: 0.5rem;
        }
        
        .details {
            padding: 3rem;
        }
        
        .details h2 {
            text-align: center;
            margin-bottom: 3rem;
            color: #333;
        }
        
        .card {
            background: white;
            border-radius: 10px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .card h3 {
            margin-bottom: 1.5rem;
            color: #444;
        }
        
        .info-grid {
            display: grid;
            gap: 1rem;
        }
        
        .info-item {
            display: flex;
            padding: 0.75rem;
            background: #f8f9fa;
            border-radius: 5px;
        }
        
        .label {
            font-weight: 600;
            min-width: 120px;
            color: #666;
        }
        
        .value {
            flex: 1;
        }
        
        .tech-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }
        
        .tech-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 5px;
        }
        
        .tech-item i {
            color: #667eea;
        }
        
        .recommendations {
            display: grid;
            gap: 1rem;
        }
        
        .recommendation {
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        .priority-high {
            border-left-color: #ef4444;
            background: #fef2f2;
        }
        
        .priority-medium {
            border-left-color: #f59e0b;
            background: #fffbeb;
        }
        
        .priority-low {
            border-left-color: #10b981;
            background: #f0fdf4;
        }
        
        .priority {
            font-weight: bold;
            text-transform: uppercase;
            font-size: 0.875rem;
            margin-bottom: 0.5rem;
        }
        
        .issue {
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .solution {
            color: #666;
        }
        
        .ai-analysis {
            line-height: 1.8;
        }
        
        .ai-analysis h4 {
            margin: 1.5rem 0 1rem;
            color: #444;
        }
        
        .ai-analysis pre {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 5px;
            overflow-x: auto;
        }
        
        .report-footer {
            text-align: center;
            padding: 2rem;
            background: #f8f9fa;
            color: #666;
            border-top: 1px solid #eee;
        }
        
        @media (max-width: 768px) {
            .metrics {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .tech-info {
                grid-template-columns: 1fr;
            }
        }
    """

def get_score_class(score: int) -> str:
    """根据分数返回样式类"""
    if score >= 80:
        return 'score-excellent'
    elif score >= 60:
        return 'score-good'
    else:
        return 'score-poor'

def get_performance_chart(performance: dict) -> str:
    """生成性能图表JavaScript"""
    metrics = performance.get('metrics', {})
    
    return f"""
        const ctx = document.getElementById('performanceChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: ['DNS查询', 'TCP连接', '服务器响应', 'DOM加载', '页面加载'],
                datasets: [{{
                    label: '耗时 (ms)',
                    data: [
                        {metrics.get('dns_lookup', 0)},
                        {metrics.get('tcp_connection', 0)},
                        {metrics.get('server_response', 0)},
                        {metrics.get('dom_load', 0)},
                        {metrics.get('page_load', 0)}
                    ],
                    backgroundColor: 'rgba(102, 126, 234, 0.5)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
    """

def generate_keyword_cloud(keyword_density: dict) -> str:
    """生成关键词云HTML"""
    if not keyword_density:
        return '<p>无关键词数据</p>'
    
    html = '<div class="keyword-cloud">'
    for keyword, data in keyword_density.items():
        size = min(30, max(12, data.get('density', 0) * 100))
        html += f'<span style="font-size: {size}px; margin: 5px;">{keyword}</span>'
    html += '</div>'
    
    return html

def format_ai_analysis(ai_analysis: dict) -> str:
    """格式化AI分析结果"""
    if not ai_analysis:
        return '<div class="no-ai-analysis">暂无AI分析数据</div>'
    
    html = ''
    
    # 数据分析专家
    if 'analysis' in ai_analysis:
        html += '''
        <div class="ai-section">
            <h4><i class="fas fa-chart-line"></i> 数据分析专家</h4>
            <div class="ai-content">
        '''
        
        analysis = ai_analysis['analysis']
        if isinstance(analysis, str):
            # 处理字符串格式的分析
            html += f'<div class="analysis-text">{analysis}</div>'
        elif isinstance(analysis, dict):
            # 处理结构化数据
            for key, value in analysis.items():
                if key == 'insights':
                    html += '<div class="insights"><h5>🔍 关键洞察</h5><ul>'
                    if isinstance(value, list):
                        for insight in value:
                            html += f'<li>{insight}</li>'
                    html += '</ul></div>'
                elif key == 'scores':
                    html += '<div class="scores"><h5>📊 评分详情</h5><ul>'
                    if isinstance(value, dict):
                        for score_name, score_value in value.items():
                            html += f'<li><strong>{score_name}:</strong> {score_value}分</li>'
                    html += '</ul></div>'
                elif key == 'issues':
                    html += '<div class="issues"><h5>⚠️ 发现问题</h5><ul>'
                    if isinstance(value, list):
                        for issue in value:
                            html += f'<li>{issue}</li>'
                    html += '</ul></div>'
        
        html += '</div></div>'
    
    # 策略顾问
    if 'strategy' in ai_analysis:
        html += '''
        <div class="ai-section">
            <h4><i class="fas fa-lightbulb"></i> 策略优化顾问</h4>
            <div class="ai-content">
        '''
        
        strategy = ai_analysis['strategy']
        if isinstance(strategy, str):
            html += f'<div class="strategy-text">{strategy}</div>'
        elif isinstance(strategy, dict):
            # 处理策略建议
            if 'recommendations' in strategy:
                html += '<div class="recommendations"><h5>💡 优化建议</h5><div class="rec-list">'
                recommendations = strategy['recommendations']
                if isinstance(recommendations, list):
                    for i, rec in enumerate(recommendations, 1):
                        if isinstance(rec, dict):
                            priority = rec.get('priority', 'medium')
                            description = rec.get('description', '')
                            actions = rec.get('actions', [])
                            estimated_time = rec.get('estimated_time', '')
                            expected_effect = rec.get('expected_effect', '')
                            
                            html += f'''
                            <div class="recommendation-item priority-{priority}">
                                <div class="rec-header">
                                    <span class="rec-number">#{i}</span>
                                    <span class="rec-priority">{priority.upper()}</span>
                                </div>
                                <div class="rec-description">{description}</div>
                                {f'<div class="rec-actions"><strong>具体行动:</strong><ul>{"".join([f"<li>{action}</li>" for action in actions])}</ul></div>' if actions else ''}
                                {f'<div class="rec-time"><strong>预计时间:</strong> {estimated_time}</div>' if estimated_time else ''}
                                {f'<div class="rec-effect"><strong>预期效果:</strong> {expected_effect}</div>' if expected_effect else ''}
                            </div>
                            '''
                        else:
                            html += f'<div class="recommendation-item"><div class="rec-description">{rec}</div></div>'
                html += '</div></div>'
            
            if 'priority_matrix' in strategy:
                html += '<div class="priority-matrix"><h5>📋 优先级矩阵</h5>'
                matrix = strategy['priority_matrix']
                if isinstance(matrix, dict):
                    for level, items in matrix.items():
                        html += f'<div class="priority-level"><strong>{level}:</strong> {", ".join(items) if isinstance(items, list) else items}</div>'
                html += '</div>'
        
        html += '</div></div>'
    
    # 报告设计师
    if 'html_report' in ai_analysis:
        html += '''
        <div class="ai-section">
            <h4><i class="fas fa-file-alt"></i> 报告设计专家</h4>
            <div class="ai-content">
        '''
        
        report_data = ai_analysis['html_report']
        if isinstance(report_data, str):
            html += f'<div class="report-summary">{report_data}</div>'
        elif isinstance(report_data, dict):
            if 'summary' in report_data:
                html += f'<div class="report-summary"><h5>📋 报告摘要</h5><p>{report_data["summary"]}</p></div>'
            if 'key_metrics' in report_data:
                html += '<div class="key-metrics"><h5>📊 关键指标</h5><ul>'
                metrics = report_data['key_metrics']
                if isinstance(metrics, dict):
                    for metric, value in metrics.items():
                        html += f'<li><strong>{metric}:</strong> {value}</li>'
                html += '</ul></div>'
            if 'risk_assessment' in report_data:
                html += f'<div class="risk-assessment"><h5>⚠️ 风险评估</h5><p>{report_data["risk_assessment"]}</p></div>'
        
        html += '</div></div>'
    
    # 添加AI分析样式
    if html:
        html = f'''
        <style>
        .ai-section {{
            margin-bottom: 2rem;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
        }}
        .ai-section h4 {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: 0;
            padding: 1rem;
            font-size: 1.1rem;
        }}
        .ai-content {{
            padding: 1.5rem;
            background: #f9f9f9;
        }}
        .recommendation-item {{
            background: white;
            border-left: 4px solid #ddd;
            margin-bottom: 1rem;
            padding: 1rem;
            border-radius: 4px;
        }}
        .recommendation-item.priority-high {{
            border-left-color: #ff4757;
        }}
        .recommendation-item.priority-medium {{
            border-left-color: #ffa502;
        }}
        .recommendation-item.priority-low {{
            border-left-color: #2ed573;
        }}
        .rec-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }}
        .rec-number {{
            background: #667eea;
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 12px;
            font-size: 0.8rem;
        }}
        .rec-priority {{
            background: #f1f2f6;
            padding: 0.2rem 0.5rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: bold;
        }}
        .rec-description {{
            margin-bottom: 1rem;
            line-height: 1.6;
        }}
        .rec-actions ul {{
            margin: 0.5rem 0;
            padding-left: 1.5rem;
        }}
        .rec-time, .rec-effect {{
            margin-top: 0.5rem;
            font-size: 0.9rem;
            color: #666;
        }}
        .insights ul, .scores ul, .issues ul {{
            margin: 0.5rem 0;
            padding-left: 1.5rem;
        }}
        .priority-level {{
            margin-bottom: 0.5rem;
            padding: 0.5rem;
            background: white;
            border-radius: 4px;
        }}
        .no-ai-analysis {{
            text-align: center;
            color: #666;
            font-style: italic;
            padding: 2rem;
        }}
        </style>
        ''' + html
    
    return html

def generate_batch_report(reports: List[dict]) -> str:
    """生成批量对比报告"""
    if not reports:
        return '<h1>无数据</h1>'
    
    html = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>批量SEO分析报告</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 2rem;
            background: #f5f5f5;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 3rem;
        }
        
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }
        
        .summary-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            text-align: center;
        }
        
        .summary-card h3 {
            color: #666;
            margin-bottom: 0.5rem;
        }
        
        .summary-card .value {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .comparison-table {
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #444;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .score-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-weight: 600;
            color: white;
        }
        
        .score-excellent {
            background: #10b981;
        }
        
        .score-good {
            background: #f59e0b;
        }
        
        .score-poor {
            background: #ef4444;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>批量SEO分析报告</h1>
        
        <div class="summary-cards">
            <div class="summary-card">
                <h3>分析网站数</h3>
                <div class="value">{len(reports)}</div>
            </div>
            <div class="summary-card">
                <h3>平均SEO评分</h3>
                <div class="value">{round(sum(r.get('seo_score', 0) for r in reports) / len(reports), 1)}</div>
            </div>
            <div class="summary-card">
                <h3>最高评分</h3>
                <div class="value">{max(r.get('seo_score', 0) for r in reports)}</div>
            </div>
            <div class="summary-card">
                <h3>最低评分</h3>
                <div class="value">{min(r.get('seo_score', 0) for r in reports)}</div>
            </div>
        </div>
        
        <div class="comparison-table">
            <table>
                <thead>
                    <tr>
                        <th>网站</th>
                        <th>SEO评分</th>
                        <th>内容字数</th>
                        <th>加载时间</th>
                        <th>全球排名</th>
                        <th>移动友好</th>
                        <th>分析时间</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for report in reports:
        url = report.get('url', '')
        seo_score = report.get('seo_score', 0)
        word_count = report.get('content_analysis', {}).get('word_count', 0)
        load_time = report.get('performance', {}).get('total_load_time', 0)
        global_rank = report.get('traffic_data', {}).get('global_rank', 'N/A')
        mobile_score = report.get('technical_seo', {}).get('mobile_friendly', {}).get('score', 0)
        timestamp = report.get('timestamp', '')[:10]
        
        score_class = get_score_class(seo_score)
        
        html += f"""
                    <tr>
                        <td><a href="{url}" target="_blank">{url}</a></td>
                        <td><span class="score-badge {score_class}">{seo_score}</span></td>
                        <td>{word_count:,}</td>
                        <td>{load_time:.2f}s</td>
                        <td>{global_rank}</td>
                        <td>{mobile_score}%</td>
                        <td>{timestamp}</td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
    """
    
    return html

if __name__ == "__main__":
    # 检查环境变量
    if not os.getenv('SILICONFLOW_API_KEY'):
        print("⚠️  警告: 未设置 SILICONFLOW_API_KEY 环境变量")
        print("AI分析功能将不可用，将使用基础分析模式")
    
    print("🚀 启动 SEO Agent Pro 服务器...")
    
    # 获取端口配置（支持Render等云平台）
    port = int(os.getenv('PORT', 8000))
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f"🌐 访问地址: http://{host}:{port}")
    print("📊 管理面板: http://{host}:{port}/history")
    
    # 启动服务器 - 生产模式
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=False,  # 生产模式，关闭自动重载
        log_level="info",
        access_log=True  # 启用访问日志
    )