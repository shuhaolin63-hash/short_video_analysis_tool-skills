"""
NLP 评论分析模块
提供分词、话题聚类、疑问句提取功能
"""

from .word_segment import segment_comments
from .topic_cluster import cluster_topics
from .question_extract import extract_questions

__all__ = ["segment_comments", "cluster_topics", "extract_questions"]
