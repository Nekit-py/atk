"""Модуль для работы с базой данных PostgreSQL."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Optional

import asyncpg

from atk.common import get_required_env_vars

logger = logging.getLogger(__name__)


class PostgresPool:
    """Класс для управления пулами соединений PostgreSQL.

    Реализует паттерн Singleton и поддерживает множественные именованные пулы
    для подключения к разным базам данных PostgreSQL.

    Attributes:
        _instance: Единственный экземпляр класса (Singleton)
        _pools: Словарь именованных пулов соединений
    """

    _instance: Optional["PostgresPool"] = None
    _pools: dict[str, asyncpg.Pool] = {}

    def __new__(cls):
        """Создает единственный экземпляр класса (Singleton).

        Returns:
            PostgresPool: Единственный экземпляр класса
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ruff: noqa: S107
    @classmethod
    async def create_pool(
        cls,
        user: str = "POSTGRES_USER",
        password: str = "POSTGRES_PASSWORD",
        host: str = "POSTGRES_HOST",
        port: int = "POSTGRES_PORT",
        dbname: str = "POSTGRES_DBNAME",
        *,
        pool_name: str = "default",
        min_size: int = 5,
        max_size: int = 20,
    ) -> None:
        """Инициализирует пул соединений PostgreSQL.

        Создает новый пул соединений с указанными параметрами подключения.
        Если пул с таким именем уже существует, метод завершается без ошибки.

        Args:
            user: Имя пользователя для подключения к базе данных
            password: Пароль для подключения к базе данных
            host: Хост сервера PostgreSQL
            port: Порт сервера PostgreSQL
            dbname: Имя базы данных
            pool_name: Имя пула для идентификации (по умолчанию "default")
            min_size: Минимальное количество соединений в пуле (по умолчанию 5)
            max_size: Максимальное количество соединений в пуле (по умолчанию 20)

        Raises:
            Exception: При ошибке создания пула соединений
        """
        if pool_name not in cls._pools:
            try:
                user, password, host, port, dbname = get_required_env_vars(
                    user, password, host, port, dbname
                )
                cls._pools[pool_name] = await asyncpg.create_pool(
                    user=user,
                    password=password,
                    host=host,
                    port=port,
                    database=dbname,
                    min_size=min_size,
                    max_size=max_size,
                    command_timeout=60,
                )
                logger.info("Database pool initialized successfully")
            except Exception as e:
                logger.error("Failed to initialize database pool: %s", e)
                raise

    @classmethod
    @asynccontextmanager
    async def acquire(
        cls, pool_name: str = "default"
    ) -> AsyncGenerator[asyncpg.Connection, None]:
        """Получает соединение из пула.

        Асинхронный контекстный менеджер для получения соединения из пула.
        Автоматически возвращает соединение в пул при выходе из контекста.

        Args:
            pool_name: Имя пула для получения соединения (по умолчанию "default")

        Yields:
            asyncpg.Connection: Соединение с базой данных

        Raises:
            RuntimeError: Если пул с указанным именем не инициализирован

        Example:
            ```python
            async with PostgresPool.acquire() as connection:
                result = await connection.fetchrow("SELECT 1 as result")
                print(result)
            ```
        """
        if pool_name not in cls._pools:
            raise RuntimeError("Database pool is not initialized")
        # Сначала получаем корутину от базового пула
        acquisition_coroutine = cls._pools[pool_name].acquire()

        # Затем ждём результат выполнения этой корутины
        connection = await acquisition_coroutine
        try:
            yield connection
            # Обязательно возвращаем коннект в пул!
        finally:
            await cls._pools[pool_name].release(connection)

    @classmethod
    async def close_all(cls) -> None:
        """Закрывает все пулы соединений.

        Закрывает все активные пулы и очищает словарь пулов.
        Рекомендуется вызывать при завершении работы приложения.
        """
        for pool in cls._pools.values():
            await pool.close()
            logger.info("Все PostgreSQL пулы соединений закрыты")

    @classmethod
    async def close(cls, pool_name: str = "default") -> None:
        """Закрывает конкретный пул соединений.

        Args:
            pool_name: Имя пула для закрытия (по умолчанию "default")

        Raises:
            KeyError: Если пул с указанным именем не существует
        """
        await cls._pools[pool_name].close()
        logger.info("%s PostgreSQL Database pool closed", pool_name)
