"""
评论明细 Excel 表格导出模块
将清洗后的评论数据导出为格式化的 Excel 文件
"""

from typing import List, Optional

from ._excel_common import (
    load_template_config,
    load_table_format,
    setup_header_style,
    write_headers,
    apply_worksheet_formatting,
)


def export_comment_detail_table(
    comments: List[dict],
    output_path: str,
    template_path: Optional[str] = None,
) -> str:
    """
    将评论明细数据导出为 Excel 文件

    Args:
        comments: 标准化评论列表（clean_comments 返回值）
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

    comment_config = template.get("comment_detail", {})
    columns = comment_config.get("columns", [])
    fields = [col.get("field", "") for col in columns]

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = comment_config.get("sheet_name", "评论明细")

    font, fill = setup_header_style(table_format)
    write_headers(ws, columns, font, fill)

    for row_idx, comment in enumerate(comments, 2):
        for col_idx, field in enumerate(fields, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=comment.get(field, ""))
            cell.alignment = Alignment(vertical="center")

    apply_worksheet_formatting(ws, columns, len(comments), table_format)

    import os
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    wb.save(output_path)

    return os.path.abspath(output_path)