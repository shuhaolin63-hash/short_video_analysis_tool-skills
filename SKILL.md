---
name: "short-video-analysis-tool"
description: "抖音/TikTok/B站短视频全链路解析工具：爬取元数据+评论、下载封面、NLP评论热点挖掘、生成3张Excel分析表。当用户需要分析短视频、导出评论、提取观众关注热点、批量解析视频链接时调用。"
---

# 📊 短视频解析工具 — Short Video Analysis Tool

> 你还在手动复制粘贴评论？还在用眼睛一条条刷评论区找热点？
> **把它交给 30 秒全自动的短视频解析流水线。**

📡 爬取元数据+评论 · 🧹 数据清洗 · 🧠 NLP 热点挖掘 · 📊 三表 Excel 归一输出 · 🖼️ 封面自动归档

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![Douyin](https://img.shields.io/badge/platform-Douyin-red) ![TikTok](https://img.shields.io/badge/platform-TikTok-black) ![Bilibili](https://img.shields.io/badge/platform-Bilibili-00A1D6)

🆕 基于 [Douyin_TikTok_Download_API](https://github.com/Evil0ctal/Douyin_TikTok_Download_API) V4.1.2 封装 · 支持抖音 / TikTok / Bilibili 三平台 · 单条 & 批量

---

## 📋 目录

- [🎯 适用场景](#-适用场景)
- [📦 安装](#-安装)
- [🚀 使用](#-使用)
- [🏗️ 项目架构](#️-项目架构)
- [🧬 数据流转](#-数据流转)
- [📊 输出成果详解](#-输出成果详解)
- [⚙️ 配置参考](#️-配置参考)
- [🧠 底层爬虫能力](#-底层爬虫能力)
- [🔧 功能特性](#-功能特性)
- [⚠️ 注意事项与法律声明](#️-注意事项与法律声明)
- [📄 License](#-license)

---

## 🎯 适用场景

当用户说出以下任一句话时，**立即调用本 Skill**：

| 场景 | 触发词 |
|------|--------|
| 🔍 **单视频分析** | "帮我分析这个抖音" / "看看这个视频的数据" |
| 📋 **评论导出** | "导出评论到Excel" / "把评论存下来" |
| 🔥 **热点挖掘** | "评论区在讨论什么" / "观众最关心什么" |
| 📦 **批量处理** | "批量分析这10个视频" / "帮我跑一批链接" |
| 🖼️ **封面下载** | "下载这个视频的封面" / "保存封面图片" |
| 📊 **数据报告** | "出个视频数据报告" / "生成分析表格" |

---

## 📦 安装

### 环境要求

- Python 3.10+
- 操作系统：Windows / macOS / Linux

### 一键安装

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/short-video-analysis-tool.git
cd short_video_analysis_tool

# 2. 安装核心依赖
pip install -r requirements.txt

# 3. 安装底层爬虫引擎
cd reference/Douyin_TikTok_Download_API
pip install -r requirements.txt
cd ../..
```

### 依赖清单

```
# 核心依赖
pyyaml>=6.0              # 配置解析
httpx>=0.27.0             # HTTP客户端
aiofiles>=23.0            # 异步文件操作
pandas>=2.0               # 数据处理
openpyxl>=3.1             # Excel读写
jieba>=0.42               # 中文分词
scikit-learn>=1.3         # LDA话题聚类
snownlp>=0.12             # 中文NLP（疑问语气判断）
wordcloud>=1.9            # 词云图生成
matplotlib>=3.7           # 词云渲染
pillow>=10.0              # 图片处理
tqdm>=4.65                # 进度条

# 底层爬虫（reference/Douyin_TikTok_Download_API/requirements.txt）
# httpx, aiofiles, pyyaml, fastapi, uvicorn, pycryptodomex, lz4, browser-cookie3 ...
```

---

## 🚀 使用

### 🎬 单条视频分析

```bash
python scripts/run_single_analyze.py --url "https://v.douyin.com/xxxxx/"
```

30 秒后你就能拿到：
- 📊 `output/excel_table/video_meta_info.xlsx` — 视频信息总表
- 📋 `output/excel_table/comment_detail.xlsx` — 全量评论明细
- 🔥 `output/excel_table/comment_hot_topic.xlsx` — 热点话题汇总
- 🖼️ `output/cover_export/` — 高清封面原图
- ☁️ `output/wordcloud_img/` — 评论词云

### 📦 批量分析

```bash
# 从文件读取链接（每行一个URL）
python scripts/run_batch_analyze.py --file links.txt

# 从命令行传入
python scripts/run_batch_analyze.py --urls "url1,url2,url3"

# 自定义间隔（秒）
python scripts/run_batch_analyze.py --file links.txt --delay 2.0

# 遇错即停
python scripts/run_batch_analyze.py --file links.txt --stop-on-error
```

### 🧹 清理缓存

```bash
# 仅清理缓存和日志
python scripts/clear_cache.py

# 清理全部（含输出成果）
python scripts/clear_cache.py --all

# 预览模式（只列不删）
python scripts/clear_cache.py --dry-run
```

---

## 🏗️ 项目架构

```
short_video_analysis_tool/
│
├── 📁 config/                        # 📐 全局配置
│   ├── global_config.yaml            #   爬虫延时 · 代理 · 输出路径 · Excel 格式
│   ├── nlp_config.yaml               #   分词参数 · LDA 超参 · 疑问关键词 · 词云配置
│   └── table_template.yaml           #   三张 Excel 表的列定义 · 表头 · 宽度 · 类型
│
├── 📁 agents/                        # 🤖 任务调度智能体（编排引擎）
│   ├── data_flow_agent.py            #   AnalysisData dataclass —— 全流程数据载体
│   ├── single_video_agent.py         #   单条视频：6 步流水线编排
│   └── batch_video_agent.py          #   批量视频：进度条 + 延时 + 容错
│
├── 📁 skills/                        # 🧠 五大核心技能（独立可复用，按需导入）
│   │
│   ├── spider_fetch_skill/           # 📡 爬虫抓取
│   │   ├── api_adapter.py            #   SpiderFetchAPI — 封装 HybridCrawler 懒加载
│   │   ├── fetch_meta_data.py        #   fetch_video_meta() — 异步获取元数据
│   │   └── fetch_comment_data.py     #   fetch_comments() — 三平台分页评论
│   │
│   ├── cover_download_skill/         # 🖼️ 封面下载管理
│   │   ├── download_single_cover.py  #   download_cover() — 异步下载高清封面
│   │   └── cover_file_sort.py        #   export_covers() — 缓存 → 输出目录归档
│   │
│   ├── data_clean_skill/             # 🧹 数据清洗
│   │   ├── meta_cleaner.py           #   clean_video_meta() — 数字格式化 · 时间戳转换
│   │   └── comment_cleaner.py        #   clean_comments() — 去表情 · 去@ · 去URL
│   │
│   ├── nlp_comment_analysis_skill/   # 🧠 NLP 评论语义挖掘
│   │   ├── word_segment.py           #   segment_comments() — jieba 精确分词
│   │   ├── topic_cluster.py          #   cluster_topics() — LDA 话题聚类
│   │   └── question_extract.py       #   extract_questions() — 疑问句 + 高频问题
│   │
│   └── table_export_skill/           # 📊 Excel 多表导出
│       ├── export_video_meta_table.py    #   → video_meta_info.xlsx（14 字段）
│       ├── export_comment_detail_table.py # → comment_detail.xlsx（8 字段）
│       └── export_hot_topic_table.py      # → comment_hot_topic.xlsx（8 字段）
│
├── 📁 scripts/                       # 🚀 用户入口
│   ├── run_single_analyze.py         #   单条视频分析 CLI
│   ├── run_batch_analyze.py          #   批量视频分析 CLI
│   └── clear_cache.py                #   缓存 & 日志清理
│
├── 📁 output/                        # 📦 最终交付物
│   ├── excel_table/                  #   3 张 Excel 表格（核心输出）
│   ├── wordcloud_img/                #   评论词云图（可视化）
│   └── cover_export/                 #   高清封面原图（归档）
│
├── 📁 assets/                        # 📎 静态资源
│   ├── cache_cover/                  #   封面缓存（临时）
│   ├── nlp_dict/                     #   停用词表 · 自定义词典
│   └── static_ui/                    #   前端静态素材
│
├── 📁 logs/                          # 📝 运行日志
│
├── 📁 reference/                     # 🔗 第三方开源引擎（只读，不改动）
│   └── Douyin_TikTok_Download_API/   #   HybridCrawler · 三平台爬虫 SDK
│
├── .gitignore
├── requirements.txt
├── SKILL.md
└── README.md
```

---

## 🧬 数据流转

```
                    ┌─────────────────────────────────────┐
                    │        用户输入视频链接               │
                    │  "帮我分析这个抖音视频"                │
                    └──────────┬──────────────────────────┘
                               │
                               ▼
  ┌───────────────────────────────────────────────────────────┐
  │ Step 1: spider_fetch_skill                                │
  │  ├─ HybridCrawler.hybrid_parsing_single_video(url)        │
  │  │   → video_id, platform, desc, author, statistics       │
  │  │   → cover_data, hashtags, music                         │
  │  └─ fetch_video_comments(aweme_id, cursor) ← 分页循环      │
  │      → [{cid, text, digg_count, create_time, user}, ...]  │
  └──────────────────┬────────────────────────────────────────┘
                     │
                     ▼
  ┌───────────────────────────────────────────────────────────┐
  │ Step 2: cover_download_skill                              │
  │  └─ download_cover(cover_url, video_id)                   │
  │      → assets/cache_cover/{video_id}_cover.jpg            │
  │      → output/cover_export/{video_id}_cover.jpg (归档)    │
  └──────────────────┬────────────────────────────────────────┘
                     │
                     ▼
  ┌───────────────────────────────────────────────────────────┐
  │ Step 3: data_clean_skill                                  │
  │  ├─ clean_video_meta(raw)                                 │
  │  │   → 14 字段标准化：数字格式化 · 时间戳转换 · 去异常值   │
  │  └─ clean_comments(raw_comments, video_id)                │
  │      → 去 emoji · 去 @ 提及 · 去 URL · 去重 · 去空        │
  └──────────────────┬────────────────────────────────────────┘
                     │
                     ▼
  ┌───────────────────────────────────────────────────────────┐
  │ Step 4: nlp_comment_analysis_skill                        │
  │  ├─ segment_comments(cleaned_comments)                    │
  │  │   → jieba 精确分词 · 停用词过滤 · 短词过滤             │
  │  ├─ cluster_topics(segmented)                             │
  │  │   → TF-IDF 向量化 → LDA 建模 → {话题: 关键词, 权重}   │
  │  └─ extract_questions(cleaned_comments)                   │
  │      → 关键词匹配 + SnowNLP → 标记 is_question=1          │
  └──────────────────┬────────────────────────────────────────┘
                     │
                     ▼
  ┌───────────────────────────────────────────────────────────┐
  │ Step 5: table_export_skill                                │
  │  ├─ export_video_meta_table()    → video_meta_info.xlsx   │
  │  ├─ export_comment_detail_table() → comment_detail.xlsx   │
  │  └─ export_hot_topic_table()     → comment_hot_topic.xlsx │
  └──────────────────┬────────────────────────────────────────┘
                     │
                     ▼
  ┌───────────────────────────────────────────────────────────┐
  │ Step 6: 词云生成（可选）                                    │
  │  └─ wordcloud.WordCloud → comment_wordcloud_{id}.png      │
  └───────────────────────────────────────────────────────────┘
```

---

## 📊 输出成果详解

### 表 1：`video_meta_info.xlsx` — 视频基础信息总表

> 📍 `output/excel_table/video_meta_info.xlsx`
> 📄 Sheet 名：`视频基础信息`
> 📏 每条视频 1 行，14 个字段

| # | 字段名 | 类型 | 说明 |
|:-:|--------|:----:|------|
| 1 | `video_id` | string | 视频全局唯一 ID（关联评论表主键） |
| 2 | `video_url` | string | 原视频链接 |
| 3 | `title_text` | string | 视频标题 / 完整文案 |
| 4 | `publish_time` | datetime | 发布时间 |
| 5 | `author_name` | string | 作者昵称 |
| 6 | `author_uid` | string | 作者平台 ID |
| 7 | `play_count` | int | 播放量 |
| 8 | `like_count` | int | 点赞数 |
| 9 | `collect_count` | int | 收藏数 |
| 10 | `share_count` | int | 转发数 |
| 11 | `comment_total` | int | 总评论数 |
| 12 | `cover_url` | string | 封面原图网络地址 |
| 13 | `cover_local_path` | string | 本地封面文件路径 |
| 14 | `parse_time` | datetime | 本工具解析时间 |

### 表 2：`comment_detail.xlsx` — 全量评论明细表

> 📍 `output/excel_table/comment_detail.xlsx`
> 📄 Sheet 名：`评论明细`
> 📏 每条评论 1 行，8 个字段

| # | 字段名 | 类型 | 说明 |
|:-:|--------|:----:|------|
| 1 | `video_id` | string | 关联视频 ID |
| 2 | `comment_id` | string | 评论唯一 ID |
| 3 | `parent_comment_id` | string | 父评论 ID（区分一级 / 二级回复） |
| 4 | `comment_user` | string | 评论用户昵称 |
| 5 | `comment_content` | string | 清洗后的纯评论文本 |
| 6 | `comment_like` | int | 本条评论获赞数 |
| 7 | `is_question` | int | NLP 标记：1=提问，0=非提问 |
| 8 | `publish_time` | datetime | 评论发布时间 |

### 表 3：`comment_hot_topic.xlsx` — 评论热点问题汇总表

> 📍 `output/excel_table/comment_hot_topic.xlsx`
> 📄 Sheet 名：`评论热点问题`
> 📏 每个话题簇 1 行，8 个字段

| # | 字段名 | 类型 | 说明 |
|:-:|--------|:----:|------|
| 1 | `video_id` | string | 关联视频 ID |
| 2 | `topic_id` | int | 话题聚类编号 |
| 3 | `topic_keyword` | string | 该话题核心关键词（逗号分隔） |
| 4 | `sample_question` | string | 代表性问题原文 |
| 5 | `total_comment_num` | int | 归属该话题的评论数 |
| 6 | `avg_like` | float | 话题下评论平均点赞 |
| 7 | `topic_weight` | float | 话题热度权重（0~1，越高越热） |
| 8 | `related_comment_ids` | string | 关联评论 ID 列表（逗号分隔） |

### 附加输出

| 输出 | 位置 | 格式 |
|------|------|------|
| 🖼️ 封面原图 | `output/cover_export/{video_id}_cover.jpg` | JPG |
| ☁️ 词云图 | `output/wordcloud_img/comment_wordcloud_{video_id}.png` | PNG |

---

## ⚙️ 配置参考

### `config/global_config.yaml` — 全局配置

```yaml
crawler:
  request_delay: 1.5           # 请求间隔（秒）
  max_retries: 3               # 失败重试次数
  timeout: 10                  # HTTP 超时（秒）
  proxies:
    http: ""                   # HTTP 代理
    https: ""                  # HTTPS 代理
  comment:
    page_size: 20              # 每页评论数
    max_pages: 0               # 最大页数（0=不限）
    fetch_replies: true        # 是否抓取二级回复
  cover:
    download_concurrency: 5    # 封面并发下载数
    download_timeout: 30       # 封面下载超时

output:
  excel_dir: "output/excel_table/"
  cover_export_dir: "output/cover_export/"
  wordcloud_dir: "output/wordcloud_img/"
  cache_cover_dir: "assets/cache_cover/"

table_format:
  header_font_bold: true
  auto_column_width: true
  freeze_first_row: true
  add_auto_filter: true
  max_column_width: 60

logging:
  level: "INFO"                # DEBUG / INFO / WARNING / ERROR
  log_dir: "logs/"
  log_retention_days: 7
  console_output: true
```

### `config/nlp_config.yaml` — NLP 配置

```yaml
word_segment:
  stopwords_path: "assets/nlp_dict/stopwords.txt"
  user_dict_path: "assets/nlp_dict/user_dict.txt"
  keep_digits: false
  min_word_length: 2
  use_precise_mode: true

topic_cluster:
  method: "lda"                # lda / bertopic
  num_topics: 5
  num_words_per_topic: 10
  lda_passes: 10
  random_state: 42
  max_tfidf_features: 1000
  min_df: 2
  max_df: 0.85

question_extract:
  question_keywords: ["怎么", "如何", "为什么", "多少钱", "哪里",
    "什么时候", "有没有", "是不是", "能否", "什么", "能不能",
    "会不会", "要不要", "多少", "哪个", "谁", "吗", "呢"]
  min_question_length: 4
  max_question_length: 200

wordcloud:
  background_color: "white"
  width: 800
  height: 600
  max_words: 200
  font_path: "C:/Windows/Fonts/simhei.ttf"
  generate_wordcloud: true
```

---

## 🧠 底层爬虫能力

基于 `reference/Douyin_TikTok_Download_API` 中的三个平台专用爬虫。

### 🎯 混合解析入口

```python
from crawlers.hybrid.hybrid_crawler import HybridCrawler

crawler = HybridCrawler()
result = await crawler.hybrid_parsing_single_video(url, minimal=True)
# → 自动识别 douyin / tiktok / bilibili
# → 返回结构化数据：type, platform, video_id, desc, 
#   author, statistics, cover_data, hashtags, music
```

### 🎬 抖音 (Douyin)

| 能力 | 方法 | 签名加密 |
|------|------|:--------:|
| 视频详情 | `fetch_one_video(aweme_id)` | A-Bogus |
| 评论列表 | `fetch_video_comments(aweme_id, cursor, count)` | X-Bogus |
| 评论回复 | `fetch_video_comments_reply(item_id, comment_id, cursor, count)` | X-Bogus |
| 用户信息 | `handler_user_profile(sec_user_id)` | X-Bogus |
| 用户作品 | `fetch_user_post_videos(sec_user_id, max_cursor, count)` | A-Bogus |
| 用户喜欢 | `fetch_user_like_videos(sec_user_id, max_cursor, count)` | A-Bogus |
| Token 生成 | `gen_real_msToken()` / `gen_ttwid()` / `gen_verify_fp()` | — |

### 🌍 TikTok

| 能力 | 方法 |
|------|------|
| 视频详情 | `fetch_one_video(itemId)` |
| 评论列表 | `fetch_post_comment(aweme_id, cursor, count, current_region)` |
| 评论回复 | `fetch_post_comment_reply(item_id, comment_id, cursor, count)` |
| 用户信息 | `fetch_user_profile(uniqueId, secUid)` |
| 用户作品 | `fetch_user_post(secUid, cursor, count)` |
| 用户粉丝/关注 | `fetch_user_fans()` / `fetch_user_follow()` |

### 🐦 Bilibili

| 能力 | 方法 |
|------|------|
| 视频详情 | `fetch_one_video(bv_id)` |
| 评论列表 | `fetch_video_comments(bv_id, pn)` |
| 评论回复 | `fetch_comment_reply(bv_id, pn, rpid)` |
| 播放地址 | `fetch_video_playurl(bv_id, cid)` |
| 用户信息 | `fetch_user_profile(uid)` |
| 弹幕 | `fetch_video_danmaku(cid)` — 返回 XML |

---

## 🔧 功能特性

### 🧱 模块化 Skills 架构

五大 Skills 各自独立、按需加载，任一模块缺失不影响整体流程：

```
skills/
├── spider_fetch_skill          📡 爬取
├── cover_download_skill        🖼️ 封面
├── data_clean_skill            🧹 清洗
├── nlp_comment_analysis_skill  🧠 分析
└── table_export_skill          📊 导出
```

### 📐 配置驱动

所有参数通过 YAML 配置，零硬编码：
- 爬虫延时、代理、重试
- NLP 分词、LDA 超参、疑问关键词
- Excel 表头、列宽、样式
- 词云尺寸、字体、配色

### 🛡️ 缺失容错

每个 Skill 通过 `try/except ImportError` 导入，缺失时仅记录日志，不中断流程。

### 📦 数据中间件

`AnalysisData` dataclass 作为唯一数据载体贯穿 6 步流程：

```python
@dataclass
class AnalysisData:
    video_meta: Optional[dict] = None        # Step 1 产出
    raw_comments: Optional[list] = None       # Step 1 产出
    cleaned_comments: Optional[list] = None   # Step 3 产出
    segmented_comments: Optional[list] = None # Step 4 产出
    topics: Optional[dict] = None             # Step 4 产出
    questions: Optional[list] = None          # Step 4 产出
    cover_local_path: Optional[str] = None    # Step 2 产出
    wordcloud_path: Optional[str] = None      # Step 6 产出
    video_url: Optional[str] = None
    platform: Optional[str] = None
    status: str = "pending"
    error_msg: Optional[str] = None
    extra: dict = field(default_factory=dict) # 扩展字段
```

### 📊 Excel 输出规范

三张表遵循统一模板引擎：
- 🔵 蓝色表头 `#4472C4` + 白色粗体字
- ❄️ 首行冻结
- 🔍 自动筛选器
- 📏 自适应列宽（上限 60 字符）

---

## ⚠️ 注意事项与法律声明

> **📌 本工具仅供合法合规的数据分析与学术研究使用。使用者须自行遵守所在地法律法规及平台服务条款。**

### 使用限制

| 事项 | 说明 |
|------|------|
| ⚖️ **合规使用** | 本工具仅用于公开数据的采集与分析。**不得**用于非法爬取非公开数据、侵犯隐私、商业间谍等违法违规行为。 |
| 🛡️ **平台条款** | 使用者须遵守抖音、TikTok、Bilibili 等平台的 **服务条款** 与 **Robots 协议**。高频爬取可能导致 IP 被封禁，请合理控制请求频率。 |
| 🔐 **账号安全** | 如有 Cookie 配置需求，请使用**小号/临时账号**，不建议使用主力账号。Cookie 仅保存在本地，不会上传或泄露。 |
| 📊 **数据用途** | 所有抓取数据仅限本地存储与分析使用。**不得**将数据用于转售、批量分发、或侵犯原平台/创作者的合法权益。 |
| ⏱️ **频率控制** | 默认已内置 1.5 秒请求间隔，建议批量任务不超过 **30 条/批次**，跑完静置 **3 分钟** 后再继续。 |

### Multilingual Legal Disclaimer

> **中文 (Chinese)**
>
> 本工具仅用于合法的数据分析与学术研究目的。使用者须自行遵守适用的法律法规及第三方平台服务条款。开发者不对因使用本工具而产生的任何法律风险或责任承担责任。严禁将本工具用于爬取非公开数据、侵犯他人隐私、侵犯知识产权或任何其他违法违规活动。
>
> **English**
>
> This tool is intended solely for lawful data analysis and academic research purposes. Users are responsible for complying with all applicable laws, regulations, and third-party platform terms of service. The developer assumes no liability for any legal risks or consequences arising from the use of this tool. It is strictly prohibited to use this tool for scraping non-public data, infringing privacy or intellectual property rights, or any other illegal or unauthorized activities.
>
> **Français (French)**
>
> Cet outil est destiné uniquement à des fins légitimes d'analyse de données et de recherche académique. Les utilisateurs sont tenus de se conformer à toutes les lois et réglementations applicables ainsi qu'aux conditions d'utilisation des plateformes tierces. Le développeur décline toute responsabilité pour les risques juridiques ou les conséquences découlant de l'utilisation de cet outil. Il est strictement interdit d'utiliser cet outil pour extraire des données non publiques, porter atteinte à la vie privée ou aux droits de propriété intellectuelle, ou pour toute autre activité illégale ou non autorisée.
>
> **Русский (Russian)**
>
> Данный инструмент предназначен исключительно для законного анализа данных и академических исследований. Пользователи обязаны соблюдать все применимые законы, нормативные акты и условия обслуживания сторонних платформ. Разработчик не несет ответственности за любые юридические риски или последствия, возникающие в результате использования данного инструмента. Строго запрещается использовать данный инструмент для сбора непубличных данных, нарушения конфиденциальности или прав интеллектуальной собственности, а также для любых других незаконных или неавторизованных действий.
>
> **العربية (Arabic)**
>
> تم تصميم هذه الأداة فقط لأغراض تحليل البيانات القانونية والبحث الأكاديمي. يتحمل المستخدمون مسؤولية الامتثال لجميع القوانين واللوائح المعمول بها وشروط خدمة المنصات الخارجية. لا يتحمل المطور أي مسؤولية عن أي مخاطر قانونية أو عواقب تنشأ عن استخدام هذه الأداة. يُحظر تمامًا استخدام هذه الأداة لجمع البيانات غير العامة، أو انتهاك الخصوصية أو حقوق الملكية الفكرية، أو أي أنشطة غير قانونية أو غير مصرح بها.
>
> **Español (Spanish)**
>
> Esta herramienta está destinada únicamente a fines legítimos de análisis de datos e investigación académica. Los usuarios son responsables de cumplir con todas las leyes y regulaciones aplicables, así como con los términos de servicio de las plataformas de terceros. El desarrollador no asume ninguna responsabilidad por los riesgos legales o consecuencias derivados del uso de esta herramienta. Está estrictamente prohibido utilizar esta herramienta para extraer datos no públicos, infringir la privacidad o los derechos de propiedad intelectual, o cualquier otra actividad ilegal o no autorizada.

---

## 📄 License

MIT

```
MIT License

Copyright (c) 2026 夜秋风6

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
