# Excel Writer

Инструменты для автоматизации

## Установка

```bash
pip install atk
```

## Использование

### Запись одного листа

```python
import pandas as pd
from atk import SheetContent, write_single_sheet

# Создаем DataFrame
df = pd.DataFrame({
    'Имя': ['Иван', 'Петр', 'Мария'],
    'Возраст': [25, 30, 28]
})

# Создаем объект SheetContent
sheet = SheetContent("Сотрудники", df)

# Записываем в Excel и получаем байты
excel_bytes = write_single_sheet(sheet)

# Сохраняем в файл
with open('сотрудники.xlsx', 'wb') as f:
    f.write(excel_bytes)
```

### Запись нескольких листов

```python
import pandas as pd
from atk import SheetContent, write_multiple_sheets

# Создаем несколько DataFrame
df1 = pd.DataFrame({'A': [1, 2, 3]})
df2 = pd.DataFrame({'B': [4, 5, 6]})

# Создаем список SheetContent
sheets = [
    SheetContent("Лист1", df1),
    SheetContent("Лист2", df2)
]

# Записываем в Excel и получаем байты
excel_bytes = write_multiple_sheets(sheets)

# Сохраняем в файл
with open('много_листов.xlsx', 'wb') as f:
    f.write(excel_bytes)
```

## Особенности

- Автоматическая настройка ширины столбцов
- Поддержка множества листов
- Возвращает данные в виде байтов для гибкого использования
- Типизация для лучшей поддержки IDE

## Требования

- Python >= 3.7
- pandas >= 1.3.0
- openpyxl >= 3.0.0 