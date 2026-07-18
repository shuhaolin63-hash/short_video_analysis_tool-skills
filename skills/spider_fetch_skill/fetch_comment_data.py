"""
评论数据抓取模块
支持抖音 / TikTok / Bilibili 三平台评论分页抓取
"""

import sys
import os
import asyncio
from typing import Optional

# 将项目根目录和参考代码目录加入 sys.path，以支持跨模块导入
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
_reference_path = os.path.join(_project_root, 'reference', 'Douyin_TikTok_Download_API')
if _reference_path not in sys.path:
    sys.path.insert(0, _reference_path)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from skills.spider_fetch_skill.api_adapter import SpiderFetchAPI


async def fetch_comments(
    video_id: str,
    platform: str,
    max_pages: int = 0,
    api_adapter: Optional[SpiderFetchAPI] = None,
) -> list:
    """
    分页抓取指定视频的全部评论

    Args:
        video_id: 视频 ID（抖音为 aweme_id，TikTok 为 aweme_id，Bilibili 为 BV 号）
        platform: 平台名称，可选值: "douyin", "tiktok", "bilibili"
        max_pages: 最大抓取页数（0 表示不限）
        api_adapter: SpiderFetchAPI 实例，若为 None 则内部创建

    Returns:
        标准化评论列表，每条评论包含:
            - cid: 评论 ID
            - user: 评论用户信息字典 {nickname}
            - text: 评论文本
            - digg_count: 评论点赞数
            - create_time: 评论发布时间 (Unix 时间戳)
            - reply_id: 父评论 ID（顶级评论为 "0"）
    """
    should_close = False
    if api_adapter is None:
        api_adapter = SpiderFetchAPI()
        should_close = True

    try:
        platform = platform.lower()
        if platform == "douyin":
            return await _fetch_douyin_comments(video_id, max_pages, api_adapter)
        elif platform == "tiktok":
            return await _fetch_tiktok_comments(video_id, max_pages, api_adapter)
        elif platform == "bilibili":
            return await _fetch_bilibili_comments(video_id, max_pages, api_adapter)
        else:
            raise ValueError(f"不支持的平台: {platform}")
    finally:
        if should_close:
            await api_adapter.close()


async def _fetch_douyin_comments(aweme_id: str, max_pages: int, api_adapter: SpiderFetchAPI) -> list:
    """
    抓取抖音评论

    Args:
        aweme_id: 抖音 aweme_id
        max_pages: 最大页数（0 表示不限）
        api_adapter: 爬虫适配器

    Returns:
        标准化评论列表
    """
    crawler = api_adapter.get_douyin_crawler()
    comments = []
    cursor = 0
    count = api_adapter.config.get("crawler", {}).get("comment", {}).get("page_size", 20)
    page = 0

    while True:
        page += 1
        if max_pages > 0 and page > max_pages:
            break

        result = await crawler.fetch_video_comments(aweme_id, cursor=cursor, count=count)
        raw_comments = result.get("comments", [])
        if not raw_comments:
            break

        for c in raw_comments:
            comments.append({
                "cid": str(c.get("cid", "")),
                "user": {
                    "nickname": c.get("user", {}).get("nickname", ""),
                },
                "text": c.get("text", ""),
                "digg_count": int(c.get("digg_count", 0)),
                "create_time": int(c.get("create_time", 0)),
                "reply_id": str(c.get("reply_id", 0)),
            })

        has_more = result.get("has_more", 0)
        if not has_more:
            break
        cursor = result.get("cursor", cursor)
        await asyncio.sleep(api_adapter.request_delay)

    return comments


async def _fetch_tiktok_comments(aweme_id: str, max_pages: int, api_adapter: SpiderFetchAPI) -> list:
    """
    抓取 TikTok 评论

    Args:
        aweme_id: TikTok aweme_id
        max_pages: 最大页数（0 表示不限）
        api_adapter: 爬虫适配器

    Returns:
        标准化评论列表
    """
    hybrid = api_adapter.get_hybrid_crawler()
    crawler = hybrid.TikTokWebCrawler
    comments = []
    cursor = 0
    count = api_adapter.config.get("crawler", {}).get("comment", {}).get("page_size", 20)
    page = 0

    while True:
        page += 1
        if max_pages > 0 and page > max_pages:
            break

        result = await crawler.fetch_post_comment(aweme_id, cursor=cursor, count=count)
        raw_comments = result.get("comments", [])
        if not raw_comments:
            break

        for c in raw_comments:
            comments.append({
                "cid": str(c.get("cid", "")),
                "user": {
                    "nickname": c.get("user", {}).get("nickname", ""),
                },
                "text": c.get("text", ""),
                "digg_count": int(c.get("digg_count", 0)),
                "create_time": int(c.get("create_time", 0)),
                "reply_id": str(c.get("reply_id", 0)),
            })

        has_more = result.get("has_more", 0)
        if not has_more:
            break
        cursor = result.get("cursor", cursor)
        await asyncio.sleep(api_adapter.request_delay)

    return comments


async def _fetch_bilibili_comments(bv_id: str, max_pages: int, api_adapter: SpiderFetchAPI) -> list:
    """
    抓取 Bilibili 评论

    Args:
        bv_id: Bilibili BV 号
        max_pages: 最大页数（0 表示不限）
        api_adapter: 爬虫适配器

    Returns:
        标准化评论列表
    """
    hybrid = api_adapter.get_hybrid_crawler()
    crawler = hybrid.BilibiliWebCrawler
    comments = []
    page = 0

    while True:
        page += 1
        if max_pages > 0 and page > max_pages:
            break

        result = await crawler.fetch_video_comments(bv_id, pn=page)
        data = result.get("data", {})
        replies = data.get("replies", [])
        if not replies:
            break

        for r in replies:
            comments.append({
                "cid": str(r.get("rpid", "")),
                "user": {
                    "nickname": r.get("member", {}).get("uname", ""),
                },
                "text": r.get("content", {}).get("message", ""),
                "digg_count": int(r.get("like", 0)),
                "create_time": int(r.get("ctime", 0)),
                "reply_id": str(r.get("parent", 0)),
            })

        if max_pages > 0 and page >= max_pages:
            break
        # Bilibili 没有明确的 has_more 标志，根据返回数量判断
        if len(replies) < 20:
            break
        await asyncio.sleep(api_adapter.request_delay)

    return comments
