"""Модуль для отправки email сообщений."""

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import aiosmtplib

from .models import EmailMessage
from common import retry


class EmailSender:
    """Класс для отправки email сообщений.

    Атрибуты:
        hostname: SMTP сервер
        port: Порт SMTP сервера
        username: Имя пользователя для аутентификации
        password: Пароль для аутентификации
        use_tls: Использовать ли TLS
        from_email: Email адрес отправителя
    """

    def __init__(
        self,
        hostname: str = "10.0.100.10",
        port: int = 25,
        start_tls: bool = False,
        from_email: str = "exhorter@akcept.ru",
    ) -> None:
        """Инициализирует отправителя.

        Аргументы:
            hostname: SMTP сервер
            port: Порт SMTP сервера
            username: Имя пользователя для аутентификации
            password: Пароль для аутентификации
            use_tls: Использовать ли TLS
            from_email: Email адрес отправителя
        """
        self.hostname = hostname
        self.port = port
        self.from_email = from_email
        self.start_tls = start_tls

    @retry(max_attempts=4, delay=20.0, backoff=3.0)
    async def send(self, message: EmailMessage) -> None:
        """Отправляет email сообщение.

        Аргументы:
            message: Сообщение для отправки
        """
        msg = MIMEMultipart()
        msg["From"] = self.from_email
        msg["To"] = message.format_recipients()
        msg["Subject"] = message.subject

        # Добавляем тело сообщения
        msg.attach(MIMEText(message.body, "html"))

        # Добавляем вложение, если есть
        if message.attachment is not None:
            part = MIMEBase(
                "application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            part.set_payload(message.attachment.data)
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={message.attachment.name}",
            )
            msg.attach(part)

        # Отправляем сообщение
        async with aiosmtplib.SMTP(
            hostname=self.hostname,
            port=self.port,
            start_tls=self.start_tls,
        ) as server:
            recipients = message.format_recipients().split(", ")
            await server.sendmail(self.from_email, recipients, msg.as_string())
