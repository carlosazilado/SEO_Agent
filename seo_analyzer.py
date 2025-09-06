"""
增强版SEO分析器
集成数据收集和AI分析功能
"""
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from seo_collector import SEODataCollector
from seo_agents import SEOAgentOrchestrator


class EnhancedSEOAnalyzer:
    """增强版SEO分析器"""
    
    def __init__(self, use_ai=True):
        self.use_ai = use_ai
        self.collector = SEODataCollector()
        self.orchestrator = SEOAgentOrchestrator() if use_ai else None
    
    async def analyze_website(self, url: str) -> Dict[str, Any]:
        """分析网站SEO"""
        try:
            print(f"\n🚀 开始AI SEO分析: {url}")
            start_time = time.time()
            
            # 数据收集阶段
            async with self.collector as collector:
                seo_data = await collector.collect_all_data(url)
            
            # 如果没有启用AI，返回基础数据
            if not self.use_ai or not self.orchestrator:
                return self._generate_basic_report(seo_data)
            
            # AI分析阶段
            ai_result = await self.orchestrator.run_full_analysis(seo_data)
            
            # 计算总耗时
            analysis_time = round(time.time() - start_time, 2)
            ai_result['analysis_time'] = analysis_time
            
            print(f"✅ AI SEO分析完成！耗时: {analysis_time}秒")
            return ai_result
            
        except Exception as e:
            print(f"❌ 分析过程中发生错误: {e}")
            return {"error": str(e)}
    
    def _generate_basic_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成基础分析报告（无AI）"""
        print("⚠️ 使用基础分析模式")
        
        # 计算基础评分
        scores = self._calculate_basic_scores(data)
        
        return {
            "url": data.get('url'),
            "timestamp": datetime.now().isoformat(),
            "mode": "basic",
            "scores": scores,
            "overall_score": sum(scores.values()) // len(scores) if scores else 0,
            "data": data,
            "recommendations": self._generate_basic_recommendations(data),
            "analysis_time": 0
        }
    
    def _calculate_basic_scores(self, data: Dict[str, Any]) -> Dict[str, int]:
        """计算基础评分"""
        scores = {
            'technical': 0,
            'content': 0,
            'performance': 0
        }
        
        # 技术SEO评分 (40%)
        tech_data = data.get('technical_seo', {})
        tech_score = 0
        
        # 检查基础技术要素
        if tech_data.get('robots_txt', {}).get('exists'):
            tech_score += 20
        if tech_data.get('sitemap', {}).get('exists'):
            tech_score += 20
        if tech_data.get('canonical'):
            tech_score += 20
        if tech_data.get('meta_tags', {}).get('viewport'):
            tech_score += 20
        if tech_data.get('html_structure', {}).get('has_doctype'):
            tech_score += 20
        
        scores['technical'] = min(100, tech_score)
        
        # 内容质量评分 (40%)
        content_data = data.get('content_analysis', {})
        content_score = 0
        
        # TDK分析
        tdk = content_data.get('tdk', {})
        if 30 <= tdk.get('title_length', 0) <= 60:
            content_score += 25
        if 100 <= tdk.get('description_length', 0) <= 160:
            content_score += 25
        
        # 图片优化
        images = content_data.get('images', {})
        if images.get('total', 0) > 0:
            alt_ratio = images.get('with_alt', 0) / images.get('total', 1)
            content_score += int(alt_ratio * 50)
        
        scores['content'] = min(100, content_score)
        
        # 性能评分 (20%)
        perf_data = data.get('performance', {})
        load_time = perf_data.get('page_load_time', 0)
        
        if load_time < 2:
            perf_score = 100
        elif load_time < 4:
            perf_score = 80
        elif load_time < 6:
            perf_score = 60
        else:
            perf_score = 40
        
        scores['performance'] = perf_score
        
        return scores
    
    def _generate_basic_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """生成基础建议"""
        recommendations = []
        
        # 技术建议
        tech_data = data.get('technical_seo', {})
        if not tech_data.get('robots_txt', {}).get('exists'):
            recommendations.append("添加robots.txt文件以指导搜索引擎爬取")
        
        if not tech_data.get('sitemap', {}).get('exists'):
            recommendations.append("创建sitemap.xml以帮助搜索引擎索引网站")
        
        if not tech_data.get('canonical'):
            recommendations.append("添加canonical标签避免重复内容问题")
        
        # 内容建议
        content_data = data.get('content_analysis', {})
        tdk = content_data.get('tdk', {})
        
        if tdk.get('title_length', 0) < 30 or tdk.get('title_length', 0) > 60:
            recommendations.append("优化标题长度，建议在30-60字符之间")
        
        if tdk.get('description_length', 0) < 100 or tdk.get('description_length', 0) > 160:
            recommendations.append("优化描述长度，建议在100-160字符之间")
        
        # 图片建议
        images = content_data.get('images', {})
        if images.get('without_alt', 0) > 0:
            recommendations.append(f"为{images.get('without_alt')}张图片添加ALT属性")
        
        # 性能建议
        perf_data = data.get('performance', {})
        load_time = perf_data.get('page_load_time', 0)
        
        if load_time > 3:
            recommendations.append("优化页面加载速度，建议压缩图片和启用缓存")
        
        return recommendations


class BatchSEOAnalyzer:
    """批量SEO分析器"""
    
    def __init__(self, use_ai=True):
        self.analyzer = EnhancedSEOAnalyzer(use_ai=use_ai)
    
    async def analyze_multiple(self, urls: List[str]) -> List[Dict[str, Any]]:
        """批量分析多个网站"""
        print(f"\n🚀 开始批量分析 {len(urls)} 个网站...")
        
        results = []
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] 分析: {url}")
            
            try:
                result = await self.analyzer.analyze_website(url)
                results.append({
                    "url": url,
                    "status": "success" if "error" not in result else "error",
                    "result": result if "error" not in result else None,
                    "error": result.get("error") if "error" in result else None,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                print(f"❌ 分析失败: {url} - {e}")
                results.append({
                    "url": url,
                    "status": "error",
                    "result": None,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        print(f"\n✅ 批量分析完成！成功: {success_count}/{len(urls)}")
        
        return results


def batch_analyze_urls(urls: List[str], use_ai=True) -> List[Dict[str, Any]]:
    """
    同步批量分析URL接口
    为了兼容现有的调用方式
    """
    analyzer = BatchSEOAnalyzer(use_ai=use_ai)
    
    # 运行异步分析
    try:
        # 创建新的事件循环（如果当前没有运行的循环）
        try:
            loop = asyncio.get_running_loop()
            # 如果已经有运行的事件循环，使用 run_in_executor
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, analyzer.analyze_multiple(urls))
                return future.result()
        except RuntimeError:
            # 没有运行的事件循环，直接运行
            return asyncio.run(analyzer.analyze_multiple(urls))
    except Exception as e:
        print(f"❌ 批量分析失败: {e}")
        return [{
            "url": url,
            "status": "error",
            "result": None,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        } for url in urls]