# ============================================================
# 短视频解析工具 - 缓存清理脚本
# 清理 assets/cache_cover/、logs/、及可选 output/ 目录
# ============================================================

import sys
import os
import shutil
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def parse_args():
    parser = argparse.ArgumentParser(
        description="短视频分析工具 - 清理缓存文件",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="同时清理 output/excel_table/、output/wordcloud_img/、output/cover_export/",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅预览要删除的文件，不实际删除",
    )
    return parser.parse_args()


def get_project_root() -> str:
    """获取项目根目录"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def clean_directory(dir_path: str, dry_run: bool = False) -> int:
    """
    清空指定目录（保留目录本身和 .gitkeep 文件）

    返回: 删除的文件数
    """
    if not os.path.isdir(dir_path):
        print(f"  [跳过] 目录不存在: {dir_path}")
        return 0

    count = 0
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)

        # 保留 .gitkeep
        if item == ".gitkeep":
            continue

        if dry_run:
            print(f"  [预览] 将删除: {item_path}")
            count += 1
        else:
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.remove(item_path)
                    count += 1
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    count += 1
            except Exception as e:
                print(f"  [错误] 删除失败 {item_path}: {e}")

    return count


def main():
    args = parse_args()
    root = get_project_root()

    print("=" * 60)
    print("短视频分析工具 - 缓存清理")
    print("=" * 60)
    if args.dry_run:
        print("模式: 预览（不实际删除）")
    print()

    total_deleted = 0

    # ---- 清理缓存封面 ----
    cache_cover_dir = os.path.join(root, "assets", "cache_cover")
    print(f"[1/3] 清理缓存封面: {cache_cover_dir}")
    deleted = clean_directory(cache_cover_dir, args.dry_run)
    total_deleted += deleted
    print(f"  -> 清理了 {deleted} 个文件")
    print()

    # ---- 清理日志 ----
    logs_dir = os.path.join(root, "logs")
    print(f"[2/3] 清理日志: {logs_dir}")
    deleted = clean_directory(logs_dir, args.dry_run)
    total_deleted += deleted
    print(f"  -> 清理了 {deleted} 个文件")
    print()

    # ---- 可选清理 output ----
    if args.all:
        output_dirs = [
            ("Excel 表格", os.path.join(root, "output", "excel_table")),
            ("词云图片", os.path.join(root, "output", "wordcloud_img")),
            ("导出封面", os.path.join(root, "output", "cover_export")),
        ]
        print(f"[3/3] 清理 output 目录")
        for label, dir_path in output_dirs:
            print(f"  - {label}: {dir_path}")
            deleted = clean_directory(dir_path, args.dry_run)
            total_deleted += deleted
            print(f"    -> 清理了 {deleted} 个文件")
    else:
        print("[3/3] output 目录未清理（使用 --all 参数可清理）")

    print()
    print("=" * 60)

    if args.dry_run:
        print(f"预览完成，共 {total_deleted} 个文件将被删除")
    else:
        print(f"清理完成，共删除 {total_deleted} 个文件")
    print("=" * 60)


if __name__ == "__main__":
    main()
