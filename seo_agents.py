"""
AI SEO Agent系统
使用硅基流动API驱动三个专业AI Agent
"""
import os
import json
import asyncio
from typing import Dict, Any, List
from openai import OpenAI


class SEOAIAgent:
    """AI SEO Agent基类"""
    
    def __init__(self):
        # 使用硅基流动的API
        self.client = OpenAI(
            api_key=os.getenv('SILICONFLOW_API_KEY', 'sk-fxeehbzkospkgoluchoqgxgkszkjaluozkohofghkzrqianx'),
            base_url="https://api.siliconflow.cn/v1"
        )
        self.model = "Qwen/Qwen2.5-VL-72B-Instruct"
    
    async def call_ai(self, system_prompt: str, user_content: str) -> str:
        """调用AI API - 带超时保护"""
        try:
            # 添加超时保护，最多30秒
            import asyncio
            
            def _sync_call():
                return self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.7,
                    max_tokens=2000,  # 减少token数量
                    timeout=30  # 30秒超时
                )
            
            # 使用asyncio超时保护
            response = await asyncio.wait_for(
                asyncio.to_thread(_sync_call), 
                timeout=30
            )
            return response.choices[0].message.content
            
        except asyncio.TimeoutError:
            print("⏰ AI调用超时(30s)，返回默认分析")
            return "AI分析超时，使用基础分析模式。建议稍后重试。"
        except Exception as e:
            print(f"❌ AI调用失败: {e}")
            return f"AI分析失败: {str(e)}，已切换到安全模式。"


class SEODataAnalysisExpert(SEOAIAgent):
    """SEO数据分析专家"""
    
    def __init__(self):
        super().__init__()
        self.system_prompt = """你是专业的SEO数据分析专家，精通网站技术分析和数据解读。

核心能力：
- 解析网站技术数据（性能、结构、标签等）
- 识别SEO问题并评估严重程度
- 提供数据驱动的客观分析结果

分析框架：
1. 技术性能：页面加载速度、服务器响应、资源优化
2. 基础SEO：TDK质量、URL结构、Meta标签完整性
3. 页面结构：H标签层次、内链分布、导航深度
4. 内容质量：图片优化、链接质量、文本结构
5. 社交优化：OG标签、Twitter Cards、分享配置
6. 技术标签：Canonical、Sitemap、Robots、Hreflang
7. 流量数据：访问来源、用户行为、关键词表现

输出要求：
- 客观数据分析，不带主观判断
- 问题严重程度分级（严重/警告/提醒）
- 具体数据指标和改进空间
- 使用JSON格式返回分析结果"""
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析SEO数据"""
        print("\n🤖 SEO数据分析专家开始工作...")
        
        # 构建分析提示
        prompt = f"""
请分析以下SEO数据，提供专业的数据诊断：

网站URL: {data.get('url')}

基础信息:
{json.dumps(data.get('basic_info', {}), indent=2, ensure_ascii=False)}

技术SEO:
{json.dumps(data.get('technical_seo', {}), indent=2, ensure_ascii=False)}

内容分析:
{json.dumps(data.get('content_analysis', {}), indent=2, ensure_ascii=False)}

性能指标:
{json.dumps(data.get('performance', {}), indent=2, ensure_ascii=False)}

流量数据:
{json.dumps(data.get('traffic_data', {}), indent=2, ensure_ascii=False)}

请提供JSON格式的分析结果，包含以下字段：
- issues: 问题列表，每个问题包含type（严重/警告/提醒）、category、description、impact
- scores: 各项评分（0-100之间的整数），必须包含以下字段：
  * technical_performance: 技术性能评分
  * basic_seo: 基础SEO评分
  * content_quality: 内容质量评分
  * overall: 总体评分（可选）
- insights: 关键发现
- recommendations: 初步改进建议

重要：所有评分必须是0-100之间的整数！
"""
        
        response = await self.call_ai(self.system_prompt, prompt)
        
        try:
            # 尝试解析JSON响应
            if response.startswith('```json'):
                response = response[7:-3]
            elif response.startswith('```'):
                # 处理其他格式的代码块
                lines = response.split('\n')
                json_lines = []
                in_json = False
                for line in lines:
                    if line.strip().startswith('{') or in_json:
                        in_json = True
                        json_lines.append(line)
                        if line.strip().endswith('}') and line.count('}') >= line.count('{'):
                            break
                response = '\n'.join(json_lines)
            
            result = json.loads(response)
            
            # 确保scores字段存在且包含数值
            if 'scores' not in result or not result['scores']:
                print("⚠️ AI响应中缺少scores字段，尝试从文本中提取...")
                result['scores'] = self._extract_scores_from_text(response)
            
            # 验证并修正scores中的数值
            if 'scores' in result:
                result['scores'] = self._validate_scores(result['scores'])
            
            print(f"✅ 数据分析专家解析成功，评分: {result.get('scores', {})}")
            return result
            
        except Exception as e:
            print(f"❌ JSON解析失败: {e}")
            # 如果不是JSON，尝试从文本中提取评分
            extracted_scores = self._extract_scores_from_text(response)
            return {
                'raw_analysis': response,
                'issues': [],
                'scores': extracted_scores,
                'insights': [response],
                'recommendations': []
            }
    
    def _extract_scores_from_text(self, text: str) -> Dict[str, int]:
        """从文本中提取评分"""
        scores = {}
        import re
        
        # 查找各种评分模式
        patterns = [
            r'technical_performance["\']?\s*[:：]\s*(\d+)',
            r'basic_seo["\']?\s*[:：]\s*(\d+)',
            r'content_quality["\']?\s*[:：]\s*(\d+)', 
            r'overall_score["\']?\s*[:：]\s*(\d+)',
            r'overall["\']?\s*[:：]\s*(\d+)',
            r'技术性能.*?(\d+)',
            r'基础SEO.*?(\d+)',
            r'内容质量.*?(\d+)',
            r'总体评分.*?(\d+)'
        ]
        
        score_keys = ['technical_performance', 'basic_seo', 'content_quality', 'overall_score', 'overall', 'technical_performance', 'basic_seo', 'content_quality', 'overall_score']
        
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                score = int(matches[0])
                if 0 <= score <= 100:
                    key = score_keys[i % len(score_keys)]
                    scores[key] = score
        
        # 如果没有找到具体分类评分，尝试找任何数字评分
        if not scores:
            all_scores = re.findall(r'(?:评分|分数|得分|score)[:：\s]*(\d+)', text, re.IGNORECASE)
            if all_scores:
                score = int(all_scores[0])
                if 0 <= score <= 100:
                    scores['overall_score'] = score
        
        print(f"📊 从文本提取的评分: {scores}")
        return scores
    
    def _validate_scores(self, scores: Dict) -> Dict[str, int]:
        """验证并修正评分数据"""
        validated = {}
        
        for key, value in scores.items():
            if isinstance(value, (int, float)):
                score = int(value)
                if 0 <= score <= 100:
                    validated[key] = score
            elif isinstance(value, str):
                # 从字符串中提取数字
                import re
                numbers = re.findall(r'\d+', value)
                if numbers:
                    score = int(numbers[0])
                    if 0 <= score <= 100:
                        validated[key] = score
        
        print(f"✅ 验证后的评分: {validated}")
        return validated


class SEOStrategyAdvisor(SEOAIAgent):
    """SEO优化策略顾问"""
    
    def __init__(self):
        super().__init__()
        self.system_prompt = """你是资深SEO策略顾问，擅长制定优化方案和改进策略。

策略原则：
1. 保护现有资产：不改变已收录URL，维护外链价值
2. 双轨道优化：挖需求加新页面 + 找问题改老页面
3. 效果优先：优先处理高影响、低成本的改进项目

TDK优化模板：
- 首页：网站名-Slogan-关键词1-关键词2-关键词3
- 栏目：栏目名-子关键词1-子关键词2-网站名
- 内页：功能名-栏目名-网站名

技术优化清单：
- Canonical标签、Sitemap文件、合理内链结构
- H标签层次（H1唯一，H2分组，H3细分）
- 页面加载速度、服务器性能优化

内容策略：
- 基于关键词研究制定内容计划
- 优化图片Alt属性和链接锚文本
- 建立主题集群和内链网络

改版策略：
- URL结构保持一致，数据完整迁移
- 技术标签配置，搜索引擎重新收录

多语言优化：
- 子目录结构（/zh/、/en/），配置Hreflang
- 用户友好的语言切换，避免自动跳转

请根据分析结果，制定具体可执行的优化策略和实施计划。"""
    
    async def generate_strategy(self, data: Dict[str, Any], analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成优化策略"""
        print("\n💡 SEO策略顾问开始制定方案...")
        
        prompt = f"""
基于以下SEO数据分析结果，请制定具体的优化策略：

网站URL: {data.get('url')}

数据分析结果:
{json.dumps(analysis_result, indent=2, ensure_ascii=False)}

原始数据:
- 基础信息: {json.dumps(data.get('basic_info', {}), indent=2, ensure_ascii=False)}
- 技术SEO: {json.dumps(data.get('technical_seo', {}), indent=2, ensure_ascii=False)}
- 内容分析: {json.dumps(data.get('content_analysis', {}), indent=2, ensure_ascii=False)}

请提供：
1. 总体策略方向
2. 具体行动计划（按优先级排序）
3. 预期效果和时间估算
4. 资源需求评估
5. 风险提示和应对措施

使用JSON格式返回策略方案。"""
        
        response = await self.call_ai(self.system_prompt, prompt)
        
        try:
            if response.startswith('```json'):
                response = response[7:-3]
            result = json.loads(response)
            return result
        except:
            return {
                'raw_strategy': response,
                'strategy': response,
                'action_plan': [],
                'timeline': '待定',
                'resources': []
            }


class SEOReportDesigner(SEOAIAgent):
    """SEO报告设计师"""
    
    def __init__(self):
        super().__init__()
        self.system_prompt = """你是专业的SEO报告设计师，擅长将分析数据转化为美观直观的HTML报告。

设计原则：
1. 数据可视化：图表、进度条、评分卡片展示关键指标
2. 层次清晰：问题分级标识（红色严重、黄色警告、绿色正常）
3. 交互友好：折叠展开、标签页、响应式布局

报告结构：
1. 执行摘要：总体评分、关键问题、优先建议
2. 技术性能：加载速度、服务器指标、性能评分
3. 基础SEO：TDK分析、结构问题、标签检测
4. 内容优化：图片、链接、文本质量分析
5. 流量洞察：来源分析、关键词机会、竞争态势
6. 行动计划：优先级清单、时间规划、预期效果

视觉元素：
- 使用现代CSS框架（Bootstrap）
- 图标库（Font Awesome）
- 色彩方案（成功绿、警告黄、危险红）
- 数据图表（Chart.js）

技术要求：
- 响应式设计，移动端友好
- 可打印版本，PDF导出兼容
- 清晰的字体层次和间距
- 专业的品牌配色方案

请根据SEO分析数据生成完整的HTML报告。"""
    
    async def generate_report(self, data: Dict[str, Any], analysis: Dict[str, Any], strategy: Dict[str, Any]) -> str:
        """生成HTML报告"""
        print("\n📊 SEO报告设计师开始生成报告...")
        
        prompt = f"""
请生成一个完整的SEO分析HTML报告，包含以下内容：

网站URL: {data.get('url')}

数据分析结果:
{json.dumps(analysis, indent=2, ensure_ascii=False)}

优化策略:
{json.dumps(strategy, indent=2, ensure_ascii=False)}

关键数据摘要:
- 基础信息: {json.dumps(data.get('basic_info', {}), indent=2, ensure_ascii=False)}
- 技术SEO: {json.dumps(data.get('technical_seo', {}), indent=2, ensure_ascii=False)}
- 内容分析: {json.dumps(data.get('content_analysis', {}), indent=2, ensure_ascii=False)}
- 性能指标: {json.dumps(data.get('performance', {}), indent=2, ensure_ascii=False)}
- 流量数据: {json.dumps(data.get('traffic_data', {}), indent=2, ensure_ascii=False)}

要求：
1. 使用Bootstrap 5框架
2. 包含Chart.js图表
3. 响应式设计
4. 美观的数据可视化
5. 清晰的问题分级展示
6. 可打印的样式

请直接返回完整的HTML代码。"""
        
        html_report = await self.call_ai(self.system_prompt, prompt)
        return html_report


class SEOAgentOrchestrator:
    """SEO Agent协调器"""
    
    def __init__(self):
        self.data_expert = SEODataAnalysisExpert()
        self.strategy_advisor = SEOStrategyAdvisor()
        self.report_designer = SEOReportDesigner()
    
    async def run_full_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """运行完整的SEO分析流程"""
        print("\n🚀 启动AI SEO分析流程...")
        
        # 1. 数据分析专家分析数据
        analysis_result = await self.data_expert.analyze(data)
        
        # 2. 策略顾问生成优化方案
        strategy_result = await self.strategy_advisor.generate_strategy(data, analysis_result)
        
        # 3. 报告设计师生成HTML报告
        html_report = await self.report_designer.generate_report(data, analysis_result, strategy_result)
        
        # 计算总分
        overall_score = self._calculate_overall_score(analysis_result.get('scores', {}))
        
        # 如果分数仍然是0或无效，尝试从分析文本中提取
        if overall_score == 0:
            print("⚠️ 评分计算失败，尝试从分析文本中提取...")
            # 从分析结果中查找分数信息
            all_text = str(analysis_result) + str(strategy_result)
            import re
            score_matches = re.findall(r'(?:评分|分数|得分|score)[:：\s]*(\d+)', all_text, re.IGNORECASE)
            if score_matches:
                overall_score = min(100, max(0, int(score_matches[0])))
                print(f"✅ 从文本中提取到评分: {overall_score}")
        
        # 整合所有结果
        final_result = {
            'url': data.get('url'),
            'timestamp': data.get('timestamp'),
            'overall_score': overall_score,  # 添加到顶层
            'raw_data': data,
            'analysis': analysis_result,
            'strategy': strategy_result,
            'html_report': html_report,
            'summary': {
                'overall_score': overall_score,
                'critical_issues': len([i for i in analysis_result.get('issues', []) if i.get('type') == '严重']),
                'warnings': len([i for i in analysis_result.get('issues', []) if i.get('type') == '警告']),
                'recommendations_count': len(strategy_result.get('action_plan', []))
            }
        }
        
        print("✅ AI SEO分析流程完成")
        return final_result
    
    def _calculate_overall_score(self, scores: Dict[str, Any]) -> int:
        """计算总体评分"""
        print(f"\n🔍 调试信息 - 原始scores数据: {scores}")
        print(f"🔍 调试信息 - scores类型: {type(scores)}")
        
        if not scores:
            print("⚠️ scores为空，返回0")
            return 0
        
        # 如果scores是字符串，尝试解析
        if isinstance(scores, str):
            try:
                scores = json.loads(scores)
                print(f"🔍 解析后的scores: {scores}")
            except:
                print("⚠️ 无法解析scores字符串")
                return 50  # 默认分数
        
        # 确保scores是字典
        if not isinstance(scores, dict):
            print(f"⚠️ scores不是字典类型: {type(scores)}")
            return 50
        
        # 过滤掉非数字评分，并尝试从字符串中提取数字
        numeric_scores = []
        for key, value in scores.items():
            print(f"🔍 处理评分项: {key} = {value} (类型: {type(value)})")
            
            # 如果值是字符串，尝试提取数字
            if isinstance(value, str):
                # 查找数字模式
                import re
                numbers = re.findall(r'\d+', value)
                if numbers:
                    num = int(numbers[0])
                    if 0 <= num <= 100:
                        numeric_scores.append(num)
                        print(f"   ✓ 提取到数字: {num}")
            elif isinstance(value, (int, float)) and 0 <= value <= 100:
                numeric_scores.append(float(value))
                print(f"   ✓ 数字评分: {value}")
        
        print(f"🔍 有效数字评分列表: {numeric_scores}")
        
        if not numeric_scores:
            print("⚠️ 没有找到有效评分，返回默认分数50")
            return 50  # 返回默认分数而不是0
        
        # 如果只有一个评分，直接使用
        if len(numeric_scores) == 1:
            score = int(numeric_scores[0])
            print(f"✅ 使用单个评分: {score}")
            return score
        
        # 计算加权平均分
        # 技术性能和基础SEO权重更高
        weights = {
            'technical_performance': 1.2,
            'basic_seo': 1.2,
            'technical': 1.2,
            'seo': 1.2,
            'page_structure': 1.0,
            'content_quality': 1.1,
            'content': 1.1,
            'social_optimization': 0.8,
            'social': 0.8,
            'technical_tags': 1.0,
            'tags': 1.0,
            'traffic_data': 0.5,  # 流量数据权重较低，因为可能不准确
            'traffic': 0.5,
            'performance': 1.0
        }
        
        weighted_sum = 0
        total_weight = 0
        
        for key, score in scores.items():
            # 确定score值
            score_value = None
            if isinstance(score, (int, float)) and 0 <= score <= 100:
                score_value = score
            elif isinstance(score, str):
                import re
                numbers = re.findall(r'\d+', score)
                if numbers:
                    num = int(numbers[0])
                    if 0 <= num <= 100:
                        score_value = num
            
            if score_value is not None:
                # 查找匹配的权重
                weight = 1.0
                for weight_key, weight_value in weights.items():
                    if weight_key.lower() in key.lower():
                        weight = weight_value
                        break
                
                weighted_sum += score_value * weight
                total_weight += weight
                print(f"   加权计算: {key}={score_value} × {weight} = {score_value * weight}")
        
        if total_weight == 0:
            avg_score = int(sum(numeric_scores) / len(numeric_scores))
            print(f"✅ 使用简单平均分: {avg_score}")
            return avg_score
        
        final_score = int(weighted_sum / total_weight)
        print(f"✅ 最终加权评分: {final_score}")
        return final_score