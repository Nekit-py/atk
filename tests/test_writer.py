import pandas as pd
import pytest
from atk import SheetContent, write_single_sheet, write_multiple_sheets


def test_write_single_sheet():
    # Создаем тестовые данные
    df = pd.DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"]})
    sheet = SheetContent("Test", df)

    # Записываем в Excel
    excel_bytes = write_single_sheet(sheet)

    # Проверяем, что получили непустые байты
    assert len(excel_bytes) > 0


def test_write_multiple_sheets():
    # Создаем тестовые данные
    df1 = pd.DataFrame({"A": [1, 2, 3]})
    df2 = pd.DataFrame({"B": [4, 5, 6]})
    sheets = [SheetContent("Sheet1", df1), SheetContent("Sheet2", df2)]

    # Записываем в Excel
    excel_bytes = write_multiple_sheets(sheets)

    # Проверяем, что получили непустые байты
    assert len(excel_bytes) > 0


def test_invalid_sheet_content():
    # Проверяем обработку некорректных данных
    with pytest.raises(ValueError):
        write_single_sheet("invalid")


def test_empty_sheets_list():
    # Проверяем обработку пустого списка
    with pytest.raises(ValueError):
        write_multiple_sheets([])
