"""
封面文件整理模块
将缓存目录中的封面导出到指定输出目录，支持去重
"""

import os
import sys
import shutil
from typing import List, Dict

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


def export_covers(export_dir: str = None) -> List[Dict[str, str]]:
    """
    将缓存目录中所有封面复制到导出目录

    处理逻辑:
        1. 从全局配置读取缓存封面目录和导出封面目录
        2. 扫描缓存目录中的所有封面文件（_cover.jpg 结尾）
        3. 复制到导出目录，自动去重（同名文件跳过）
        4. 返回文件清单

    Args:
        export_dir: 导出目录路径，默认使用全局配置中的 output/cover_export/

    Returns:
        封面清单列表，每个元素为:
            - video_id: 视频 ID
            - cover_path: 封面文件绝对路径
            - cover_filename: 封面文件名
    """
    try:
        import yaml
        config_path = os.path.join(_project_root, 'config', 'global_config.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception:
        config = {}

    output_cfg = config.get("output", {})
    cache_cover_dir = output_cfg.get("cache_cover_dir", "assets/cache_cover/")
    if export_dir is None:
        export_dir = output_cfg.get("cover_export_dir", "output/cover_export/")

    # 转换为绝对路径
    if not os.path.isabs(cache_cover_dir):
        cache_cover_dir = os.path.join(_project_root, cache_cover_dir)
    if not os.path.isabs(export_dir):
        export_dir = os.path.join(_project_root, export_dir)

    # 确保导出目录存在
    os.makedirs(export_dir, exist_ok=True)

    # 扫描缓存目录
    if not os.path.exists(cache_cover_dir):
        return []

    cover_list: List[Dict[str, str]] = []
    seen_filenames: set = set()

    for filename in os.listdir(cache_cover_dir):
        if not filename.endswith("_cover.jpg"):
            continue

        src_path = os.path.join(cache_cover_dir, filename)
        if not os.path.isfile(src_path):
            continue

        # 提取 video_id（去掉 _cover.jpg 后缀）
        video_id = filename.replace("_cover.jpg", "")

        # 去重处理：同名文件跳过
        if filename in seen_filenames:
            continue
        seen_filenames.add(filename)

        dst_path = os.path.join(export_dir, filename)
        try:
            shutil.copy2(src_path, dst_path)
        except shutil.SameFileError:
            pass  # 源和目标相同，忽略

        cover_list.append({
            "video_id": video_id,
            "cover_path": os.path.abspath(dst_path),
            "cover_filename": filename,
        })

    return cover_list
