# ============================================================
# 短视频解析工具 - 单视频分析命令行入口
# 用法: python scripts/run_single_analyze.py --url <视频链接>
# ============================================================

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.single_video_agent import SingleVideoAgent


def parse_args():
    parser = argparse.ArgumentParser(
        description="短视频分析工具 - 单视频分析",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/run_single_analyze.py --url "https://www.douyin.com/video/xxxxx"
  python scripts/run_single_analyze.py --url "https://www.tiktok.com/@user/video/xxxxx"
        """,
    )
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="视频链接（抖音 / TikTok / B站）",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("=" * 60)
    print("短视频分析工具 - 单视频分析")
    print("=" * 60)
    print(f"视频链接: {args.url}")
    print()

    # 创建 Agent 并运行
    agent = SingleVideoAgent()
    result = agent.run(args.url)

    # ---- 打印结果摘要 ----
    print()
    print("=" * 60)
    print("分析结果摘要")
    print("=" * 60)

    if result.status == "error":
        print(f"状态:   失败")
        print(f"错误:   {result.error_msg}")
        sys.exit(1)

    meta = result.video_meta or {}
    video_id = meta.get("video_id", "N/A")
    title = meta.get("title_text", meta.get("title", "N/A"))
    author = meta.get("author_name", meta.get("author", "N/A"))
    publish_time = meta.get("publish_time", "N/A")
    play_count = meta.get("play_count", "N/A")
    like_count = meta.get("like_count", "N/A")
    comment_total = meta.get("comment_total", meta.get("comment_count", "N/A"))
    collect_count = meta.get("collect_count", "N/A")
    share_count = meta.get("share_count", "N/A")

    print(f"视频ID:      {video_id}")
    print(f"标题:        {title}")
    print(f"作者:        {author}")
    print(f"发布时间:    {publish_time}")
    print(f"播放量:      {play_count}")
    print(f"点赞数:      {like_count}")
    print(f"评论数:      {comment_total}")
    print(f"收藏数:      {collect_count}")
    print(f"转发数:      {share_count}")

    comment_count = len(result.cleaned_comments or [])
    topic_count = len(result.topics or {})
    question_count = len(result.questions or [])

    print()
    print(f"清洗后评论数:    {comment_count}")
    print(f"聚类话题数:      {topic_count}")
    print(f"提取疑问评论数:  {question_count}")

    # 输出文件路径
    print()
    print("输出文件:")

    excel_paths = result.extra.get("excel_paths", {})
    if excel_paths:
        for name, path in excel_paths.items():
            print(f"  - {name}: {path}")
    else:
        print("  （Excel 表格未生成）")

    if result.cover_local_path:
        print(f"  封面路径: {result.cover_local_path}")

    if result.wordcloud_path:
        print(f"  词云路径: {result.wordcloud_path}")

    print()
    print("=" * 60)
    print("分析完成!")


if __name__ == "__main__":
    main()
