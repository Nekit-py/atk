import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(str(root_dir))

import asyncio
from atk.db.postgres import PostgresPool


async def main():
    # Инициализация пула соединений (параметры берутся из переменных окружения)
    await PostgresPool.create_pool(min_size=2, max_size=5)

    # Получение соединения из пула и выполнение запроса
    async with PostgresPool.acquire() as connection:
        result = await connection.fetchrow("SELECT 1 as result")
        print("Результат запроса:", result)

    # Корректное закрытие пула соединений
    try:
        await PostgresPool.close()
        print("Пул соединений успешно закрыт")
    except Exception as e:
        print(f"Ошибка при закрытии пула: {e}")


if __name__ == "__main__":
    asyncio.run(main())
