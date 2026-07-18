# ============================================================
# 短视频解析工具 - 批量视频分析 Agent
# 依次处理多个 URL，带延时，打印进度条
# ============================================================

import sys
import os
import time
import logging
from datetime import datetime
from typing import List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.data_flow_agent import AnalysisData
from agents.single_video_agent import SingleVideoAgent

# ---- 日志器初始化 ----
_logger = logging.getLogger("BatchVideoAgent")
_logger.setLevel(logging.INFO)

# 避免重复添加 handler
if not _logger.handlers:
    _log_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs"
    )
    os.makedirs(_log_dir, exist_ok=True)

    _fh = logging.FileHandler(
        os.path.join(_log_dir, f"batch_agent_{datetime.now().strftime('%Y%m%d')}.log"),
        encoding="utf-8"
    )
    _fh.setLevel(logging.INFO)
    _fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    _logger.addHandler(_fh)

    _ch = logging.StreamHandler()
    _ch.setLevel(logging.INFO)
    _ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    _logger.addHandler(_ch)


class BatchVideoAgent:
    """批量视频分析 Agent —— 依次处理多个视频链接"""

    def __init__(
        self,
        request_delay: float = 1.5,
        stop_on_error: bool = False,
        single_agent: Optional[SingleVideoAgent] = None,
    ):
        """
        参数:
            request_delay: 每个视频之间的处理间隔（秒），避免触发反爬
            stop_on_error: 遇到错误时是否停止后续处理
            single_agent: 可复用已有的 SingleVideoAgent 实例
        """
        self.request_delay = request_delay
        self.stop_on_error = stop_on_error
        self.single_agent = single_agent or SingleVideoAgent()
        self.logger = _logger

    def run(self, urls: List[str]) -> List[AnalysisData]:
        """
        依次处理多个视频链接

        参数:
            urls: 视频链接列表

        返回:
            List[AnalysisData]: 每个视频的分析结果
        """
        total = len(urls)
        self.logger.info(f"===== 批量分析启动，共 {total} 个视频 =====")

        results: List[AnalysisData] = []
        start_time = time.time()

        for idx, url in enumerate(urls, start=1):
            url = url.strip()
            if not url:
                continue

            self._print_progress(idx, total, url)

            try:
                data = self.single_agent.run(url)
                results.append(data)

                # 打印当前结果简况
                self._print_result_summary(data, idx)

                if data.status == "error" and self.stop_on_error:
                    self.logger.error(f"遇到错误且 stop_on_error=True，停止批量处理")
                    break

            except Exception as e:
                self.logger.error(f"[{idx}/{total}] 处理异常: {url} — {e}")
                err_data = AnalysisData(
                    video_url=url,
                    status="error",
                    error_msg=str(e)
                )
                results.append(err_data)

                if self.stop_on_error:
                    break

            # 最后一个视频之后不需要延时
            if idx < total:
                self.logger.info(f"  等待 {self.request_delay}s 后处理下一个视频...")
                time.sleep(self.request_delay)

        elapsed = time.time() - start_time
        success_count = sum(1 for r in results if r.status == "done")
        error_count = sum(1 for r in results if r.status == "error")

        self.logger.info(
            f"===== 批量分析完成 — 总计: {total}, "
            f"成功: {success_count}, 失败: {error_count}, "
            f"耗时: {elapsed:.1f}s ====="
        )

        return results

    def _print_progress(self, idx: int, total: int, url: str):
        """打印进度信息"""
        bar_len = 30
        filled = int(bar_len * idx / total)
        bar = "=" * filled + "-" * (bar_len - filled)
        self.logger.info(f"[{idx}/{total}] [{bar}] 处理中...")
        self.logger.info(f"  URL: {url}")

    def _print_result_summary(self, data: AnalysisData, idx: int):
        """打印单个视频的分析结果摘要"""
        if data.status == "error":
            self.logger.info(f"  [{idx}] 状态: 错误 — {data.error_msg}")
            return

        meta = data.video_meta or {}
        video_id = meta.get("video_id", "N/A")
        title = meta.get("title_text", meta.get("title", "N/A"))
        play_count = meta.get("play_count", "N/A")
        comment_count = len(data.cleaned_comments or [])
        topic_count = len(data.topics or {})

        self.logger.info(
            f"  [{idx}] 状态: 完成\n"
            f"    视频ID:   {video_id}\n"
            f"    标题:     {title[:50] if isinstance(title, str) else title}\n"
            f"    播放量:   {play_count}\n"
            f"    评论数:   {comment_count}\n"
            f"    话题数:   {topic_count}"
        )

        if data.extra.get("excel_paths"):
            self.logger.info(f"    输出文件: {data.extra['excel_paths']}")
