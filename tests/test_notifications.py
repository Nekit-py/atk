import pytest
from pydantic_core import ValidationError as PydanticValidationError

from atk.notifications import EmailAttachment, EmailMessage


@pytest.fixture
def valid_attachment():
    return EmailAttachment(data=b"test data", name="test.txt")


@pytest.fixture
def valid_message():
    return EmailMessage(to="test@example.com", subject="Test Subject", body="Test Body")


def test_attachment_creation(valid_attachment):
    """Тест создания вложения."""
    assert valid_attachment.data == b"test data"
    assert valid_attachment.name == "test.txt"


def test_invalid_attachment():
    """Тест создания некорректного вложения."""
    with pytest.raises(ValueError, match="Данные вложения не могут быть пустыми"):
        EmailAttachment(data=b"", name="test.txt")

    with pytest.raises(ValueError, match="Имя вложения не может быть пустым"):
        EmailAttachment(data=b"test", name="")

    with pytest.raises(ValueError, match="Имя вложения содержит недопустимые символы"):
        EmailAttachment(data=b"test", name="test/file.txt")


def test_message_creation(valid_message):
    """Тест создания сообщения."""
    assert str(valid_message.to) == "test@example.com"
    assert valid_message.subject == "Test Subject"
    assert valid_message.body == "Test Body"
    assert valid_message.cc is None
    assert valid_message.attachment is None


def test_invalid_message():
    """Тест создания некорректного сообщения."""
    with pytest.raises(PydanticValidationError):
        EmailMessage(to="invalid-email", subject="Test", body="Test")

    with pytest.raises(
        PydanticValidationError, match="String should have at least 1 character"
    ):
        EmailMessage(to="test@example.com", subject="", body="Test")

    with pytest.raises(
        PydanticValidationError, match="String should have at least 1 character"
    ):
        EmailMessage(to="test@example.com", subject="Test", body="")


def test_message_with_cc():
    """Тест сообщения с копией."""
    # Один получатель копии
    message = EmailMessage(
        to="test@example.com", subject="Test", body="Test", cc="cc@example.com"
    )
    assert str(message.cc) == "cc@example.com"

    # Несколько получателей копии
    message = EmailMessage(
        to="test@example.com",
        subject="Test",
        body="Test",
        cc=["cc1@example.com", "cc2@example.com"],
    )
    assert [str(cc) for cc in message.cc] == ["cc1@example.com", "cc2@example.com"]


def test_message_with_attachment(valid_attachment):
    """Тест сообщения с вложением."""
    message = EmailMessage(
        to="test@example.com", subject="Test", body="Test", attachment=valid_attachment
    )
    assert message.attachment == valid_attachment
    assert message.has_attachments()
    assert message.get_attachment_size() == len(valid_attachment.data)


def test_message_with_multiple_recipients():
    """Тест сообщения с несколькими получателями."""
    message = EmailMessage(
        to=["user1@example.com", "user2@example.com"], subject="Test", body="Test"
    )
    assert [str(to) for to in message.to] == ["user1@example.com", "user2@example.com"]


def test_format_recipients():
    """Тест форматирования списка получателей."""
    message = EmailMessage(
        to=["user1@example.com", "user2@example.com"],
        subject="Test",
        body="Test",
        cc=["cc1@example.com", "cc2@example.com"],
    )

    expected = "user1@example.com, user2@example.com, cc1@example.com, cc2@example.com"
    assert message.format_recipients() == expected
