from io import BytesIO
import pandas as pd
from typing import List

from .models import SheetContent
from .formatting import set_column_widths


def write_single_sheet(sheet_content: SheetContent) -> bytes:
    """Записывает один лист в Excel и возвращает его в виде байтов.

    Аргументы:
        sheet_content: Объект SheetContent, содержащий название листа и данные

    Возвращает:
        bytes: Содержимое Excel файла в виде байтов

    Выбрасывает:
        ValueError: Если sheet_content некорректен
    """
    if not isinstance(sheet_content, SheetContent):
        raise ValueError("sheet_content должен быть экземпляром SheetContent")

    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer) as writer:
            sheet_name, data = sheet_content
            data.to_excel(writer, sheet_name=sheet_name, index=False)
            set_column_widths(writer, sheet_name, data)
        return buffer.getvalue()


def write_multiple_sheets(contents: List[SheetContent]) -> bytes:
    """Записывает несколько листов в Excel и возвращает файл в виде байтов.

    Аргументы:
        contents: Список объектов SheetContent

    Возвращает:
        bytes: Содержимое Excel файла в виде байтов

    Выбрасывает:
        ValueError: Если список contents пуст или содержит некорректные элементы
    """
    if not contents:
        raise ValueError("список contents не может быть пустым")

    if not all(isinstance(content, SheetContent) for content in contents):
        raise ValueError(
            "Все элементы в contents должны быть экземплярами SheetContent"
        )

    with BytesIO() as buffer:
        with pd.ExcelWriter(path=buffer, engine="openpyxl") as writer:
            for sheet_content in contents:
                sheet_name, data = sheet_content
                data.to_excel(writer, sheet_name=sheet_name, index=False)
                set_column_widths(writer, sheet_name, data)
        return buffer.getvalue()
