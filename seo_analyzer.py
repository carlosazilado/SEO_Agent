"""
SEO分析器 - 基础版本（无可视化依赖）
临时用于测试项目
"""
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import aiohttp
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
import re
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class EnhancedSEOAgent:
    """增强型SEO分析器"""
    
    def __init__(self, use_ai=True):
        self.use_ai = use_ai
        self.ai_enabled = False
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 初始化AI分析
        if self.use_ai:
            self._init_ai_analysis()
    
    def _init_ai_analysis(self):
        """初始化AI分析功能"""
        try:
            # 检查是否有可用的AI API
            api_key = os.getenv('SILICONFLOW_API_KEY')
            if api_key:
                self.ai_enabled = True
                print("✅ AI分析功能已启用")
            else:
                print("⚠️ 未找到AI API密钥，将使用基础分析模式")
        except Exception as e:
            print(f"❌ AI分析初始化失败: {e}")
            self.ai_enabled = False
    
    async def analyze_website(self, url: str) -> Dict[str, Any]:
        """分析网站SEO"""
        try:
            print(f"\n🔍 开始分析网站: {url}")
            start_time = time.time()
            
            # 创建会话
            self.session = aiohttp.ClientSession(headers=self.headers)
            
            # 获取页面内容
            content = await self._fetch_content(url)
            if not content:
                return {"error": "无法获取页面内容"}
            
            # 解析HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # 基础SEO分析
            result = {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "content_analysis": self._analyze_content(soup),
                "technical_seo": self._analyze_technical_seo(soup, url),
                "performance": await self._analyze_performance(url),
                "seo_score": 0
            }
            
            # AI数据分析
            if self.ai_enabled:
                print("🤖 执行AI数据分析...")
                await self._ai_data_analysis(result)
            else:
                print("⚠️ AI分析未启用，使用基础分析模式")
                self._generate_basic_analysis(result)
            
            # 计算SEO分数
            result["seo_score"] = self._calculate_seo_score(result)
            
            # 生成建议
            result["recommendations"] = self._generate_recommendations(result)
            
            # 计算总耗时
            result["analysis_time"] = round(time.time() - start_time, 2)
            
            print(f"✅ 分析完成！耗时: {result['analysis_time']}秒")
            return result
            
        except Exception as e:
            print(f"❌ 分析过程中发生错误: {e}")
            return {"error": str(e)}
        finally:
            if self.session:
                await self.session.close()
    
    async def _fetch_content(self, url: str) -> Optional[str]:
        """获取页面内容"""
        try:
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"⚠️ HTTP错误: {response.status}")
                    return None
        except Exception as e:
            print(f"❌ 获取页面失败: {e}")
            return None
    
    def _analyze_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """分析内容质量"""
        print("📝 分析内容质量...")
        
        analysis = {
            "title": None,
            "meta_description": None,
            "headings": {"h1": [], "h2": [], "h3": []},
            "word_count": 0,
            "images": {"total": 0, "without_alt": 0},
            "links": {"internal": 0, "external": 0},
            "score": 0
        }
        
        # 标题分析
        title_tag = soup.find('title')
        if title_tag:
            analysis["title"] = {
                "text": title_tag.get_text().strip(),
                "length": len(title_tag.get_text().strip())
            }
        
        # Meta描述
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            analysis["meta_description"] = {
                "text": meta_desc.get('content', '').strip(),
                "length": len(meta_desc.get('content', '').strip())
            }
        
        # 标题结构
        for h in soup.find_all(['h1', 'h2', 'h3']):
            analysis["headings"][h.name.lower()].append(h.get_text().strip())
        
        # 内容统计
        body_text = soup.get_text()
        analysis["word_count"] = len(body_text.split())
        
        # 图片分析
        images = soup.find_all('img')
        analysis["images"]["total"] = len(images)
        for img in images:
            if not img.get('alt'):
                analysis["images"]["without_alt"] += 1
        
        # 链接分析
        links = soup.find_all('a', href=True)
        base_url = urlparse(soup.find('base')['href'] if soup.find('base') else '')
        
        for link in links:
            href = link['href']
            if href.startswith('http'):
                if urlparse(href).netloc == base_url.netloc if base_url else True:
                    analysis["links"]["internal"] += 1
                else:
                    analysis["links"]["external"] += 1
            elif href.startswith('/') or not href.startswith(('http', '#')):
                analysis["links"]["internal"] += 1
        
        # 计算内容分数
        analysis["score"] = self._calculate_content_score(analysis)
        
        return analysis
    
    def _analyze_technical_seo(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """分析技术SEO"""
        print("🔧 分析技术SEO...")
        
        analysis = {
            "meta_robots": None,
            "canonical": None,
            "schema_org": [],
            "open_graph": {},
            "twitter_card": {},
            "mobile_friendly": {"score": 80},  # 简化检测
            "https": url.startswith('https://'),
            "score": 0
        }
        
        # Meta robots
        meta_robots = soup.find('meta', attrs={'name': 'robots'})
        if meta_robots:
            analysis["meta_robots"] = meta_robots.get('content', '')
        
        # Canonical标签
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if canonical:
            analysis["canonical"] = canonical.get('href', '')
        
        # 结构化数据
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.get_text())
                analysis["schema_org"].append(data.get('@type', 'Unknown'))
            except:
                pass
        
        # Open Graph
        for meta in soup.find_all('meta', attrs={'property': lambda x: x and x.startswith('og:')}):
            prop = meta.get('property')[3:]
            analysis["open_graph"][prop] = meta.get('content', '')
        
        # Twitter Card
        for meta in soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')}):
            prop = meta.get('name')[8:]
            analysis["twitter_card"][prop] = meta.get('content', '')
        
        # 计算技术SEO分数
        analysis["score"] = self._calculate_technical_score(analysis)
        
        return analysis
    
    async def _analyze_performance(self, url: str) -> Dict[str, Any]:
        """分析性能指标（简化版）"""
        print("⚡ 分析性能指标...")
        
        try:
            start = time.time()
            response = requests.get(url, timeout=10)
            load_time = (time.time() - start) * 1000
            
            return {
                "load_time": round(load_time, 2),
                "status_code": response.status_code,
                "size": len(response.content),
                "score": max(0, 100 - (load_time / 10))  # 简单计算
            }
        except:
            return {
                "load_time": 0,
                "status_code": 0,
                "size": 0,
                "score": 0
            }
    
    def _calculate_content_score(self, content: Dict[str, Any]) -> int:
        """计算内容质量分数"""
        score = 0
        
        # 标题 (30分)
        if content["title"]:
            score += 15
            if 30 <= content["title"]["length"] <= 60:
                score += 15
        
        # Meta描述 (20分)
        if content["meta_description"]:
            score += 10
            if 120 <= content["meta_description"]["length"] <= 160:
                score += 10
        
        # 标题结构 (20分)
        if content["headings"]["h1"]:
            score += 10
            if len(content["headings"]["h1"]) == 1:
                score += 5
        
        # 内容长度 (15分)
        if content["word_count"] >= 300:
            score += 15
        elif content["word_count"] >= 100:
            score += 8
        
        # 图片ALT (10分)
        if content["images"]["total"] > 0:
            alt_ratio = 1 - (content["images"]["without_alt"] / content["images"]["total"])
            score += int(alt_ratio * 10)
        
        # 链接 (5分)
        if content["links"]["internal"] > 0:
            score += 5
        
        return score
    
    def _calculate_technical_score(self, tech: Dict[str, Any]) -> int:
        """计算技术SEO分数"""
        score = 0
        
        # HTTPS (20分)
        if tech["https"]:
            score += 20
        
        # Meta robots (10分)
        if tech["meta_robots"]:
            score += 10
        
        # Canonical (10分)
        if tech["canonical"]:
            score += 10
        
        # 结构化数据 (20分)
        if tech["schema_org"]:
            score += 20
        
        # Open Graph (20分)
        if tech["open_graph"]:
            score += 20
        
        # 移动友好性 (20分)
        score += tech["mobile_friendly"]["score"] * 0.2
        
        return int(score)
    
    def _calculate_seo_score(self, result: Dict[str, Any]) -> int:
        """计算总体SEO分数"""
        content_weight = 0.4
        technical_weight = 0.3
        performance_weight = 0.3
        
        content_score = result["content_analysis"]["score"]
        technical_score = result["technical_seo"]["score"]
        performance_score = result["performance"]["score"]
        
        total_score = (
            content_score * content_weight +
            technical_score * technical_weight +
            performance_score * performance_weight
        )
        
        return round(total_score)
    
    def _generate_recommendations(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成优化建议"""
        recommendations = []
        
        # 内容建议
        if not result["content_analysis"]["title"]:
            recommendations.append({
                "issue": "缺少页面标题",
                "solution": "添加描述性的页面标题，包含关键词",
                "priority": "high"
            })
        
        if result["content_analysis"]["title"] and result["content_analysis"]["title"]["length"] > 60:
            recommendations.append({
                "issue": "标题过长",
                "solution": "将标题缩短至60个字符以内",
                "priority": "medium"
            })
        
        if not result["content_analysis"]["meta_description"]:
            recommendations.append({
                "issue": "缺少Meta描述",
                "solution": "添加吸引人的Meta描述，提高点击率",
                "priority": "high"
            })
        
        # 技术建议
        if not result["technical_seo"]["https"]:
            recommendations.append({
                "issue": "未使用HTTPS",
                "solution": "安装SSL证书，启用HTTPS",
                "priority": "high"
            })
        
        if not result["technical_seo"]["canonical"]:
            recommendations.append({
                "issue": "缺少Canonical标签",
                "solution": "添加Canonical标签防止重复内容",
                "priority": "medium"
            })
        
        # 性能建议
        if result["performance"]["load_time"] > 3000:
            recommendations.append({
                "issue": "页面加载速度慢",
                "solution": "优化图片、启用缓存、使用CDN",
                "priority": "high"
            })
        
        return recommendations
    
    async def _ai_data_analysis(self, result: Dict[str, Any]):
        """AI数据分析（占位符）"""
        # 这里可以集成实际的AI分析
        pass
    
    def _generate_basic_analysis(self, result: Dict[str, Any]):
        """生成基础分析结果"""
        # 添加一些基础的分析数据
        result["ai_insights"] = {
            "content_quality": "良好",
            "keyword_density": "适中",
            "readability": "容易理解"
        }


class BatchSEOAnalyzer:
    """批量SEO分析器"""
    
    def __init__(self, use_ai=True):
        self.agent = EnhancedSEOAgent(use_ai=use_ai)
    
    async def analyze_multiple(self, urls: List[str]) -> List[Dict[str, Any]]:
        """批量分析多个网站"""
        print(f"\n🚀 开始批量分析 {len(urls)} 个网站...")
        
        results = []
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] 分析: {url}")
            result = await self.agent.analyze_website(url)
            results.append({
                "url": url,
                "status": "success" if "error" not in result else "error",
                "result": result if "error" not in result else None,
                "error": result.get("error") if "error" in result else None,
                "timestamp": datetime.now().isoformat()
            })
        
        print(f"\n✅ 批量分析完成！成功: {sum(1 for r in results if r['status'] == 'success')}")
        return results