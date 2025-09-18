# ATK (Automation Toolkit)

Инструменты для автоматизации работы с данными, отправки уведомлений, работы с базами данных и датами.

## Установка

### Через uv (рекомендуется)

```bash
uv pip install git+http://10.0.2.212/services/ldap_auth.git@main
```

### Через pip (альтернатива)

```bash
pip install git+http://10.0.2.212/services/ldap_auth.git
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
    # Создание пула по умолчанию с параметрами подключения (берутся из файла .env)
    await PostgresPool.create_pool(
        user="POSTGRES_USER",
        password="POSTGRES_PASSWORD", 
        host="POSTGRES_HOST",
        port="POSTGRES_PORT",
        dbname="POSTGRES_DBNAME"
    )
    
    # Работа с основным пулом
    async with PostgresPool.acquire() as connection:
        result = await connection.fetchrow("SELECT 1 as result")
        print(result)
    
    
    # Закрытие всех пулов
    await PostgresPool.close_all()

asyncio.run(main())
```

### Oracle

```python
from atk.db.oracle import OraclePool
import asyncio

async def main():
    # Создание пула по умолчанию с параметрами подключения (берутся из файла .env)
    await OraclePool.create_pool(
        user="ORACLE_USER",
        password="ORACLE_PASSWORD",
        host="ORACLE_HOST", 
        port="ORACLE_PORT",
        service_name="ORACLE_SERVICE_NAME"
    )
    
    # Работа с основным пулом
    async with OraclePool.acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT 1 FROM DUAL")
            result = await cursor.fetchone()
            print(result)
    
    # Создание дополнительного пула для отчетов
    await OraclePool.create_pool(
        user="ORACLE_USER",
        password="ORACLE_PASSWORD",
        host="ORACLE_HOST",
        port="ORACLE_PORT",
        service_name="ORACLE_SERVICE_NAME",
        pool_name="reports",
        min_size=2,
        max_size=8
    )
    
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

### Использование переменных окружения

Вместо явного указания параметров подключения можно использовать переменные окружения:

```python
# Для PostgreSQL
import os
os.environ.update({
    "POSTGRES_USER": "myuser",
    "POSTGRES_PASSWORD": "mypassword",
    "POSTGRES_HOST": "localhost",
    "POSTGRES_PORT": "5432",
    "POSTGRES_DBNAME": "mydb"
})

# Для Oracle
os.environ.update({
    "ORACLE_USER": "myuser",
    "ORACLE_PASSWORD": "mypassword", 
    "ORACLE_HOST": "localhost",
    "ORACLE_PORT": "1521",
    "ORACLE_SERVICE_NAME": "ORCL"
})
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

### Установка зависимостей (uv)

```bash
uv venv
uv sync --dev
```

### Запуск тестов

```bash
uv run pytest tests/
```

### Форматирование кода

```bash
uv run black .
uv run isort .
```

### Линтинг

```bash
uv run ruff check .
```

### Проверка типов

```bash
uv run mypy .
```

## Лицензия

MIT