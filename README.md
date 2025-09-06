# SEO Agent Pro - 智能SEO分析系统 🚀

## 🌟 项目简介

SEO Agent 是一个基于AI技术的智能SEO分析系统，支持多种AI服务提供商（硅基流动、OpenAI、Google等），提供专业的网站SEO分析和优化建议：

- 🔍 **智能分析**: 支持多种AI模型深度分析网站SEO状况
- 📊 **数据收集**: 自动收集页面内容、性能指标、技术参数
- 🧠 **AI专家团队**: 三位AI专家（数据分析师、策略顾问、报告设计师）提供专业分析
- 📈 **评分系统**: 综合评分和详细的改进建议
- 📝 **专业报告**: 生成详细的SEO分析报告（支持下载）
- 🌐 **Web界面**: 友好的Web界面，支持批量分析
- 💾 **历史记录**: 保存所有分析历史，便于对比
- 🔐 **安全设计**: 环境变量管理，保护API密钥安全
- ⚡ **基础模式**: 即使没有API密钥也能进行基础SEO分析

## ✨ 核心特性

### 🤖 AI驱动分析
- **三个专业AI代理**：数据分析专家、策略顾问、报告设计师
- **多AI提供商支持**：
  - 硅基流动（SiliconFlow）：Qwen/Qwen2.5-VL-72B-Instruct
  - OpenAI：GPT-3.5/4系列模型
  - Google：Gemini系列模型
- **智能建议生成**：基于深度分析的个性化优化方案
- **基础分析模式**：无API密钥时提供基础SEO分析功能

### 📊 全面数据收集
- **基础信息**：域名信息、服务器状态、WHOIS查询
- **内容分析**：TDK、标题结构、图片优化、链接分析
- **技术SEO**：HTTPS、canonical、robots.txt、sitemap、移动友好性
- **性能监测**：页面加载时间、渲染性能、缓存策略

### 🎯 智能评分系统
- **多维度评分**：内容质量(40%) + 技术SEO(30%) + 性能(30%)
- **问题分级**：严重/警告/提醒三级问题识别
- **可视化展示**：直观的评分圆环和进度条

### 📄 专业报告
- **HTML格式**：美观的可视化报告
- **AI洞察**：深度分析和策略建议
- **下载功能**：支持报告保存和分享
- **历史记录**：完整的分析历史管理

## 🛠 技术架构

### 后端技术栈
- **FastAPI**：现代化的异步Web框架
- **SiliconFlow API**：Qwen/Qwen2.5-VL-72B-Instruct AI模型
- **Playwright**：浏览器自动化和页面渲染
- **aiohttp**：异步HTTP客户端
- **BeautifulSoup4**：HTML解析和处理
- **SQLite**：轻量级关系数据库
- **python-dotenv**：环境变量管理

### 前端技术栈
- **Bootstrap 5**：响应式UI框架
- **Jinja2**：服务端模板引擎
- **Chart.js**：数据可视化
- **Font Awesome**：矢量图标库

## 🚀 快速开始

### 📋 环境要求
- Python 3.11+
- Windows/Linux/macOS
- 2GB+ 可用内存
- 网络连接（用于AI API调用）

### 1. 克隆项目
```bash
git clone <repository-url>
cd SEO_Agent
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. 配置环境变量
```bash
# 复制环境配置模板
cp .env.example .env

# 编辑 .env 文件，设置你的API密钥
# SILICONFLOW_API_KEY=your-api-key-here
```

### 4. 启动前准备
```bash
# 安装Playwright浏览器
python -m playwright install chromium

# 下载spaCy模型
python -m spacy download en_core_web_sm
```

### 5. 启动应用
```bash
# 使用启动脚本（推荐）
python start.py

# 或直接启动
python app.py
```

### 6. 开始使用
打开浏览器访问: http://localhost:8000

## 📁 项目结构

```
SEO_Agent/
├── app.py               # FastAPI主应用
├── seo_analyzer.py      # 核心SEO分析引擎
├── database.py          # 数据库操作
├── start.py             # 启动脚本
├── start.bat            # Windows启动脚本
├── requirements.txt     # 依赖包列表
├── .env.example         # 环境变量模板
├── .gitignore           # Git忽略文件
├── vercel.json          # Vercel配置
├── templates/           # HTML模板
│   ├── index.html       # 首页
│   ├── results.html     # 结果页面
│   ├── batch.html       # 批量处理
│   └── history.html     # 历史记录
├── static/              # 静态资源
│   └── css/
│       └── modern.css   # 现代化样式
├── reports/             # 生成的报告目录
└── venv/                # 虚拟环境（推荐）
```

## 📊 使用指南

### 单个网站分析
1. 在首页输入要分析的网站URL
2. 点击"开始分析"按钮
3. 等待分析完成（通常1-3分钟）
4. 查看详细的分析报告

### 批量网站分析
1. 在"批量URL分析"框中每行输入一个URL
2. 系统将依次分析每个网站
3. 在结果页面查看所有网站的分析结果

### 查看历史记录
1. 点击"分析历史"链接
2. 查看之前的所有分析记录
3. 可以重新下载之前的报告

## 🔧 配置说明

### 🔐 安全的API配置
系统支持多种AI服务提供商，使用环境变量配置：

1. **复制配置模板**：
   ```bash
   cp .env.example .env
   ```

2. **编辑.env文件**：
   ```env
   # 硅基流动API配置（推荐）
   SILICONFLOW_API_KEY=your_api_key_here
   SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
   SILICONFLOW_MODEL=Qwen/Qwen2.5-VL-72B-Instruct

   # OpenAI API配置（备用）
   OPENAI_API_KEY=your_openai_key_here
   OPENAI_BASE_URL=https://api.openai.com/v1
   OPENAI_MODEL=gpt-3.5-turbo

   # Google API配置（备用）
   GOOGLE_API_KEY=your_google_api_key_here
   GOOGLE_MODEL=gemini-2.0-flash-exp
   ```

3. **环境变量说明**：
   - **优先级**：SiliconFlow > OpenAI > Google
   - 系统会自动检测可用的API密钥
   - 如果没有配置任何API密钥，系统将运行在基础分析模式

### 📁 配置文件
- `.env.example`: 配置模板文件
- `.env`: 实际配置文件（包含在.gitignore中）
- `.gitignore`: 防止敏感信息泄露

### 数据库配置
系统默认使用SQLite数据库：
- 数据文件：`seo_analysis.db`
- 自动创建表结构
- 支持历史记录管理

## 📈 性能优化

- **异步处理**：所有网络请求和AI调用都是异步的
- **智能缓存**：避免重复分析相同网站
- **错误恢复**：多种备用方案确保分析完成
- **资源管理**：自动清理浏览器实例和网络连接

## 🎯 功能特色

### AI分析流程
1. **数据收集阶段**：并行收集网站各维度数据
2. **AI分析阶段**：三个专业AI代理分别进行分析
3. **报告生成阶段**：整合分析结果生成专业报告

### 智能建议类型
- **技术优化**：HTTPS、性能、移动友好性
- **内容优化**：TDK、图片alt、内链结构
- **SEO策略**：关键词优化、竞争分析、增长策略

### 报告特色
- **视觉化评分**：直观的评分展示
- **分层建议**：按优先级组织的改进建议
- **可操作性**：每个建议都有具体的实施方案

## 🏗️ 系统架构

### AI专家代理系统
1. **数据分析专家**：
   - 专注技术指标和性能数据
   - 识别SEO问题和评估严重程度
   - 提供客观的数据分析结果

2. **策略顾问**：
   - 制定优化方案和改进策略
   - 优先级排序和实施规划
   - 资源需求评估和预期效果

3. **报告设计师**：
   - 数据可视化和洞察提炼
   - 风险评估和成功指标
   - 行动路线图设计

### 容错机制
- **多重备用方案**：确保分析在各种情况下都能完成
- **优雅降级**：AI不可用时自动切换到基础分析模式
- **错误恢复**：自动重试和备用数据源

## 🔮 扩展计划

- [ ] 集成更多SEO工具API
- [ ] 添加竞争对手分析
- [ ] 支持定时监控和报警
- [ ] 增加更多可视化图表
- [ ] 支持团队协作功能
- [ ] 移动端App开发

## 📞 技术支持

- **问题反馈**：提交Issue或PR
- **技术交流**：加入技术讨论群
- **定制开发**：支持企业级定制需求

---

> 🌟 SEO Agent - 让SEO分析更智能、更专业、更高效！
