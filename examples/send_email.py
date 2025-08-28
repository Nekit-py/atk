import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(str(root_dir))

import asyncio

from atk.notifications.email.models import EmailMessage
from atk.notifications.email.sender import EmailSender


async def main():
    sender = EmailSender()
    message = EmailMessage(
        subject="Test",
        body="Test",
        to=["sidorovich_ns@akcept.ru"],
    )
    await sender.send(message)


if __name__ == "__main__":
    asyncio.run(main())
