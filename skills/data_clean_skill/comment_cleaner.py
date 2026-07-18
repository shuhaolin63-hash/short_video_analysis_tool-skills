"""
评论数据清洗模块
清洗评论文本和批量标准化评论数据
"""

import re
import sys
import os
from typing import List, Dict

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


def clean_comment_text(text: str) -> str:
    """
    清洗单条评论内容

    处理逻辑:
        1. 去除表情符号（Unicode 表情符号范围）
        2. 去除特殊符号（如 # @ 等）
        3. 去除多余空白和换行
        4. 去除首尾空格

    Args:
        text: 原始评论文本

    Returns:
        清洗后的评论文本
    """
    if not isinstance(text, str):
        text = str(text) if text is not None else ""

    # 去除 Unicode 表情符号 (Emoji) 范围
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # 表情符号
        "\U0001F300-\U0001F5FF"  # 符号和象形文字
        "\U0001F680-\U0001F6FF"  # 运输和地图符号
        "\U0001F1E0-\U0001F1FF"  # 旗帜
        "\U00002702-\U000027B0"  # 其他符号
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # 补充符号和象形文字
        "\U0001FA00-\U0001FA6F"  # 象棋符号
        "\U0001FA70-\U0001FAFF"  # 符号扩展-A
        "\U00002600-\U000026FF"  # 杂项符号
        "\U0000FE00-\U0000FE0F"  # 变体选择器
        "\U0000200D-\U0000200F"  # 零宽连接符等
        "\U0000202E-\U0000202F"  # 方向符号
        "\U00002060-\U0000206F"  # 格式字符
        "\U00002190-\U000021FF"  # 箭头
        "\U00002000-\U0000206F"  # 一般标点
        "]+",
        flags=re.UNICODE,
    )
    text = emoji_pattern.sub("", text)

    # 去除 @ 用户提及
    text = re.sub(r'@\S+', '', text)

    # 去除 # 话题标签
    text = re.sub(r'#\S+', '', text)

    # 去除 URL
    text = re.sub(r'https?://\S+', '', text)

    # 替换换行和多余空格
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = re.sub(r'\s+', ' ', text)

    # 去除首尾空格
    text = text.strip()

    return text


def clean_comments(raw_comments: List[dict], video_id: str) -> List[dict]:
    """
    批量清洗评论数据

    将爬虫抓取的原始评论列表清洗为标准化的评论明细数据。

    Args:
        raw_comments: 原始评论列表（fetch_comments 返回值）
        video_id: 关联的视频 ID

    Returns:
        标准化评论列表，每条包含:
            - video_id: 关联视频 ID
            - comment_id: 评论 ID
            - parent_comment_id: 父评论 ID（0 表示顶级评论）
            - comment_user: 评论用户昵称
            - comment_content: 清洗后的评论内容
            - comment_like: 评论点赞数
            - is_question: 是否提问（默认 0）
            - publish_time: 评论发布时间 (格式: YYYY-MM-DD HH:MM:SS)
    """
    cleaned: List[dict] = []

    for c in raw_comments:
        if not isinstance(c, dict):
            continue

        user = c.get("user", {})
        create_ts = int(c.get("create_time", 0))
        publish_time = ""
        if create_ts > 0:
            try:
                from datetime import datetime
                publish_time = datetime.fromtimestamp(create_ts).strftime("%Y-%m-%d %H:%M:%S")
            except (OSError, ValueError, OverflowError):
                publish_time = ""

        cleaned.append({
            "video_id": str(video_id),
            "comment_id": str(c.get("cid", "")),
            "parent_comment_id": str(c.get("reply_id", "0")),
            "comment_user": str(user.get("nickname", "")),
            "comment_content": clean_comment_text(c.get("text", "")),
            "comment_like": int(c.get("digg_count", 0)),
            "is_question": 0,  # 默认非提问，由 NLP 模块标记
            "publish_time": publish_time,
        })

    return cleaned
