"""
视频元数据 Excel 表格导出模块
将视频元数据列表导出为格式化的 Excel 文件
"""

import sys
import os
from typing import List, Optional

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


def export_video_meta_table(
    video_meta_list: List[dict],
    output_path: str,
    template_path: Optional[str] = None,
) -> str:
    """
    将视频元数据列表导出为 Excel 文件

    功能:
        1. 读取 table_template.yaml 获取列定义
        2. 创建 Excel 工作簿，按列定义写入数据
        3. 冻结首行、自动筛选、自动列宽
        4. 返回输出文件路径

    Args:
        video_meta_list: 标准化视频元数据列表
        output_path: 输出 Excel 文件路径
        template_path: 模板配置文件路径，默认读取 config/table_template.yaml

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

    meta_config = template.get("video_meta_info", {})
    sheet_name = meta_config.get("sheet_name", "视频基础信息")
    columns = meta_config.get("columns", [])

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

    # 写入数据
    for row_idx, meta in enumerate(video_meta_list, 2):
        for col_idx, field in enumerate(fields, 1):
            value = meta.get(field, "")
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.alignment = Alignment(vertical="center")

    # 冻结首行
    if table_format.get("freeze_first_row", True):
        ws.freeze_panes = "A2"

    # 自动筛选
    if table_format.get("add_auto_filter", True):
        max_col = len(headers)
        max_row = len(video_meta_list) + 1
        if max_row > 1:
            ws.auto_filter.ref = f"A1:{get_column_letter(max_col)}{max_row}"

    # 自动列宽
    if table_format.get("auto_column_width", True):
        max_column_width = table_format.get("max_column_width", 60)
        for col_idx, col_config in enumerate(columns, 1):
            width = col_config.get("width", 20)
            # 限制最大宽度
            width = min(width, max_column_width)
            ws.column_dimensions[get_column_letter(col_idx)].width = width

    # 保存
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    wb.save(output_path)

    return os.path.abspath(output_path)
