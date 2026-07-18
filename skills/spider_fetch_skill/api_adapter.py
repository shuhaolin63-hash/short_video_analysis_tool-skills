"""
爬虫 API 适配器模块
用于初始化和管理各类平台爬虫实例
"""

import sys
import os
import asyncio
import yaml
from typing import Optional


# 将项目根目录和参考代码目录加入 sys.path，以支持跨模块导入
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
_reference_path = os.path.join(_project_root, 'reference', 'Douyin_TikTok_Download_API')
if _reference_path not in sys.path:
    sys.path.insert(0, _reference_path)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


class SpiderFetchAPI:
    """爬虫 API 适配器，封装爬虫实例的创建与配置加载"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化 SpiderFetchAPI

        Args:
            config_path: 全局配置文件路径，默认读取 skills 同级目录下的 config/global_config.yaml
        """
        if config_path is None:
            config_path = os.path.join(_project_root, 'config', 'global_config.yaml')

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        crawler_cfg = self.config.get('crawler', {})
        self.request_delay = crawler_cfg.get('request_delay', 1.5)
        self.max_retries = crawler_cfg.get('max_retries', 3)
        self.timeout = crawler_cfg.get('timeout', 10)
        self.proxies = crawler_cfg.get('proxies', {"http": "", "https": ""})

        # 转换代理格式：去掉值中的空字符串，保留 None 供 BaseCrawler 判断
        self._proxies_for_crawler = None
        if self.proxies and (self.proxies.get("http") or self.proxies.get("https")):
            self._proxies_for_crawler = {
                "http://": self.proxies.get("http", ""),
                "https://": self.proxies.get("https", ""),
            }

        self._hybrid_crawler_instance = None
        self._douyin_crawler_instance = None

    def get_hybrid_crawler(self):
        """
        获取 HybridCrawler 实例（懒加载单例）

        Returns:
            HybridCrawler: 混合爬虫实例
        """
        if self._hybrid_crawler_instance is None:
            # 延迟导入，确保 sys.path 已配置
            from crawlers.hybrid.hybrid_crawler import HybridCrawler
            self._hybrid_crawler_instance = HybridCrawler()
        return self._hybrid_crawler_instance

    def get_douyin_crawler(self):
        """
        获取 DouyinWebCrawler 实例（懒加载单例）

        Returns:
            DouyinWebCrawler: 抖音 Web 爬虫实例
        """
        if self._douyin_crawler_instance is None:
            from crawlers.douyin.web.web_crawler import DouyinWebCrawler
            self._douyin_crawler_instance = DouyinWebCrawler()
        return self._douyin_crawler_instance

    async def close(self):
        """关闭所有爬虫实例，释放资源"""
        if self._hybrid_crawler_instance is not None:
            # HybridCrawler 内部持有各子爬虫，关闭其内部的 async client
            for crawler_attr in ['DouyinWebCrawler', 'TikTokWebCrawler', 'TikTokAPPCrawler', 'BilibiliWebCrawler']:
                sub = getattr(self._hybrid_crawler_instance, crawler_attr, None)
                if sub is not None and hasattr(sub, 'aclient'):
                    await sub.aclient.aclose()
            self._hybrid_crawler_instance = None

        if self._douyin_crawler_instance is not None:
            self._douyin_crawler_instance = None
