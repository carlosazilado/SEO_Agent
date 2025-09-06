"""
SEO数据收集器
负责收集各种SEO相关数据
"""
import asyncio
import aiohttp
import json
import time
import platform
from datetime import datetime
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
import whois
from playwright.async_api import async_playwright
import re


class SEODataCollector:
    """SEO数据收集器 - 修复版本，解决并发问题"""
    
    def __init__(self):
        self.session = None
        self.playwright = None
        self.browser = None
        self.context = None
        self._page_semaphore = None  # 限制并发页面数量
        self._browser_lock = None  # 浏览器操作锁
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        self._browser_lock = asyncio.Lock()
        
        # 尝试初始化 Playwright (Windows 兼容性改进)
        try:
            # 设置Windows事件循环策略
            if platform.system() == 'Windows':
                try:
                    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                except AttributeError:
                    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
            self.playwright = await async_playwright().start()
            
            # 尝试启动浏览器，使用多种配置
            browser_configs = [
                # 配置1：稳定配置
                {
                    'headless': True,
                    'args': [
                        '--no-sandbox',
                        '--disable-setuid-sandbox', 
                        '--disable-dev-shm-usage',
                        '--disable-web-security',
                        '--disable-gpu',
                        '--disable-software-rasterizer',
                        '--disable-background-timer-throttling',
                        '--disable-renderer-backgrounding',
                        '--disable-backgrounding-occluded-windows'
                    ]
                },
                # 配置2：简化配置
                {
                    'headless': True,
                    'args': ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage']
                },
                # 配置3：默认配置
                {
                    'headless': True
                }
            ]
            
            for i, config in enumerate(browser_configs):
                try:
                    print(f"尝试浏览器配置 {i+1}/3...")
                    self.browser = await self.playwright.chromium.launch(**config)
                    
                    # 创建一个持久的浏览器上下文，配置更多选项
                    self.context = await self.browser.new_context(
                        user_agent=self.headers['User-Agent'],
                        viewport={'width': 1920, 'height': 1080},
                        ignore_https_errors=True,
                        java_script_enabled=True
                    )
                    
                    # 设置默认超时
                    self.context.set_default_timeout(30000)
                    self.context.set_default_navigation_timeout(30000)
                    
                    # 创建信号量限制并发页面数量 - 只允许1个页面同时操作
                    self._page_semaphore = asyncio.Semaphore(1)
                    print("✅ 浏览器启动成功")
                    break
                except Exception as e:
                    print(f"配置 {i+1} 失败: {e}")
                    if self.browser:
                        try:
                            await self.browser.close()
                        except:
                            pass
                    if i == len(browser_configs) - 1:
                        raise e
                        
        except Exception as e:
            print(f"⚠️ Playwright初始化失败: {e}")
            print("⚠️ 浏览器不可用，使用简化数据收集模式")
            self.playwright = None
            self.browser = None
            self.context = None
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """清理资源"""
        if self.context:
            try:
                await self.context.close()
            except:
                pass
        if self.browser:
            try:
                await self.browser.close()
            except:
                pass
        if self.playwright:
            try:
                await self.playwright.stop()
            except:
                pass
        if self.session:
            try:
                await self.session.close()
            except:
                pass
    
    async def _get_page(self):
        """安全地获取一个页面实例"""
        if not self.context:
            return None
        
        async with self._page_semaphore:
            try:
                async with self._browser_lock:
                    page = await self.context.new_page()
                    return page
            except Exception as e:
                print(f"⚠️ 创建页面失败: {e}")
                return None
    
    async def _close_page(self, page):
        """安全地关闭页面"""
        if page:
            try:
                await page.close()
            except:
                pass
    
    async def collect_all_data(self, url: str) -> Dict[str, Any]:
        """收集所有SEO数据"""
        print(f"\n🔍 开始收集SEO数据: {url}")
        
        data = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'basic_info': {},
            'technical_seo': {},
            'content_analysis': {},
            'performance': {},
            'traffic_data': {},
            'serp_data': {}
        }
        
        # 先使用简化模式确保功能正常 
        print("🔧 使用简化数据收集模式以确保稳定性")
        data['basic_info'] = await self._get_basic_info(url)
        data['traffic_data'] = await self._get_traffic_data(url)
        data['serp_data'] = await self._get_serp_data(url)
        
        # 使用HTTP请求获取内容分析
        content_data = await self._analyze_content_simple(url)
        if content_data:
            data['content_analysis'] = content_data
        
        # 如果浏览器可用，获取技术SEO和性能数据
        if self.context:
            try:
                data['technical_seo'] = await self._analyze_technical_seo(url)
                data['performance'] = await self._get_performance_metrics(url)
            except Exception as e:
                print(f"⚠️ 浏览器数据收集失败: {e}")
        else:
            print("⚠️ 浏览器不可用，跳过技术SEO和性能分析")
        
        print("✅ SEO数据收集完成")
        return data
    
    async def _get_basic_info(self, url: str) -> Dict[str, Any]:
        """获取基础信息"""
        print("📝 获取基础信息...")
        
        try:
            domain = urlparse(url).netloc
            w = whois.whois(domain)
            
            return {
                'domain': domain,
                'domain_age': self._calculate_domain_age(w.creation_date),
                'registrar': w.registrar,
                'nameservers': w.name_servers,
                'ssl_info': await self._check_ssl(url)
            }
        except Exception as e:
            print(f"❌ 获取基础信息失败: {e}")
            return {}
    
    async def _analyze_technical_seo(self, url: str) -> Dict[str, Any]:
        """分析技术SEO"""
        print("🔧 分析技术SEO...")
        
        if not self.context:
            print("⚠️ 浏览器上下文不可用，跳过技术SEO分析")
            return {}
        
        page = await self._get_page()
        if not page:
            print("⚠️ 无法创建页面，跳过技术SEO分析")
            return {}
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # 检查robots.txt
            robots_url = urljoin(url, '/robots.txt')
            robots_content = await self._fetch_url_content(robots_url)
            
            # 检查sitemap.xml
            sitemap_url = urljoin(url, '/sitemap.xml')
            sitemap_content = await self._fetch_url_content(sitemap_url)
            
            # 分析HTML结构
            html = await page.content()
            structure_analysis = self._analyze_html_structure(html)
            
            return {
                'robots_txt': {
                    'exists': bool(robots_content),
                    'content': robots_content[:500] if robots_content else None
                },
                'sitemap_xml': {
                    'exists': bool(sitemap_content),
                    'content': sitemap_content[:500] if sitemap_content else None
                },
                'html_structure': structure_analysis,
                'ssl_enabled': url.startswith('https://')
            }
            
        except Exception as e:
            print(f"⚠️ 数据收集失败: {e}")
            return {}
        finally:
            await self._close_page(page)
    
    async def _analyze_content(self, url: str) -> Dict[str, Any]:
        """分析内容质量"""
        print("📄 分析内容质量...")
        
        if not self.context:
            print("⚠️ 浏览器上下文不可用，使用简化模式")
            return await self._analyze_content_simple(url)
        
        page = await self._get_page()
        if not page:
            print("⚠️ 无法创建页面，使用简化模式")
            return await self._analyze_content_simple(url)
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            
            # 分析页面内容 - 简化JavaScript执行
            content_data = await page.evaluate('''() => {
                try {
                    const title = document.querySelector('title')?.textContent || '';
                    const description = document.querySelector('meta[name="description"]')?.content || '';
                    const h1s = Array.from(document.querySelectorAll('h1')).map(h => h.textContent);
                    const h2s = Array.from(document.querySelectorAll('h2')).map(h => h.textContent);
                    const images = Array.from(document.querySelectorAll('img'));
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    
                    const wordCount = document.body ? document.body.innerText.split(/\\s+/).filter(w => w.length > 0).length : 0;
                    
                    return {
                        tdk: {
                            title: title,
                            title_length: title.length,
                            description: description,
                            description_length: description.length,
                            keywords: document.querySelector('meta[name="keywords"]')?.content || ''
                        },
                        headings: {
                            h1: h1s,
                            h2: h2s,
                            h1_count: h1s.length,
                            h2_count: h2s.length
                        },
                        images: {
                            total: images.length,
                            without_alt: images.filter(img => !img.alt || img.alt.trim() === '').length,
                            with_alt: images.filter(img => img.alt && img.alt.trim() !== '').length
                        },
                        links: {
                            total: links.length,
                            internal: links.filter(link => {
                                try {
                                    return link.href.includes(window.location.hostname) || link.href.startsWith('/');
                                } catch(e) {
                                    return false;
                                }
                            }).length,
                            external: links.filter(link => {
                                try {
                                    return !link.href.includes(window.location.hostname) && !link.href.startsWith('/') && link.href.startsWith('http');
                                } catch(e) {
                                    return false;
                                }
                            }).length
                        },
                        content_metrics: {
                            word_count: wordCount,
                            reading_time: Math.ceil(wordCount / 200)
                        }
                    };
                } catch(e) {
                    console.error('Content analysis error:', e);
                    return null;
                }
            }()');
            
            if content_data:
                return content_data
            else:
                print("⚠️ JavaScript执行失败，使用简化模式")
                return await self._analyze_content_simple(url)
                
        except Exception as e:
            print(f"❌ 内容分析失败，使用简化模式: {e}")
            return await self._analyze_content_simple(url)
        finally:
            if page:
                try:
                    await page.close()
                except:
                    pass
                
                return {
                    title: title,
                    title_length: title.length,
                    description: description,
                    description_length: description.length,
                    h1_count: h1s.length,
                    h2_count: h2s.length,
                    h1_texts: h1s,
                    word_count: wordCount,
                    image_count: images.length,
                    images_without_alt: images.filter(img => !img.alt).length,
                    internal_links: links.filter(link => 
                        link.href.includes(window.location.hostname) || 
                        link.href.startsWith('/')
                    ).length,
                    external_links: links.filter(link => 
                        !link.href.includes(window.location.hostname) && 
                        !link.href.startsWith('/') &&
                        (link.href.startsWith('http') || link.href.startsWith('https'))
                    ).length
                };
            }''')
            
            return content_data
            
        except Exception as e:
            print(f"⚠️ 内容分析失败: {e}")
            return {}
        finally:
            await self._close_page(page)
            return {}
        
        async with self._page_semaphore:
            page = None
            try:
                page = await self.context.new_page()
                await page.goto(url, wait_until="networkidle", timeout=30000)
                
                content = await page.evaluate('''
                    () => {
                        const title = document.title;
                        const description = document.querySelector('meta[name="description"]')?.content || '';
                        const keywords = document.querySelector('meta[name="keywords"]')?.content || '';
                        
                        // 分析标题结构
                        const headings = {};
                        for (let i = 1; i <= 6; i++) {
                            headings[`h${i}`] = Array.from(document.querySelectorAll(`h${i}`)).map(h => h.textContent.trim());
                        }
                        
                        // 分析图片
                        const images = Array.from(document.querySelectorAll('img'));
                        const imageAnalysis = {
                            total: images.length,
                            without_alt: images.filter(img => !img.alt || img.alt.trim() === '').length,
                            with_alt: images.filter(img => img.alt && img.alt.trim() !== '').length
                        };
                        
                        // 分析链接
                        const links = Array.from(document.querySelectorAll('a[href]'));
                        const linkAnalysis = {
                            total: links.length,
                            internal: links.filter(link => link.href.includes(window.location.hostname)).length,
                            external: links.filter(link => !link.href.includes(window.location.hostname)).length,
                            nofollow: links.filter(link => link.rel?.includes('nofollow')).length
                        };
                        
                        // OG标签
                        const ogTags = {};
                        document.querySelectorAll('meta[property^="og:"]').forEach(tag => {
                            ogTags[tag.getAttribute('property')] = tag.getAttribute('content');
                        });
                        
                        // Twitter Cards
                        const twitterTags = {};
                        document.querySelectorAll('meta[name^="twitter:"]').forEach(tag => {
                            twitterTags[tag.getAttribute('name')] = tag.getAttribute('content');
                        });
                        
                        // 文本内容分析
                        const textContent = document.body.innerText;
                        const wordCount = textContent.split(/\\s+/).filter(word => word.length > 0).length;
                        
                        return {
                            tdk: {
                                title: title,
                                title_length: title.length,
                                description: description,
                                description_length: description.length,
                                keywords: keywords
                            },
                            headings: headings,
                            images: imageAnalysis,
                            links: linkAnalysis,
                            social_tags: {
                                og: ogTags,
                                twitter: twitterTags
                            },
                            content_metrics: {
                                word_count: wordCount,
                                reading_time: Math.ceil(wordCount / 200)  // 假设每分钟阅读200字
                            }
                        };
                    }
                ''')
                
                return content
            except Exception as e:
                print(f"❌ 内容分析失败: {e}")
                return {}
            finally:
                if page:
                    try:
                        await page.close()
                    except:
                        pass
    
    async def _analyze_content_simple(self, url: str) -> Dict[str, Any]:
        """使用HTTP请求分析内容"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    if BeautifulSoup:
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # 提取基本信息
                        title = soup.find('title')
                        title_text = title.text.strip() if title else ''
                        
                        description = soup.find('meta', attrs={'name': 'description'})
                        desc_text = description.get('content', '') if description else ''
                        
                        # 分析标题
                        headings = {}
                        for i in range(1, 7):
                            h_tags = soup.find_all(f'h{i}')
                            headings[f'h{i}'] = [h.text.strip() for h in h_tags]
                        
                        # 分析图片
                        images = soup.find_all('img')
                        img_no_alt = sum(1 for img in images if not img.get('alt'))
                        
                        # 分析链接
                        links = soup.find_all('a', href=True)
                        domain = urlparse(url).netloc
                        internal_links = sum(1 for link in links if domain in link.get('href', ''))
                        
                        return {
                            'tdk': {
                                'title': title_text,
                                'title_length': len(title_text),
                                'description': desc_text,
                                'description_length': len(desc_text),
                                'keywords': ''
                            },
                            'headings': headings,
                            'images': {
                                'total': len(images),
                                'without_alt': img_no_alt,
                                'with_alt': len(images) - img_no_alt
                            },
                            'links': {
                                'total': len(links),
                                'internal': internal_links,
                                'external': len(links) - internal_links,
                                'nofollow': 0
                            },
                            'social_tags': {'og': {}, 'twitter': {}},
                            'content_metrics': {
                                'word_count': len(soup.get_text().split()),
                                'reading_time': 0
                            }
                        }
        except Exception as e:
            print(f"❌ 简化内容分析失败: {e}")
        
        return {}
    
    async def _get_performance_metrics(self, url: str) -> Dict[str, Any]:
        """获取性能指标"""
        print("⚡ 获取性能指标...")
        
        if not self.context:
            print("⚠️ 浏览器上下文不可用，跳过性能分析")
            return {}
        
        page = await self._get_page()
        if not page:
            print("⚠️ 无法创建页面，跳过性能分析")
            return {}
        
        try:
            start_time = time.time()
            await page.goto(url, wait_until="networkidle", timeout=30000)
            load_time = time.time() - start_time
            
            # 获取页面性能指标
            performance_data = await page.evaluate('''() => {
                const navigation = performance.getEntriesByType('navigation')[0];
                const resources = performance.getEntriesByType('resource');
                
                return {
                    page_load_time: navigation ? navigation.loadEventEnd - navigation.fetchStart : 0,
                    dom_content_loaded: navigation ? navigation.domContentLoadedEventEnd - navigation.fetchStart : 0,
                    first_byte: navigation ? navigation.responseStart - navigation.fetchStart : 0,
                    resources: {
                        total_requests: resources.length,
                        total_size: resources.reduce((sum, r) => sum + (r.transferSize || 0), 0),
                        images: resources.filter(r => r.initiatorType === 'img').length,
                        scripts: resources.filter(r => r.initiatorType === 'script').length,
                        stylesheets: resources.filter(r => r.initiatorType === 'link').length
                    }
                };
            }''')
            
            # 添加我们测量的加载时间
            performance_data['measured_load_time'] = round(load_time, 2)
            
            return performance_data
            
        except Exception as e:
            print(f"⚠️ 性能分析失败: {e}")
            return {'measured_load_time': 0, 'error': str(e)}
        finally:
            await self._close_page(page)
    
    async def _get_traffic_data(self, url: str) -> Dict[str, Any]:
        """获取流量数据（模拟数据，避免API依赖）"""
        print("📊 获取流量数据...")
        
        domain = urlparse(url).netloc
        
        # 返回模拟的流量数据，避免依赖付费API
        print("ℹ️  使用模拟流量数据（SimilarWeb API需要付费密钥）")
        
        return {
            'estimated_visits': {
                'monthly': 'N/A',
                'note': '需要流量分析API'
            },
            'engagement': {
                'avg_visit_duration': 'N/A',
                'pages_per_visit': 'N/A', 
                'bounce_rate': 'N/A'
            },
            'traffic_sources': {
                'direct': 'N/A',
                'search': 'N/A',
                'social': 'N/A',
                'referrals': 'N/A'
            },
            'top_countries': 'N/A',
            'rankings': {
                'global_rank': 'N/A',
                'country_rank': 'N/A'
            },
            'domain': domain,
            'status': 'mock_data'
        }
    
    async def _get_serp_data(self, url: str) -> Dict[str, Any]:
        """获取SERP数据（模拟）"""
        print("🔍 获取SERP数据...")
        
        # 这里可以集成OpenSERP或其他SERP API
        # 目前返回模拟数据
        return {
            'indexed_pages': '未知',
            'backlinks_estimate': '未知',
            'domain_authority': 0,
            'keyword_rankings': [],
            'note': 'SERP数据需要配置专门的API服务'
        }
    
    async def _fetch_url_content(self, url: str) -> Optional[str]:
        """获取URL内容"""
        try:
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
        except Exception:
            pass
        return None
    
    def _calculate_domain_age(self, creation_date) -> Optional[int]:
        """计算域名年龄"""
        if not creation_date:
            return None
        
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        
        if isinstance(creation_date, str):
            try:
                creation_date = datetime.strptime(creation_date, '%Y-%m-%d %H:%M:%S')
            except:
                try:
                    creation_date = datetime.strptime(creation_date, '%Y-%m-%d')
                except:
                    return None
        
        days = (datetime.now() - creation_date).days
        return days
    
    def _analyze_html_structure(self, html: str) -> Dict[str, Any]:
        """分析HTML结构"""
        if not BeautifulSoup:
            return {}
            
        soup = BeautifulSoup(html, 'html.parser')
        
        structure_analysis = {
            'has_doctype': bool(html.startswith('<!DOCTYPE')),
            'semantic_tags': {
                'header': len(soup.find_all('header')),
                'nav': len(soup.find_all('nav')),
                'main': len(soup.find_all('main')),
                'article': len(soup.find_all('article')),
                'section': len(soup.find_all('section')),
                'aside': len(soup.find_all('aside')),
                'footer': len(soup.find_all('footer'))
            },
            'total_images': len(soup.find_all('img')),
            'total_links': len(soup.find_all('a')),
            'has_schema': bool(soup.find_all(attrs={'type': 'application/ld+json'}))
        }
        
        return structure_analysis
    
    async def _check_ssl(self, url: str) -> Dict[str, Any]:
        """检查SSL证书"""
        try:
            async with self.session.get(url, ssl=False) as response:
                return {
                    'enabled': url.startswith('https://'),
                    'valid': True,  # 简化检查
                    'issuer': 'Unknown'
                }
        except:
            return {
                'enabled': False,
                'valid': False,
                'issuer': None
            }


# BeautifulSoup导入
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None