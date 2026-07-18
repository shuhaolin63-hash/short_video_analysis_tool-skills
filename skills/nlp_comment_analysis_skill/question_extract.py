"""
疑问句提取模块
使用关键词匹配 + SnowNLP 判断评论是否为疑问句
"""

import sys
import os
from typing import List, Dict, Optional

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


def extract_questions(comments: List[dict], keywords: list = None) -> List[dict]:
    """
    从评论列表中提取疑问句

    处理逻辑:
        1. 使用配置中的 question_keywords 进行关键词匹配
        2. 若安装了 SnowNLP，使用疑问语气判断辅助识别
        3. 对每条命中的评论标记 is_question=1
        4. 过滤过长/过短的文本

    Args:
        comments: 标准化评论列表
        keywords: 自定义疑问词列表，若为 None 则从 nlp_config.yaml 读取

    Returns:
        包含疑问标记的评论子集，每条在原有字段基础上增加 is_question=1
    """
    # 读取 NLP 配置
    if keywords is None:
        try:
            import yaml
            nlp_config_path = os.path.join(_project_root, 'config', 'nlp_config.yaml')
            with open(nlp_config_path, 'r', encoding='utf-8') as f:
                nlp_config = yaml.safe_load(f)
            qe_cfg = nlp_config.get("question_extract", {})
            keywords = qe_cfg.get("question_keywords", [])
            min_length = qe_cfg.get("min_question_length", 4)
            max_length = qe_cfg.get("max_question_length", 200)
        except Exception:
            keywords = ["怎么", "如何", "为什么", "多少钱", "哪里", "什么时候",
                        "有没有", "是不是", "能否", "什么", "能不能", "会不会",
                        "要不要", "多少", "哪个", "谁", "吗", "呢"]
            min_length = 4
            max_length = 200
    else:
        min_length = 4
        max_length = 200

    # 尝试导入 SnowNLP
    has_snownlp = False
    try:
        from snownlp import SnowNLP
        has_snownlp = True
    except ImportError:
        pass

    # 编译关键词正则
    import re
    keyword_patterns = []
    for kw in keywords:
        if kw:
            keyword_patterns.append(re.compile(re.escape(kw)))

    question_comments: List[dict] = []
    for comment in comments:
        if not isinstance(comment, dict):
            continue

        text = str(comment.get("comment_content", "")).strip()
        if not text:
            continue

        # 长度过滤
        if len(text) < min_length or len(text) > max_length:
            continue

        # 关键词匹配
        matched = False
        for pattern in keyword_patterns:
            if pattern.search(text):
                matched = True
                break

        # 如果安装了 SnowNLP，用疑问语气辅助判断
        if not matched and has_snownlp:
            try:
                s = SnowNLP(text)
                # 以问号结尾或包含问号
                if "?" in text or "？" in text:
                    matched = True
            except Exception:
                pass

        if matched:
            # 标记为疑问句
            question_comment = dict(comment)
            question_comment["is_question"] = 1
            question_comments.append(question_comment)

    return question_comments
