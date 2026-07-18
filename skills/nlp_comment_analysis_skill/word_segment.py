"""
中文分词模块
使用 jieba 对评论进行精确模式分词，并过滤停用词
"""

import sys
import os
from typing import List, Dict, Optional

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


def segment_comments(
    comments: List[dict],
    stopwords_path: Optional[str] = None,
) -> List[dict]:
    """
    对评论列表进行分词处理

    处理逻辑:
        1. 使用 jieba 精确模式分词
        2. 加载停用词表，过滤停用词
        3. 过滤单字词和过短的词（长度小于 min_word_length）
        4. 保留分词结果和原文

    Args:
        comments: 标准化评论列表（每条包含 comment_id, comment_content 等字段）
        stopwords_path: 停用词表文件路径，默认从 nlp_config.yaml 读取

    Returns:
        分词结果列表，每条包含:
            - comment_id: 评论 ID
            - words: 分词后的 token 列表
            - full_text: 原始评论内容（未经分词）
    """
    try:
        import jieba
    except ImportError:
        raise ImportError("需要安装 jieba (pip install jieba)")

    # 读取 NLP 配置
    if stopwords_path is None:
        try:
            import yaml
            nlp_config_path = os.path.join(_project_root, 'config', 'nlp_config.yaml')
            with open(nlp_config_path, 'r', encoding='utf-8') as f:
                nlp_config = yaml.safe_load(f)
            stopwords_path = nlp_config.get("word_segment", {}).get(
                "stopwords_path", "assets/nlp_dict/stopwords.txt"
            )
            user_dict_path = nlp_config.get("word_segment", {}).get(
                "user_dict_path", ""
            )
            min_word_length = nlp_config.get("word_segment", {}).get(
                "min_word_length", 2
            )
            keep_digits = nlp_config.get("word_segment", {}).get(
                "keep_digits", False
            )
        except Exception:
            min_word_length = 2
            keep_digits = False
            user_dict_path = ""
    else:
        min_word_length = 2
        keep_digits = False
        user_dict_path = ""

    # 转换为绝对路径
    if stopwords_path and not os.path.isabs(stopwords_path):
        stopwords_path = os.path.join(_project_root, stopwords_path)
    if user_dict_path and not os.path.isabs(user_dict_path):
        user_dict_path = os.path.join(_project_root, user_dict_path)

    # 加载用户自定义词典
    if user_dict_path and os.path.exists(user_dict_path):
        jieba.load_userdict(user_dict_path)

    # 加载停用词表
    stopwords = _load_stopwords(stopwords_path)

    results: List[dict] = []
    for comment in comments:
        if not isinstance(comment, dict):
            continue

        comment_id = str(comment.get("comment_id", ""))
        full_text = str(comment.get("comment_content", ""))

        if not full_text.strip():
            continue

        # jieba 精确模式分词
        words = jieba.lcut(full_text.strip(), cut_all=False)

        # 过滤停用词、单字词、数字
        filtered = []
        for w in words:
            w = w.strip()
            if not w:
                continue
            if w in stopwords:
                continue
            if len(w) < min_word_length:
                continue
            if not keep_digits and w.isdigit():
                continue
            filtered.append(w)

        if filtered:
            results.append({
                "comment_id": comment_id,
                "words": filtered,
                "full_text": full_text,
            })

    return results


def _load_stopwords(stopwords_path: str) -> set:
    """
    加载停用词表

    Args:
        stopwords_path: 停用词表文件路径

    Returns:
        停用词集合
    """
    stopwords: set = set()
    if not stopwords_path or not os.path.exists(stopwords_path):
        # 内置基础停用词
        builtin = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人",
                   "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去",
                   "你", "会", "着", "没有", "看", "好", "自己", "这"}
        stopwords.update(builtin)
        return stopwords

    try:
        with open(stopwords_path, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip()
                if word:
                    stopwords.add(word)
    except Exception:
        pass

    return stopwords
