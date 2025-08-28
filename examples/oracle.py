import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(str(root_dir))

import asyncio

from atk.db.oracle import OraclePool


async def main():
    # Инициализация пула соединений (параметры берутся из переменных окружения)
    await OraclePool.create_pool(min_size=2, max_size=5)

    # Получение соединения из пула и выполнение запроса
    async with OraclePool.acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT 1 FROM DUAL")
            result = await cursor.fetchone()
            print("Результат запроса:", result)

    # Корректное закрытие пула соединений
    await OraclePool.close()


if __name__ == "__main__":
    asyncio.run(main())
