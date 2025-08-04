"""Модуль для работы с базой данных PostgreSQL."""

import asyncpg
from contextlib import asynccontextmanager
import logging
from typing import Optional, AsyncGenerator

from atk.common import get_required_env_vars

logger = logging.getLogger(__name__)


class PostgresPool:
    _instance: Optional["PostgresPool"] = None
    _pool: Optional[asyncpg.Pool] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def create_pool(cls, min_size: int = 5, max_size: int = 20) -> None:
        """
        Инициализирует пул соединений
        """
        if cls._pool is None:
            try:
                user, password, host, port, dbname = get_required_env_vars(
                    "POSTGRES_USER",
                    "POSTGRES_PASSWORD",
                    "POSTGRES_HOST",
                    "POSTGRES_PORT",
                    "POSTGRES_DBNAME",
                )
                cls._pool = await asyncpg.create_pool(
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
    async def acquire(cls) -> AsyncGenerator[asyncpg.Connection, None]:
        """
        Получает соединение из пула
        """
        if cls._pool is None:
            raise RuntimeError("Database pool is not initialized")
        # Сначала получаем корутину от базового пула
        acquisition_coroutine = cls._pool.acquire()

        # Затем ждём результат выполнения этой корутины
        connection = await acquisition_coroutine
        try:
            yield connection
            # Обязательно возвращаем коннект в пул!
        finally:
            await cls._pool.release(connection)

    @classmethod
    async def close(cls) -> None:
        """
        Закрывает пул соединений
        """
        if cls._pool is not None:
            await cls._pool.close()
            logger.info("Database pool closed successfully")
            cls._pool = None
