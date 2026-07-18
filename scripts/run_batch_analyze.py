# ============================================================
# 短视频解析工具 - 批量视频分析命令行入口
# 用法:
#   python scripts/run_batch_analyze.py --file urls.txt
#   python scripts/run_batch_analyze.py --urls "url1,url2,url3"
# ============================================================

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.batch_video_agent import BatchVideoAgent


def parse_args():
    parser = argparse.ArgumentParser(
        description="短视频分析工具 - 批量视频分析",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/run_batch_analyze.py --file urls.txt
  python scripts/run_batch_analyze.py --urls "https://douyin.com/video/1,https://douyin.com/video/2"
  python scripts/run_batch_analyze.py --file urls.txt --delay 3.0 --stop-on-error
        """,
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="URL 列表文件，每行一个视频链接",
    )
    parser.add_argument(
        "--urls",
        type=str,
        default=None,
        help="逗号分隔的视频链接列表",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        help="每个视频之间的处理间隔（秒），默认 1.5",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="遇到错误时停止后续处理",
    )
    return parser.parse_args()


def load_urls_from_file(file_path: str) -> list:
    """从文件中读取 URL 列表（每行一个）"""
    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        print(f"[错误] 文件不存在: {abs_path}")
        sys.exit(1)

    urls = []
    with open(abs_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls


def main():
    args = parse_args()

    # ---- 收集 URL ----
    urls = []
    if args.file:
        urls = load_urls_from_file(args.file)
        print(f"从文件加载了 {len(urls)} 个 URL: {args.file}")
    elif args.urls:
        urls = [u.strip() for u in args.urls.split(",") if u.strip()]
        print(f"从命令行参数加载了 {len(urls)} 个 URL")
    else:
        print("[错误] 请提供 --file 或 --urls 参数")
        print("用法: python scripts/run_batch_analyze.py --file urls.txt")
        sys.exit(1)

    if not urls:
        print("[错误] 未找到有效的 URL")
        sys.exit(1)

    print()
    print("=" * 60)
    print("短视频分析工具 - 批量视频分析")
    print("=" * 60)
    print(f"总数:        {len(urls)}")
    print(f"请求间隔:    {args.delay}s")
    print(f"遇错停止:    {'是' if args.stop_on_error else '否'}")
    print()

    # 打印前几个 URL
    for i, url in enumerate(urls[:5], start=1):
        print(f"  [{i}] {url}")
    if len(urls) > 5:
        print(f"  ... 共 {len(urls)} 个")
    print()

    # ---- 创建 Agent 并运行 ----
    agent = BatchVideoAgent(
        request_delay=args.delay,
        stop_on_error=args.stop_on_error,
    )
    results = agent.run(urls)

    # ---- 批量结果汇总 ----
    print()
    print("=" * 60)
    print("批量分析汇总")
    print("=" * 60)

    success_count = sum(1 for r in results if r.status == "done")
    error_count = sum(1 for r in results if r.status == "error")

    print(f"总处理数:  {len(results)}")
    print(f"成功:      {success_count}")
    print(f"失败:      {error_count}")
    print()

    if error_count > 0:
        print("失败详情:")
        for i, r in enumerate(results, start=1):
            if r.status == "error":
                print(f"  [{i}] {r.video_url} -> {r.error_msg}")
        print()

    print("=" * 60)
    print("批量分析完成!")


if __name__ == "__main__":
    main()
