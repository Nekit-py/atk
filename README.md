# ATK (Automation Toolkit)

Инструменты для автоматизации работы с данными, отправки уведомлений, работы с базами данных и датами.

## Установка

```bash
pip install git+https://github.com/Nekit-py/atk.git@develop
```

Требуется Python 3.8+

---

## Логгирование

В начале вашего приложения инициализируйте логгирование:

```python
import atk.logger.logger  # инициализация логгирования
```

В любом модуле используйте стандартный логгер:

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Пример логирования")
```

---

## Работа с Excel

Модуль для работы с Excel файлами.

### Пример использования

```python
from atk.excel import write_single_sheet, write_multiple_sheets, SheetContent
import pandas as pd

data = pd.DataFrame({"Name": ["John", "Jane"], "Age": [30, 25]})
sheet = SheetContent("Users", data)

excel_bytes = write_single_sheet(sheet)

sheets = [
    SheetContent("Users", data),
    SheetContent("Stats", pd.DataFrame({"Total": [2]}))
]
excel_bytes = write_multiple_sheets(sheets)

with open("output.xlsx", "wb") as f:
    f.write(excel_bytes)
```

---

## Email-уведомления

Модуль для работы с email-уведомлениями.

### Пример использования

```python
from atk.notifications import EmailMessage, EmailAttachment, EmailSender

message = EmailMessage(
    to=["recipient@example.com"],
    subject="Test Subject",
    body="<p>Test Body</p>",
    cc=["cc@example.com"],
)

attachment = EmailAttachment(
    name="report.xlsx",
    data=b"file content",
)
message.attachment = attachment

sender = EmailSender(
    hostname="smtp.example.com",
    port=587,
    start_tls=False,
)
await sender.send(message)
```

---

## Работа с датами

Модуль для работы с временными периодами.

### Пример использования

```python
from atk.dates import Period
from datetime import datetime, timedelta

start = datetime(2024, 1, 1, 10, 0)
end = datetime(2024, 1, 1, 12, 0)
period = Period(start=start, end=end)

other_period = Period(
    start=datetime(2024, 1, 1, 11, 0),
    end=datetime(2024, 1, 1, 13, 0)
)
intersection = period.intersection(other_period)

sub_periods = period.split(timedelta(hours=1))
```

---

## Работа с базами данных

### Oracle

```python
from atk.db.oracle import OraclePool
import asyncio

async def main():
    await OraclePool.create_pool()
    async with OraclePool.acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT 1 FROM DUAL")
            result = await cursor.fetchone()
            print(result)
    await OraclePool.close()

asyncio.run(main())
```

### PostgreSQL

```python
from atk.db.postgres import PostgresPool
import asyncio

async def main():
    await PostgresPool.create_pool()
    async with PostgresPool.acquire() as connection:
        result = await connection.fetchrow("SELECT 1 as result")
        print(result)
    await PostgresPool.close()

asyncio.run(main())
```

---

## Разработка

### Установка зависимостей для разработки

```bash
pip install -r requirements-dev.txt
```

### Запуск тестов

```bash
pytest tests/
```

### Форматирование кода

```bash
black .
isort .
```

### Проверка типов

```bash
mypy .
```

### Проверка стиля кода

```bash
flake8 .
```

## Лицензия

MIT