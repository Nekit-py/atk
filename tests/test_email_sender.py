"""Тесты для модуля отправки email."""

import pytest
from unittest.mock import AsyncMock, patch

from atk.notifications.email.sender import EmailSender
from atk.notifications import EmailMessage, EmailAttachment


@pytest.fixture
def email_sender():
    """Фикстура для создания отправителя."""
    return EmailSender(
        hostname="test.smtp.com",
        port=587,
        start_tls=False,
    )


@pytest.fixture
def email_message():
    """Фикстура для создания тестового сообщения."""
    return EmailMessage(
        to=["recipient@example.com"],
        subject="Test Subject",
        body="<p>Test Body</p>",
    )


@pytest.fixture
def email_message_with_attachment():
    """Фикстура для создания сообщения с вложением."""
    attachment = EmailAttachment(
        name="test.xlsx",
        data=b"test data",
    )
    return EmailMessage(
        to=["recipient@example.com"],
        subject="Test Subject",
        body="<p>Test Body</p>",
        attachment=attachment,
    )


@pytest.mark.asyncio
async def test_send_email(email_sender, email_message):
    """Тест отправки простого email."""
    mock_smtp = AsyncMock()
    mock_smtp.sendmail = AsyncMock(return_value={})
    mock_smtp.__aenter__.return_value = mock_smtp

    with patch("aiosmtplib.SMTP", return_value=mock_smtp):
        await email_sender.send(email_message)

        # Проверяем, что SMTP был создан с правильными параметрами
        mock_smtp.__aenter__.assert_called_once()
        mock_smtp.__aexit__.assert_called_once()

        # Проверяем, что sendmail был вызван с правильными параметрами
        mock_smtp.sendmail.assert_called_once()
        args = mock_smtp.sendmail.call_args[0]
        assert args[0] == email_sender.from_email
        assert args[1] == email_message.to

        # Проверяем содержимое сообщения
        msg = args[2]
        assert isinstance(msg, str)
        assert f"Subject: {email_message.subject}" in msg
        assert email_message.body in msg


@pytest.mark.asyncio
async def test_send_email_with_attachment(email_sender, email_message_with_attachment):
    """Тест отправки email с вложением."""
    mock_smtp = AsyncMock()
    mock_smtp.sendmail = AsyncMock(return_value={})
    mock_smtp.__aenter__.return_value = mock_smtp

    with patch("aiosmtplib.SMTP", return_value=mock_smtp):
        await email_sender.send(email_message_with_attachment)

        # Проверяем, что sendmail был вызван
        mock_smtp.sendmail.assert_called_once()
        args = mock_smtp.sendmail.call_args[0]
        msg = args[2]

        # Проверяем наличие вложения
        assert (
            "Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            in msg
        )
        assert f"filename={email_message_with_attachment.attachment.name}" in msg


@pytest.mark.asyncio
async def test_send_email_multiple_recipients(email_sender):
    """Тест отправки email нескольким получателям."""
    message = EmailMessage(
        to=["recipient1@example.com", "recipient2@example.com"],
        subject="Test Subject",
        body="<p>Test Body</p>",
    )

    mock_smtp = AsyncMock()
    mock_smtp.sendmail = AsyncMock(return_value={})
    mock_smtp.__aenter__.return_value = mock_smtp

    with patch("aiosmtplib.SMTP", return_value=mock_smtp):
        await email_sender.send(message)

        # Проверяем, что sendmail был вызван с правильными получателями
        mock_smtp.sendmail.assert_called_once()
        args = mock_smtp.sendmail.call_args[0]
        assert args[1] == message.to
