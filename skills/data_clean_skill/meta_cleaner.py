"""
视频元数据清洗模块
将原始爬虫返回的元数据清洗为标准化的格式
"""

import sys
import os
from datetime import datetime
from typing import Optional

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


def clean_video_meta(raw_meta: dict) -> dict:
    """
    清洗视频元数据，标准化字段名和格式

    处理逻辑:
        1. 格式化数字（去科学计数法，转 int）
        2. 处理缺失值（None 转 0 或空字符串）
        3. 转换时间戳为 datetime 字符串
        4. 映射字段名为统一标准

    Args:
        raw_meta: fetch_video_meta 返回的原始元数据字典

    Returns:
        标准化后的元数据字典，包含以下字段:
            - video_id: 视频 ID
            - video_url: 视频链接（留空，由调用方填充）
            - title_text: 视频标题
            - publish_time: 发布时间 (格式: YYYY-MM-DD HH:MM:SS)
            - author_name: 作者昵称
            - author_uid: 作者 UID
            - play_count: 播放量
            - like_count: 点赞数
            - collect_count: 收藏数
            - share_count: 转发数
            - comment_total: 总评论数
            - cover_url: 封面链接
            - cover_local_path: 本地封面路径（留空，由调用方填充）
            - parse_time: 解析时间 (格式: YYYY-MM-DD HH:MM:SS)
    """
    statistics = raw_meta.get("statistics", {})
    author = raw_meta.get("author", {})

    # 处理封面 URL：优先使用 origin_cover，其次是 cover
    cover_data = raw_meta.get("cover_data", {})
    cover_url = (
        cover_data.get("origin_cover")
        or cover_data.get("cover")
        or ""
    )

    # 转换时间戳
    create_ts = _safe_int(raw_meta.get("create_time", 0))
    publish_time = _timestamp_to_str(create_ts) if create_ts > 0 else ""

    # 当前解析时间
    parse_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "video_id": str(raw_meta.get("video_id", "")),
        "video_url": "",  # 由调用方填充
        "title_text": str(raw_meta.get("desc", "")),
        "publish_time": publish_time,
        "author_name": str(author.get("name", "")),
        "author_uid": str(author.get("id", "")),
        "play_count": _safe_int(statistics.get("play_count", 0)),
        "like_count": _safe_int(statistics.get("like_count", 0)),
        "collect_count": _safe_int(statistics.get("collect_count", 0)),
        "share_count": _safe_int(statistics.get("share_count", 0)),
        "comment_total": _safe_int(statistics.get("comment_count", 0)),
        "cover_url": cover_url,
        "cover_local_path": "",  # 由调用方填充
        "parse_time": parse_time,
    }


def _safe_int(value) -> int:
    """
    安全地将值转换为 int，去除科学计数法

    Args:
        value: 输入值

    Returns:
        int 值
    """
    if value is None:
        return 0
    try:
        # 如果是浮点数科学计数法，先转 float 再转 int
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            # 去除科学计数法
            if 'e' in value.lower():
                return int(float(value))
            return int(value)
        return int(value)
    except (ValueError, TypeError):
        return 0


def _timestamp_to_str(ts: int) -> str:
    """
    将 Unix 时间戳转换为日期时间字符串

    Args:
        ts: Unix 时间戳（秒）

    Returns:
        格式化的时间字符串 (YYYY-MM-DD HH:MM:SS)
    """
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except (OSError, ValueError, OverflowError):
        return ""
