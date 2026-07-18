# 短视频数据采集与分析工具

> 抖音 / TikTok / B站 视频数据全维度采集 + 评论智能分析 + Excel多表导出

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)

---

## 功能简介

一键采集短视频全维度数据，输出结构化的Excel报表和可视化结果。

| 功能模块 | 能力 |
|---------|------|
| 🕷️ 数据爬取 | 视频元数据、作者信息、互动数据、全量评论 |
| 🖼️ 封面下载 | 高清封面自动缓存与归档 |
| 🧹 数据清洗 | 去表情、去@、去URL、标准化格式、时间戳转换 |
| 🧠 NLP智能分析 | jieba分词、LDA话题聚类、用户疑问提取 |
| 📊 Excel多表导出 | 视频基础信息表 + 评论明细表 + 热点话题汇总表 |
| ☁️ 词云生成 | 评论区高频词可视化 |

---

## 目录结构

```
short_video_analysis_tool/
├── config/                        # 统一配置
│   ├── global_config.yaml         # 爬虫/输出/日志配置
│   ├── nlp_config.yaml            # 分词/LDA/词云配置
│   └── table_template.yaml        # Excel表列定义模板
├── agents/                        # 任务调度
│   ├── single_video_agent.py      # 单视频全流程解析
│   ├── batch_video_agent.py       # 批量视频解析
│   └── data_flow_agent.py         # AnalysisData 数据载体
├── scripts/                       # CLI入口
│   ├── run_single_analyze.py      # 单条分析
│   ├── run_batch_analyze.py       # 批量分析
│   └── clear_cache.py             # 缓存清理
├── skills/                        # 5大核心技能
│   ├── spider_fetch_skill/        # 爬虫抓取
│   ├── cover_download_skill/      # 封面下载
│   ├── data_clean_skill/          # 数据清洗
│   ├── nlp_comment_analysis_skill/ # NLP评论分析
│   └── table_export_skill/        # Excel导出
├── output/                        # 输出成果
│   ├── excel_table/               # 3张Excel表
│   ├── wordcloud_img/             # 词云图
│   └── cover_export/              # 封面归档
├── assets/ (cache_cover/, nlp_dict/)
└── reference/Douyin_TikTok_Download_API/
```

---

## 输出成果（3表 + 封面 + 词云）

| 文件 | 说明 | 字段数 |
|------|------|:------:|
| `video_meta_info.xlsx` | 视频基础信息总表 | 14字段 |
| `comment_detail.xlsx` | 全量评论明细表 | 8字段 |
| `comment_hot_topic.xlsx` | 评论热点话题汇总表 | 8字段 |
| `cover_export/` | 高清封面原图归档 | - |
| `wordcloud_img/` | 评论区词云可视化 | - |

---

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 底层爬虫引擎
cd reference/Douyin_TikTok_Download_API && pip install -r requirements.txt && cd ../..

# 单条视频分析
python scripts/run_single_analyze.py --url "https://v.douyin.com/xxxxx/"

# 批量分析
python scripts/run_batch_analyze.py --file links.txt
```

---

## 数据流转

```
视频链接 → 爬虫抓取(元数据+评论)
        → 封面下载
        → 数据清洗(去表情/去重/标准化)
        → NLP分析(分词→LDA聚类→疑问提取)
        → Excel多表导出 + 词云图生成
```

---

## 依赖

```
pyyaml, httpx, aiofiles, pandas, openpyxl,
jieba, scikit-learn, snownlp, wordcloud,
matplotlib, pillow, tqdm
```

---

## License

Apache 2.0
