"""Пакет для работы с уведомлениями."""

from .email.models import EmailMessage, EmailAttachment
from .email.sender import EmailSender

__all__ = ["EmailMessage", "EmailAttachment", "EmailSender"]
