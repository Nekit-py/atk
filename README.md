# ATK (Automation Toolkit)

Инструменты для автоматизации работы с данными, отправки уведомлений, работы с базами данных и датами.

## Установка

```bash
pip install git+http://10.0.2.191:8888/project/sidorovich_ns/atk.git@develop
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

Поддерживает работу с множественными пулами соединений для подключения к разным базам данных.

### PostgreSQL

```python
from atk.db.postgres import PostgresPool
import asyncio

async def main():
    # Создание пула по умолчанию
    await PostgresPool.create_pool()
    
    # Работа с основным пулом
    async with PostgresPool.acquire() as connection:
        result = await connection.fetchrow("SELECT 1 as result")
        print(result)
    
    # Создание дополнительного пула для аналитики
    await PostgresPool.create_pool("analytics", min_size=3, max_size=10)
    
    # Работа с пулом аналитики
    async with PostgresPool.acquire("analytics") as connection:
        result = await connection.fetchrow("SELECT COUNT(*) FROM reports")
        print(result)
    
    # Закрытие конкретного пула
    await PostgresPool.close("analytics")
    
    # Закрытие всех пулов
    await PostgresPool.close_all()

asyncio.run(main())
```

### Oracle

```python
from atk.db.oracle import OraclePool
import asyncio

async def main():
    # Создание пула по умолчанию
    await OraclePool.create_pool()
    
    # Работа с основным пулом
    async with OraclePool.acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT 1 FROM DUAL")
            result = await cursor.fetchone()
            print(result)
    
    # Создание дополнительного пула для отчетов
    await OraclePool.create_pool("reports", min_size=2, max_size=8)
    
    # Работа с пулом отчетов
    async with OraclePool.acquire("reports") as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT COUNT(*) FROM reports")
            result = await cursor.fetchone()
            print(result)
    
    # Закрытие конкретного пула
    await OraclePool.close("reports")
    
    # Закрытие всех пулов
    await OraclePool.close_all()

asyncio.run(main())
```

### Переменные окружения

Для PostgreSQL:
- `POSTGRES_USER` - имя пользователя
- `POSTGRES_PASSWORD` - пароль
- `POSTGRES_HOST` - хост
- `POSTGRES_PORT` - порт
- `POSTGRES_DBNAME` - имя базы данных

Для Oracle:
- `ORACLE_USER` - имя пользователя
- `ORACLE_PASSWORD` - пароль
- `ORACLE_HOST` - хост
- `ORACLE_PORT` - порт
- `ORACLE_SERVICE_NAME` - имя сервиса

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