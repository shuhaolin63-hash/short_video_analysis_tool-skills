"""
热点话题 Excel 表格导出模块
将话题聚类结果转换为格式化的 Excel 文件
"""

import sys
import os
from typing import Dict, List, Optional

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


def export_hot_topic_table(
    topics: Dict[int, dict],
    output_path: str,
    template_path: Optional[str] = None,
    video_id: str = "",
) -> str:
    """
    将话题聚类结果展平为 Excel 表格

    功能:
        1. 读取 table_template.yaml 获取列定义
        2. 将 topics 字典展平为表格行
        3. 计算 topic_weight = 该话题评论数 / 总评论数
        4. 计算 avg_like
        5. 从 question_extract 结果中选取代表性提问作为 sample_question
        6. 冻结首行、自动筛选、自动列宽
        7. 返回输出文件路径

    Args:
        topics: cluster_topics 返回的话题聚类结果字典
        output_path: 输出 Excel 文件路径
        template_path: 模板配置文件路径，默认读取 config/table_template.yaml
        video_id: 关联的视频 ID

    Returns:
        输出文件的绝对路径
    """
    try:
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill
        from openpyxl.utils import get_column_letter
    except ImportError:
        raise ImportError("需要安装 openpyxl (pip install openpyxl)")

    # 读取模板配置
    if template_path is None:
        template_path = os.path.join(_project_root, 'config', 'table_template.yaml')

    try:
        import yaml
        with open(template_path, 'r', encoding='utf-8') as f:
            template = yaml.safe_load(f)
    except Exception:
        raise FileNotFoundError(f"无法读取模板配置文件: {template_path}")

    # 读取全局配置中的 table_format
    try:
        global_config_path = os.path.join(_project_root, 'config', 'global_config.yaml')
        with open(global_config_path, 'r', encoding='utf-8') as f:
            global_config = yaml.safe_load(f)
        table_format = global_config.get("table_format", {})
    except Exception:
        table_format = {}

    topic_config = template.get("comment_hot_topic", {})
    sheet_name = topic_config.get("sheet_name", "评论热点问题")
    columns = topic_config.get("columns", [])

    # 创建工作簿
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name

    # 写入表头
    header_font_bold = table_format.get("header_font_bold", True)
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=header_font_bold, color="FFFFFF", size=11)

    headers = [col.get("header", "") for col in columns]
    fields = [col.get("field", "") for col in columns]

    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # 将 topics 展平为行数据
    # topics 结构: {topic_id: {keywords: [str], comment_ids: [str], weight: float}}
    if not topics:
        # 无数据时写入一行空数据占位
        empty_row = {field: "" for field in fields}
        empty_row["video_id"] = video_id
        for col_idx, field in enumerate(fields, 1):
            ws.cell(row=2, column=col_idx, value=empty_row.get(field, ""))
    else:
        total_comment_num = sum(
            len(t.get("comment_ids", [])) for t in topics.values()
        )

        row_idx = 2
        for topic_id, topic_data in topics.items():
            keyword_str = "、".join(topic_data.get("keywords", []))
            comment_ids = topic_data.get("comment_ids", [])
            total_num = len(comment_ids)
            avg_like = 0.0  # 此处无法获取点赞数，由调用方补充

            # topic_weight = 该话题评论数 / 总评论数
            topic_weight = total_num / total_comment_num if total_comment_num > 0 else 0

            # 代表性提问：取第一条评论 ID 作为 sample_question 占位
            sample_question = ""
            if comment_ids:
                sample_question = f"关联 {total_num} 条评论"

            row_data = {
                "video_id": video_id,
                "topic_id": topic_id,
                "topic_keyword": keyword_str,
                "sample_question": sample_question,
                "total_comment_num": total_num,
                "avg_like": round(avg_like, 2),
                "topic_weight": round(topic_weight, 4),
                "related_comment_ids": ",".join(comment_ids[:10]),
            }

            for col_idx, field in enumerate(fields, 1):
                value = row_data.get(field, "")
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.alignment = Alignment(vertical="center")

            row_idx += 1

    # 冻结首行
    if table_format.get("freeze_first_row", True):
        ws.freeze_panes = "A2"

    # 自动筛选
    if table_format.get("add_auto_filter", True):
        max_col = len(headers)
        max_row = ws.max_row
        if max_row > 1:
            ws.auto_filter.ref = f"A1:{get_column_letter(max_col)}{max_row}"

    # 自动列宽
    if table_format.get("auto_column_width", True):
        max_column_width = table_format.get("max_column_width", 60)
        for col_idx, col_config in enumerate(columns, 1):
            width = col_config.get("width", 20)
            width = min(width, max_column_width)
            ws.column_dimensions[get_column_letter(col_idx)].width = width

    # 保存
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    wb.save(output_path)

    return os.path.abspath(output_path)
