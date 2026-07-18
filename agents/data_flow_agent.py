# ============================================================
# 短视频解析工具 - 数据流数据结构
# Short Video Analysis Tool - Analysis Data Flow
# ============================================================

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class AnalysisData:
    """视频分析全流程数据容器，在各 skill 模块间传递数据"""

    # ---- 视频元数据 ----
    video_meta: Optional[dict] = None
    """清洗后的视频元数据，包含 video_id, title, author, play_count 等字段"""

    # ---- 评论数据 ----
    raw_comments: Optional[list] = None
    """原始评论列表（从爬虫直接获取，未经处理）"""

    cleaned_comments: Optional[list] = None
    """清洗后的评论列表，已去重、去无效"""

    segmented_comments: Optional[list] = None
    """分词结果，每条评论对应一个分词后的词列表"""

    # ---- NLP 分析结果 ----
    topics: Optional[dict] = None
    """LDA 聚类结果，格式：{topic_id: {keywords: [...], weight: float, ...}}"""

    questions: Optional[list] = None
    """提取的疑问评论列表，每条为 dict，包含 comment_id, content, like_count 等"""

    # ---- 媒体文件路径 ----
    cover_local_path: Optional[str] = None
    """封面图片的本地缓存路径"""

    wordcloud_path: Optional[str] = None
    """生成的词云图文件路径"""

    # ---- 原始输入 ----
    video_url: Optional[str] = None
    """原始视频链接"""

    platform: Optional[str] = None
    """平台标识，如 'douyin' / 'tiktok' / 'bilibili'"""

    # ---- 状态信息 ----
    status: str = "pending"
    """处理状态: pending / processing / done / error"""

    error_msg: Optional[str] = None
    """错误信息，status=error 时填充"""

    # ---- 扩展字段 ----
    extra: dict = field(default_factory=dict)
    """额外扩展字段，用于存储自定义数据"""
