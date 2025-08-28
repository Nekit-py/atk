from typing import NamedTuple

import pandas as pd


class SheetContent(NamedTuple):
    """Представляет содержимое одного листа Excel.

    Атрибуты:
        sheet_name: Название листа
        data: DataFrame с данными листа
    """

    sheet_name: str
    data: pd.DataFrame

    def __post_init__(self) -> None:
        """Проверяет корректность данных после инициализации."""
        if not isinstance(self.sheet_name, str):
            raise ValueError("sheet_name должен быть строкой")
        if not isinstance(self.data, pd.DataFrame):
            raise ValueError("data должен быть DataFrame")
