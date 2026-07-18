# ============================================================
# 短视频解析工具 - 单视频分析 Agent
# 完整实现 6 步数据流：爬取 -> 下载封面 -> 清洗 -> NLP -> 导出
# ============================================================

import sys
import os
import time
import asyncio
import logging
from datetime import datetime
from typing import Optional

# 将项目根目录加入 sys.path，确保技能模块可被导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.data_flow_agent import AnalysisData

# ---- 配置加载 ----
try:
    import yaml

    _config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config", "global_config.yaml"
    )
    with open(_config_path, "r", encoding="utf-8") as f:
        GLOBAL_CONFIG = yaml.safe_load(f)
except Exception as e:
    GLOBAL_CONFIG = {}
    print(f"[Warning] 无法加载全局配置: {e}")

try:
    _nlp_config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config", "nlp_config.yaml"
    )
    with open(_nlp_config_path, "r", encoding="utf-8") as f:
        NLP_CONFIG = yaml.safe_load(f)
except Exception as e:
    NLP_CONFIG = {}
    print(f"[Warning] 无法加载 NLP 配置: {e}")

# ---- 日志器初始化 ----
_log_dir = GLOBAL_CONFIG.get("logging", {}).get("log_dir", "logs/")
_log_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), _log_dir
)
os.makedirs(_log_dir, exist_ok=True)

_log_level = getattr(logging, GLOBAL_CONFIG.get("logging", {}).get("level", "INFO"), logging.INFO)
_logger = logging.getLogger("SingleVideoAgent")
_logger.setLevel(_log_level)

# 文件 Handler
_fh = logging.FileHandler(
    os.path.join(_log_dir, f"single_agent_{datetime.now().strftime('%Y%m%d')}.log"),
    encoding="utf-8"
)
_fh.setLevel(_log_level)
_fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
_logger.addHandler(_fh)

# 控制台 Handler（可选）
if GLOBAL_CONFIG.get("logging", {}).get("console_output", True):
    _ch = logging.StreamHandler()
    _ch.setLevel(_log_level)
    _ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    _logger.addHandler(_ch)


class SingleVideoAgent:
    """单视频分析 Agent —— 完整串联 6 步数据流"""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or GLOBAL_CONFIG
        self.nlp_config = NLP_CONFIG
        self.logger = _logger

        # ---- 按需导入各 skill 模块（函数/类引用） ----
        self._import_skills()

    def _import_skills(self):
        """导入所有 skill 模块，根据各模块实际导出的 API 进行适配"""
        self.skills = {}

        # ---- 1. 爬虫抓取 skill ----
        # 实际导出的 API: SpiderFetchAPI (class) + fetch_video_meta (async) + fetch_comments (async)
        try:
            from skills.spider_fetch_skill import (
                SpiderFetchAPI,
                fetch_video_meta as _fetch_video_meta,
                fetch_comments as _fetch_comments,
            )
            self.skills["spider_fetch_api_cls"] = SpiderFetchAPI
            self.skills["spider_fetch_meta_fn"] = _fetch_video_meta
            self.skills["spider_fetch_comments_fn"] = _fetch_comments
            self.logger.info("[Skill] spider_fetch_skill 加载成功")
        except ImportError as e:
            self.skills["spider_fetch_api_cls"] = None
            self.logger.warning(f"[Skill] spider_fetch_skill 加载失败: {e}")

        # ---- 2. 封面下载 skill ----
        # 实际导出的 API: download_cover (async function)
        try:
            from skills.cover_download_skill import download_cover as _download_cover
            self.skills["cover_download_fn"] = _download_cover
            self.logger.info("[Skill] cover_download_skill 加载成功")
        except ImportError as e:
            self.skills["cover_download_fn"] = None
            self.logger.warning(f"[Skill] cover_download_skill 加载失败: {e}")

        # ---- 3. 数据清洗 skill ----
        # 实际导出的 API: clean_video_meta(sync), clean_comments(sync)
        try:
            from skills.data_clean_skill import (
                clean_video_meta as _clean_meta,
                clean_comments as _clean_comments,
            )
            self.skills["data_clean_meta_fn"] = _clean_meta
            self.skills["data_clean_comments_fn"] = _clean_comments
            self.logger.info("[Skill] data_clean_skill 加载成功")
        except ImportError as e:
            self.skills["data_clean_meta_fn"] = None
            self.skills["data_clean_comments_fn"] = None
            self.logger.warning(f"[Skill] data_clean_skill 加载失败: {e}")

        # ---- 4. NLP 评论分析 skill ----
        # 实际导出的 API: segment_comments(sync), cluster_topics(sync), extract_questions(sync)
        try:
            from skills.nlp_comment_analysis_skill import (
                segment_comments as _segment,
                cluster_topics as _cluster,
                extract_questions as _extract,
            )
            self.skills["nlp_segment_fn"] = _segment
            self.skills["nlp_cluster_fn"] = _cluster
            self.skills["nlp_extract_fn"] = _extract
            self.logger.info("[Skill] nlp_comment_analysis_skill 加载成功")
        except ImportError as e:
            self.skills["nlp_segment_fn"] = None
            self.skills["nlp_cluster_fn"] = None
            self.skills["nlp_extract_fn"] = None
            self.logger.warning(f"[Skill] nlp_comment_analysis_skill 加载失败: {e}")

        # ---- 5. Excel 导出 skill ----
        # 实际导出的 API: export_video_meta_table, export_comment_detail_table, export_hot_topic_table
        try:
            from skills.table_export_skill import (
                export_video_meta_table as _export_meta,
                export_comment_detail_table as _export_comment,
                export_hot_topic_table as _export_topic,
            )
            self.skills["table_export_meta_fn"] = _export_meta
            self.skills["table_export_comment_fn"] = _export_comment
            self.skills["table_export_topic_fn"] = _export_topic
            self.logger.info("[Skill] table_export_skill 加载成功")
        except ImportError as e:
            self.skills["table_export_meta_fn"] = None
            self.skills["table_export_comment_fn"] = None
            self.skills["table_export_topic_fn"] = None
            self.logger.warning(f"[Skill] table_export_skill 加载失败: {e}")

    # ---------------------------------------------------------------
    #  主入口
    # ---------------------------------------------------------------
    def run(self, url: str) -> AnalysisData:
        """
        执行完整分析流程

        参数:
            url: 视频链接（抖音 / TikTok / B站）

        返回:
            AnalysisData: 包含所有分析结果的数据对象
        """
        data = AnalysisData(video_url=url, status="processing")
        self.logger.info(f"===== 开始分析视频: {url} =====")

        try:
            # ---- 第 1 步：爬虫抓取（元数据 + 评论） ----
            # 异步操作统一通过 asyncio.run 同步执行
            _meta_raw, _comments_raw = self._step_spider_fetch(data)
            data.raw_comments = _comments_raw

            # ---- 第 2 步：数据清洗（同步，将原始元数据转为标准化格式） ----
            self._step_data_clean(data, _meta_raw)

            # ---- 第 3 步：封面下载（异步） ----
            self._step_cover_download(data)

            # ---- 第 4 步：NLP 分词 + 聚类 + 提问提取 ----
            self._step_nlp_analysis(data)

            # ---- 第 5 步：导出 Excel 表格 ----
            self._step_table_export(data)

            # ---- 第 6 步（可选）：生成词云图 ----
            self._step_wordcloud(data)

            data.status = "done"
            self.logger.info(f"===== 视频分析完成: {data.video_meta.get('video_id', 'N/A')} =====")

        except Exception as e:
            data.status = "error"
            data.error_msg = str(e)
            self.logger.error(f"视频分析失败: {e}", exc_info=True)

        return data

    # ---------------------------------------------------------------
    #  各步骤实现
    # ---------------------------------------------------------------
    def _step_spider_fetch(self, data: AnalysisData):
        """
        第 1 步：通过爬虫获取视频元数据和评论列表

        返回:
            (raw_meta, raw_comments): 原始元数据字典 + 原始评论列表
        """
        self.logger.info("[Step 1/6] 爬虫抓取元数据和评论...")

        api_cls = self.skills.get("spider_fetch_api_cls")
        fetch_meta_fn = self.skills.get("spider_fetch_meta_fn")
        fetch_comments_fn = self.skills.get("spider_fetch_comments_fn")

        if api_cls is None or fetch_meta_fn is None:
            self.logger.warning("[Step 1] spider_fetch_skill 不可用，跳过")
            data.raw_comments = []
            return {}, []

        try:
            # 异步执行爬虫抓取
            async def _crawl():
                api = api_cls()
                # 获取元数据
                meta = await fetch_meta_fn(data.video_url, api_adapter=api)
                # 提取视频 ID 和平台
                vid = meta.get("video_id", "")
                platform = meta.get("platform", "")
                # 获取评论
                max_pages = self.config.get("crawler", {}).get("comment", {}).get("max_pages", 0)
                comments = await fetch_comments_fn(vid, platform, max_pages=max_pages, api_adapter=api)
                await api.close()
                return meta, comments

            raw_meta, raw_comments = asyncio.run(_crawl())
            data.platform = raw_meta.get("platform", "unknown")

            comment_count = len(raw_comments)
            self.logger.info(f"[Step 1] 完成 — 平台: {data.platform}, "
                             f"视频ID: {raw_meta.get('video_id', 'N/A')}, "
                             f"评论: {comment_count} 条")
            return raw_meta, raw_comments

        except Exception as e:
            self.logger.error(f"[Step 1] 抓取失败: {e}")
            data.raw_comments = []
            return {}, []

    def _step_data_clean(self, data: AnalysisData, raw_meta: dict):
        """
        第 2 步：清洗原始数据（去重、去无效、标准化）
        先清洗元数据，再清洗评论
        """
        self.logger.info("[Step 2/6] 数据清洗...")

        clean_meta_fn = self.skills.get("data_clean_meta_fn")
        clean_comments_fn = self.skills.get("data_clean_comments_fn")

        if clean_meta_fn is None or clean_comments_fn is None:
            self.logger.warning("[Step 2] data_clean_skill 不可用，直接使用原始数据")
            # 即使 skill 不可用，也尽量从 raw_meta 提取基本信息
            data.video_meta = {
                "video_id": raw_meta.get("video_id", f"video_{int(time.time())}"),
                "video_url": data.video_url,
                "title_text": raw_meta.get("desc", ""),
                "publish_time": "",
                "author_name": raw_meta.get("author", {}).get("name", ""),
                "author_uid": raw_meta.get("author", {}).get("id", ""),
                "play_count": raw_meta.get("statistics", {}).get("play_count", 0),
                "like_count": raw_meta.get("statistics", {}).get("like_count", 0),
                "collect_count": raw_meta.get("statistics", {}).get("collect_count", 0),
                "share_count": raw_meta.get("statistics", {}).get("share_count", 0),
                "comment_total": raw_meta.get("statistics", {}).get("comment_count", 0),
                "cover_url": raw_meta.get("cover_data", {}).get("origin_cover", ""),
                "cover_local_path": "",
                "parse_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            data.cleaned_comments = data.raw_comments or []
            return

        # 清洗元数据
        video_meta = clean_meta_fn(raw_meta)
        video_meta["video_url"] = data.video_url
        data.video_meta = video_meta

        # 清洗评论
        video_id = video_meta.get("video_id", "unknown")
        cleaned = clean_comments_fn(data.raw_comments or [], video_id)
        data.cleaned_comments = cleaned

        self.logger.info(f"[Step 2] 清洗完成 — 评论: {len(data.raw_comments or [])} -> "
                         f"{len(data.cleaned_comments)} 条")

    def _step_cover_download(self, data: AnalysisData):
        """第 3 步：下载视频封面到本地缓存"""
        self.logger.info("[Step 3/6] 下载视频封面...")

        download_fn = self.skills.get("cover_download_fn")
        if download_fn is None:
            self.logger.warning("[Step 3] cover_download_skill 不可用，跳过")
            return

        cover_url = data.video_meta.get("cover_url", "") if data.video_meta else ""
        if not cover_url:
            self.logger.warning("[Step 3] 无封面图链接，跳过下载")
            return

        video_id = data.video_meta.get("video_id", "unknown")

        try:
            local_path = asyncio.run(download_fn(cover_url, video_id))
            data.cover_local_path = local_path
            # 回填到 video_meta
            if data.video_meta:
                data.video_meta["cover_local_path"] = local_path
            self.logger.info(f"[Step 3] 封面已下载至: {local_path}")
        except Exception as e:
            self.logger.warning(f"[Step 3] 封面下载失败: {e}")

    def _step_nlp_analysis(self, data: AnalysisData):
        """第 4 步：NLP 分析（分词、LDA 聚类、疑问句提取）"""
        self.logger.info("[Step 4/6] NLP 评论分析（分词 + 聚类 + 疑问提取）...")

        segment_fn = self.skills.get("nlp_segment_fn")
        cluster_fn = self.skills.get("nlp_cluster_fn")
        extract_fn = self.skills.get("nlp_extract_fn")

        if segment_fn is None:
            self.logger.warning("[Step 4] nlp_comment_analysis_skill 不可用，跳过")
            data.segmented_comments = []
            data.topics = {}
            data.questions = []
            return

        comments = data.cleaned_comments or []

        # 分词
        segmented = segment_fn(comments)
        data.segmented_comments = segmented

        # 话题聚类（需要分词结果）
        if cluster_fn is not None and segmented:
            topics = cluster_fn(segmented)
            data.topics = topics
        else:
            data.topics = {}

        # 疑问句提取
        if extract_fn is not None and comments:
            questions = extract_fn(comments)
            data.questions = questions
        else:
            data.questions = []

        topic_count = len(data.topics or {})
        question_count = len(data.questions or [])
        self.logger.info(f"[Step 4] NLP 完成 — 话题簇: {topic_count} 个, "
                         f"疑问评论: {question_count} 条")

    def _step_table_export(self, data: AnalysisData):
        """第 5 步：生成 3 张 Excel 表格"""
        self.logger.info("[Step 5/6] 导出 Excel 表格...")

        export_meta_fn = self.skills.get("table_export_meta_fn")
        export_comment_fn = self.skills.get("table_export_comment_fn")
        export_topic_fn = self.skills.get("table_export_topic_fn")

        if export_meta_fn is None:
            self.logger.warning("[Step 5] table_export_skill 尚未实现，跳过")
            return

        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            self.config.get("output", {}).get("excel_dir", "output/excel_table/")
        )
        os.makedirs(output_dir, exist_ok=True)

        # 从全局配置获取文件名
        excel_cfg = self.config.get("output", {})
        meta_filename = excel_cfg.get("excel_filename_video_meta", "video_meta_info.xlsx")
        comment_filename = excel_cfg.get("excel_filename_comment_detail", "comment_detail.xlsx")
        topic_filename = excel_cfg.get("excel_filename_hot_topic", "comment_hot_topic.xlsx")

        meta_path = os.path.join(output_dir, meta_filename)
        comment_path = os.path.join(output_dir, comment_filename)
        topic_path = os.path.join(output_dir, topic_filename)

        excel_paths = {}

        try:
            # 表1: 视频基础信息总表
            # export_video_meta_table 接收列表，将单个 meta 包装为列表
            meta_list = [data.video_meta] if data.video_meta else []
            if meta_list:
                export_meta_fn(meta_list, meta_path)
                excel_paths["video_meta_info"] = os.path.abspath(meta_path)
                self.logger.info(f"  -> 视频基础信息表: {meta_path}")

            # 表2: 全量评论明细表
            if data.cleaned_comments:
                export_comment_fn(data.cleaned_comments, comment_path)
                excel_paths["comment_detail"] = os.path.abspath(comment_path)
                self.logger.info(f"  -> 评论明细表: {comment_path}")

            # 表3: 评论热点问题汇总表
            if data.topics:
                video_id = data.video_meta.get("video_id", "") if data.video_meta else ""
                export_topic_fn(data.topics, topic_path, video_id=video_id)
                excel_paths["comment_hot_topic"] = os.path.abspath(topic_path)
                self.logger.info(f"  -> 热点问题表: {topic_path}")

            data.extra["excel_paths"] = excel_paths
            self.logger.info(f"[Step 5] 共生成 {len(excel_paths)} 张 Excel 表格")

        except Exception as e:
            self.logger.error(f"[Step 5] 表格导出失败: {e}")

    def _step_wordcloud(self, data: AnalysisData):
        """第 6 步（可选）：生成词云图"""
        # 根据 config 判断是否生成
        if not NLP_CONFIG.get("wordcloud", {}).get("generate_wordcloud", True):
            self.logger.info("[Step 6/6] 词云图已禁用（配置关闭），跳过")
            return

        self.logger.info("[Step 6/6] 生成词云图...")

        try:
            from wordcloud import WordCloud
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError:
            self.logger.warning("[Step 6] wordcloud / matplotlib 未安装，跳过词云生成")
            return

        if not data.segmented_comments:
            self.logger.warning("[Step 6] 无分词数据，跳过词云生成")
            return

        # 汇总所有词语
        word_freq = {}
        for seg_item in data.segmented_comments:
            words = seg_item.get("words", [])
            if isinstance(words, list):
                for word in words:
                    word = word.strip()
                    if len(word) >= 2:
                        word_freq[word] = word_freq.get(word, 0) + 1

        if not word_freq:
            self.logger.warning("[Step 6] 无有效词汇，跳过词云生成")
            return

        wc_cfg = NLP_CONFIG.get("wordcloud", {})
        video_id = data.video_meta.get("video_id", "unknown")

        try:
            wc = WordCloud(
                font_path=wc_cfg.get("font_path", "C:/Windows/Fonts/simhei.ttf"),
                background_color=wc_cfg.get("background_color", "white"),
                width=wc_cfg.get("width", 800),
                height=wc_cfg.get("height", 600),
                max_words=wc_cfg.get("max_words", 200),
            )
            wc.generate_from_frequencies(word_freq)

            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                self.config.get("output", {}).get("wordcloud_dir", "output/wordcloud_img/")
            )
            os.makedirs(output_dir, exist_ok=True)

            filename = f"comment_wordcloud_{video_id}.png"
            output_path = os.path.join(output_dir, filename)
            wc.to_file(output_path)
            data.wordcloud_path = output_path

            plt.close("all")
            self.logger.info(f"[Step 6] 词云图已生成: {output_path}")

        except Exception as e:
            self.logger.warning(f"[Step 6] 词云生成失败: {e}")
