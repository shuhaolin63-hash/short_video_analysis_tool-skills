"""
封面下载模块
提供异步下载视频封面图片的功能
"""

import os
import sys
import asyncio
from typing import Optional

# 将项目根目录加入 sys.path，以支持跨模块导入配置
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


async def download_cover(
    cover_url: str,
    video_id: str,
    cache_dir: Optional[str] = None,
) -> str:
    """
    异步下载视频封面图片并保存到本地缓存目录

    Args:
        cover_url: 封面图片 URL
        video_id: 视频 ID，用于生成文件名
        cache_dir: 缓存目录，默认使用全局配置中的 assets/cache_cover/

    Returns:
        本地封面图片的绝对路径

    Raises:
        ValueError: cover_url 为空时抛出
        Exception: 下载失败时抛出
    """
    if not cover_url:
        raise ValueError("cover_url 不能为空")

    if cache_dir is None:
        # 读取全局配置中的缓存封面目录
        try:
            import yaml
            config_path = os.path.join(_project_root, 'config', 'global_config.yaml')
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            cache_dir = config.get("output", {}).get("cache_cover_dir", "assets/cache_cover/")
        except Exception:
            cache_dir = "assets/cache_cover/"

    # 转换为绝对路径
    if not os.path.isabs(cache_dir):
        cache_dir = os.path.join(_project_root, cache_dir)

    os.makedirs(cache_dir, exist_ok=True)

    # 文件名: {video_id}_cover.jpg
    filename = f"{video_id}_cover.jpg"
    filepath = os.path.join(cache_dir, filename)

    # 如果文件已存在，直接返回
    if os.path.exists(filepath):
        return os.path.abspath(filepath)

    try:
        import httpx
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(cover_url)
            response.raise_for_status()
            with open(filepath, 'wb') as f:
                f.write(response.content)
    except ImportError:
        # 降级使用 aiohttp
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(cover_url, timeout=30) as response:
                    response.raise_for_status()
                    content = await response.read()
                    with open(filepath, 'wb') as f:
                        f.write(content)
        except ImportError:
            raise ImportError("需要安装 httpx 或 aiohttp 才能下载封面")

    return os.path.abspath(filepath)
