"""Пакет для работы с уведомлениями."""

from .email.models import EmailAttachment, EmailMessage
from .email.sender import EmailSender

__all__ = ["EmailMessage", "EmailAttachment", "EmailSender"]
