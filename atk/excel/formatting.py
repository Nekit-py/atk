from typing import Any

import pandas as pd
from openpyxl.utils.cell import get_column_letter


def set_column_widths(
    writer: Any, sheet_name: str, data: pd.DataFrame, padding: int = 5
) -> None:
    """Устанавливает ширину столбцов для заданного DataFrame в Excel.

    Аргументы:
        writer: Объект Excel writer
        sheet_name: Название листа для модификации
        data: DataFrame с данными
        padding: Дополнительный отступ для ширины столбца (по умолчанию: 5)
    """
    for i, col in enumerate(data.columns):
        column_len = data[col].astype(str).apply(len).max()
        column_len = max(column_len, len(col)) + padding
        writer.sheets[sheet_name].column_dimensions[
            get_column_letter(i + 1)
        ].width = column_len
