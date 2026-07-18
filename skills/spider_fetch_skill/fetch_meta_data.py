"""
视频元数据抓取模块
提供根据视频 URL 获取标准化元数据的能力
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


async def fetch_video_meta(url: str, api_adapter: Optional[SpiderFetchAPI] = None) -> dict:
    """
    根据视频 URL 获取标准化的视频元数据

    Args:
        url: 视频分享链接（支持抖音 / TikTok / Bilibili）
        api_adapter: SpiderFetchAPI 实例，若为 None 则内部创建

    Returns:
        标准化后的元数据字典，包含以下字段:
            - video_id: 视频唯一标识
            - platform: 平台名称 (douyin / tiktok / bilibili)
            - desc: 视频标题/描述文字
            - create_time: 发布时间 (Unix 时间戳)
            - author: 作者信息字典 {id, name, ...}
            - statistics: 统计数据字典 {play_count, like_count, collect_count, share_count, comment_count}
            - cover_data: 封面数据字典
            - hashtags: 话题标签列表

    Raises:
        ValueError: 无法从 URL 判断视频来源时抛出
        Exception: 爬虫请求失败时抛出
    """
    should_close = False
    if api_adapter is None:
        api_adapter = SpiderFetchAPI()
        should_close = True

    try:
        hybrid = api_adapter.get_hybrid_crawler()
        raw_data = await hybrid.hybrid_parsing_single_video(url, minimal=True)

        # 标准化返回结构
        result = {
            "video_id": raw_data.get("video_id", ""),
            "platform": raw_data.get("platform", ""),
            "desc": raw_data.get("desc", ""),
            "create_time": raw_data.get("create_time", 0),
            "author": _extract_author(raw_data),
            "statistics": _extract_statistics(raw_data),
            "cover_data": raw_data.get("cover_data", {}),
            "hashtags": raw_data.get("hashtags", []),
        }
        return result

    finally:
        if should_close:
            await api_adapter.close()


def _extract_author(raw_data: dict) -> dict:
    """
    从原始数据中提取标准化的作者信息

    Args:
        raw_data: hybrid_parsing_single_video 返回的原始数据

    Returns:
        作者信息字典 {id, name}
    """
    author = raw_data.get("author")
    platform = raw_data.get("platform", "")

    if platform == "bilibili":
        # Bilibili 的 author 是 owner 对象
        if isinstance(author, dict):
            return {
                "id": str(author.get("mid", "")),
                "name": author.get("name", ""),
            }
    else:
        # 抖音/TikTok 的 author 对象
        if isinstance(author, dict):
            return {
                "id": str(author.get("uid", author.get("id", ""))),
                "name": author.get("nickname", author.get("nick_name", "")),
            }

    return {"id": "", "name": ""}


def _extract_statistics(raw_data: dict) -> dict:
    """
    从原始数据中提取标准化的统计数据

    Args:
        raw_data: hybrid_parsing_single_video 返回的原始数据

    Returns:
        统计数字典 {play_count, like_count, collect_count, share_count, comment_count}
    """
    statistics = raw_data.get("statistics", {})
    if not isinstance(statistics, dict):
        return {
            "play_count": 0,
            "like_count": 0,
            "collect_count": 0,
            "share_count": 0,
            "comment_count": 0,
        }

    platform = raw_data.get("platform", "")

    if platform == "bilibili":
        # Bilibili 的 statistics 使用 stat 字段
        return {
            "play_count": int(statistics.get("view", 0)),
            "like_count": int(statistics.get("like", 0)),
            "collect_count": int(statistics.get("favorite", 0)),
            "share_count": int(statistics.get("share", 0)),
            "comment_count": int(statistics.get("reply", 0)),
        }
    else:
        # 抖音/TikTok 的 statistics
        return {
            "play_count": int(statistics.get("play_count", statistics.get("playCount", 0))),
            "like_count": int(statistics.get("digg_count", statistics.get("likeCount", 0))),
            "collect_count": int(statistics.get("collect_count", statistics.get("collectCount", 0))),
            "share_count": int(statistics.get("share_count", statistics.get("shareCount", 0))),
            "comment_count": int(statistics.get("comment_count", statistics.get("commentCount", 0))),
        }
