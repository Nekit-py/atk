from dataclasses import dataclass
from typing import Optional, Union
import re
from pydantic import EmailStr, BaseModel, Field


@dataclass(slots=True, frozen=True)
class Attachment:
    """Вложение для сообщения.

    Атрибуты:
        data: Байтовые данные вложения
        name: Имя файла вложения
    """

    data: bytes
    name: str

    def __post_init__(self) -> None:
        """Проверяет корректность данных вложения."""
        if not self.data:
            raise ValueError("Данные вложения не могут быть пустыми")
        if not self.name:
            raise ValueError("Имя вложения не может быть пустым")
        if not re.match(r"^[\w\-\.]+$", self.name):
            raise ValueError("Имя вложения содержит недопустимые символы")

    def size(self) -> int:
        """Возвращает размер вложения в байтах."""
        return len(self.data)

    def __repr__(self) -> str:
        return f"Attachment(name={self.name}, size={self.size()})"


class Message(BaseModel):
    """Сообщение для отправки.

    Атрибуты:
        to: Адрес получателя или список получателей
        subject: Тема сообщения
        body: Текст сообщения
        cc: Адреса получателей копии (один или несколько)
        attachment: Вложение
    """

    to: Union[EmailStr, list[EmailStr]]
    subject: str = Field(
        min_length=1, description="Тема сообщения не может быть пустой"
    )
    body: str = Field(min_length=1, description="Текст сообщения не может быть пустым")
    cc: Optional[Union[EmailStr, list[EmailStr]]] = None
    attachment: Optional[Attachment] = None

    def format_recipients(self) -> str:
        """Форматирует список получателей для отправки."""
        recipients = [self.to] if isinstance(self.to, EmailStr) else self.to

        if self.cc:
            if isinstance(self.cc, EmailStr):
                recipients.append(self.cc)
            else:
                recipients.extend(self.cc)

        return ", ".join(str(recipient) for recipient in recipients)

    def has_attachments(self) -> bool:
        """Проверяет наличие вложений."""
        return self.attachment is not None

    def get_attachment_size(self) -> int:
        """Возвращает размер вложения в байтах."""
        if not self.attachment:
            return 0
        return self.attachment.size()
