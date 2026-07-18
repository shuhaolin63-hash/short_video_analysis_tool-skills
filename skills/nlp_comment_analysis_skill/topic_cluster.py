"""
话题聚类模块
使用 TF-IDF + LDA 模型对分词后的评论进行话题聚类
"""

import sys
import os
from typing import List, Dict, Optional

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


def cluster_topics(
    segmented_comments: List[dict],
    num_topics: int = 5,
) -> Dict[int, dict]:
    """
    对分词后的评论进行 LDA 话题聚类

    处理逻辑:
        1. 使用 sklearn 的 TfidfVectorizer 将文本转为 TF-IDF 特征矩阵
        2. 使用 LatentDirichletAllocation 进行话题建模
        3. 为每个话题提取关键词和关联评论
        4. 计算每个话题的权重

    Args:
        segmented_comments: 分词结果列表（segment_comments 返回值）
        num_topics: 话题数量，默认从 nlp_config.yaml 读取，此处为 fallback

    Returns:
        话题聚类结果字典，key 为 topic_id (0 ~ num_topics-1)，value 包含:
            - keywords: 该话题的关键词列表
            - comment_ids: 与该话题关联的评论 ID 列表
            - weight: 话题权重（该话题评论数 / 总评论数）
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.decomposition import LatentDirichletAllocation
    except ImportError:
        raise ImportError("需要安装 scikit-learn (pip install scikit-learn)")

    # 读取 NLP 配置
    try:
        import yaml
        nlp_config_path = os.path.join(_project_root, 'config', 'nlp_config.yaml')
        with open(nlp_config_path, 'r', encoding='utf-8') as f:
            nlp_config = yaml.safe_load(f)
        topic_cfg = nlp_config.get("topic_cluster", {})
        num_topics = topic_cfg.get("num_topics", num_topics)
        num_words_per_topic = topic_cfg.get("num_words_per_topic", 10)
        lda_passes = topic_cfg.get("lda_passes", 10)
        random_state = topic_cfg.get("random_state", 42)
        max_tfidf_features = topic_cfg.get("max_tfidf_features", 1000)
        min_df = topic_cfg.get("min_df", 2)
        max_df = topic_cfg.get("max_df", 0.85)
    except Exception:
        num_words_per_topic = 10
        lda_passes = 10
        random_state = 42
        max_tfidf_features = 1000
        min_df = 2
        max_df = 0.85

    if not segmented_comments:
        return {}

    # 构建文档列表（用空格连接分词结果）
    documents = [" ".join(item.get("words", [])) for item in segmented_comments]
    comment_ids = [item.get("comment_id", "") for item in segmented_comments]

    # TF-IDF 向量化
    vectorizer = TfidfVectorizer(
        max_features=max_tfidf_features,
        min_df=min_df,
        max_df=max_df,
        stop_words="english",  # 英文停用词，中文停用词已在分词阶段过滤
    )
    tfidf_matrix = vectorizer.fit_transform(documents)

    # 获取特征词列表
    feature_names = vectorizer.get_feature_names_out()

    # LDA 模型训练
    lda = LatentDirichletAllocation(
        n_components=num_topics,
        max_iter=lda_passes,
        random_state=random_state,
        learning_method="online",
    )
    lda.fit(tfidf_matrix)

    # 文档-话题分布矩阵
    doc_topic_dist = lda.transform(tfidf_matrix)

    # 构建结果
    topics: Dict[int, dict] = {}

    for topic_idx in range(lda.n_components):
        # 提取前 N 个关键词
        top_features_idx = lda.components_[topic_idx].argsort()[:-num_words_per_topic - 1:-1]
        keywords = [str(feature_names[i]) for i in top_features_idx]

        # 找到与该话题关联的评论（该话题概率最大的文档）
        topic_comment_ids = []
        for doc_idx, dist in enumerate(doc_topic_dist):
            if dist.argmax() == topic_idx:
                topic_comment_ids.append(str(comment_ids[doc_idx]))

        # 话题权重 = 该话题的评论数 / 总评论数
        total_docs = len(segmented_comments)
        topic_weight = len(topic_comment_ids) / total_docs if total_docs > 0 else 0

        topics[topic_idx] = {
            "keywords": keywords,
            "comment_ids": topic_comment_ids,
            "weight": round(topic_weight, 4),
        }

    return topics
