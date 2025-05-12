# ATK (Automation Toolkit)

Инструменты для автоматизации работы с данными и отправки уведомлений.

## Установка

```bash
pip install git+http://10.0.2.191:8888/project/sidorovich_ns/atk.git@develop
```

## Модули

### Excel

Модуль для работы с Excel файлами.

#### Пример использования

```python
from excel import write_single_sheet, write_multiple_sheets, SheetContent
import pandas as pd

# Создание данных
data = pd.DataFrame({
    "Name": ["John", "Jane"],
    "Age": [30, 25]
})

# Создание содержимого листа
sheet = SheetContent("Users", data)

# Запись одного листа
excel_bytes = write_single_sheet(sheet)

# Запись нескольких листов
sheets = [
    SheetContent("Users", data),
    SheetContent("Stats", pd.DataFrame({"Total": [2]}))
]
excel_bytes = write_multiple_sheets(sheets)

# Сохранение в файл
with open("output.xlsx", "wb") as f:
    f.write(excel_bytes)
```

#### Функции

##### write_single_sheet

Функция для записи одного листа в Excel.

Аргументы:
- `sheet_content`: Объект SheetContent, содержащий название листа и данные

Возвращает:
- `bytes`: Содержимое Excel файла в виде байтов

Выбрасывает:
- `ValueError`: Если sheet_content некорректен

##### write_multiple_sheets

Функция для записи нескольких листов в Excel.

Аргументы:
- `contents`: Список объектов SheetContent

Возвращает:
- `bytes`: Содержимое Excel файла в виде байтов

Выбрасывает:
- `ValueError`: Если список contents пуст или содержит некорректные элементы

#### Классы

##### SheetContent

Класс для хранения данных листа.

Атрибуты:
- `sheet_name`: Имя листа
- `data`: Данные для записи (pandas DataFrame)

##### ExcelFormatting

Класс для форматирования Excel файлов.

Методы:
- `apply_formatting(worksheet)`: Применяет форматирование к листу

### Notifications

Модуль для работы с email-уведомлениями.

#### Пример использования

```python
from notifications import EmailMessage, EmailAttachment, EmailSender

# Создание сообщения
message = EmailMessage(
    to=["recipient@example.com"],
    subject="Test Subject",
    body="<p>Test Body</p>",
    cc=["cc@example.com"],
)

# Добавление вложения
attachment = EmailAttachment(
    name="report.xlsx",
    data=b"file content",
)
message.attachment = attachment

# Отправка сообщения
sender = EmailSender(
    hostname="smtp.example.com",
    port=587,
    username="user@example.com",
    password="password",
    use_tls=True,
)
await sender.send(message)
```

#### Классы

##### EmailMessage

Класс для создания email-сообщений.

Атрибуты:
- `to`: Адрес получателя или список получателей
- `subject`: Тема сообщения
- `body`: Текст сообщения
- `cc`: Адреса получателей копии (опционально)
- `attachment`: Вложение (опционально)

Методы:
- `format_recipients()`: Форматирует список получателей для отправки
- `has_attachments()`: Проверяет наличие вложений
- `get_attachment_size()`: Возвращает размер вложения в байтах

##### EmailAttachment

Класс для работы с вложениями.

Атрибуты:
- `data`: Байтовые данные вложения
- `name`: Имя файла вложения

Методы:
- `size()`: Возвращает размер вложения в байтах

##### EmailSender

Класс для отправки email-сообщений.

Атрибуты:
- `hostname`: SMTP сервер
- `port`: Порт SMTP сервера
- `username`: Имя пользователя для аутентификации
- `password`: Пароль для аутентификации
- `use_tls`: Использовать ли TLS
- `from_email`: Email адрес отправителя

Методы:
- `send(message)`: Асинхронный метод для отправки сообщения

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