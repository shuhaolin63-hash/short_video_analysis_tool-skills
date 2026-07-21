"""
视频元数据 Excel 表格导出模块
将视频元数据列表导出为格式化的 Excel 文件
"""

from typing import List, Optional

from ._excel_common import (
    load_template_config,
    load_table_format,
    setup_header_style,
    write_headers,
    apply_worksheet_formatting,
)


def export_video_meta_table(
    video_meta_list: List[dict],
    output_path: str,
    template_path: Optional[str] = None,
) -> str:
    """
    将视频元数据列表导出为 Excel 文件

    Args:
        video_meta_list: 标准化视频元数据列表
        output_path: 输出 Excel 文件路径
        template_path: 模板配置文件路径，默认读取 config/table_template.yaml

    Returns:
        输出文件的绝对路径
    """
    try:
        import openpyxl
        from openpyxl.styles import Alignment
    except ImportError:
        raise ImportError("需要安装 openpyxl (pip install openpyxl)")

    template = load_template_config(template_path)
    table_format = load_table_format()

    meta_config = template.get("video_meta_info", {})
    columns = meta_config.get("columns", [])
    fields = [col.get("field", "") for col in columns]

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = meta_config.get("sheet_name", "视频基础信息")

    font, fill = setup_header_style(table_format)
    write_headers(ws, columns, font, fill)

    for row_idx, meta in enumerate(video_meta_list, 2):
        for col_idx, field in enumerate(fields, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=meta.get(field, ""))
            cell.alignment = Alignment(vertical="center")

    apply_worksheet_formatting(ws, columns, len(video_meta_list), table_format)

    import os
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    wb.save(output_path)

    return os.path.abspath(output_path)