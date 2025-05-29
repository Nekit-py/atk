"""Модуль для работы с базой данных PostgreSQL."""

import asyncpg
import asyncio
from contextlib import asynccontextmanager
import logging

from atk.common import get_required_env_vars

logger = logging.getLogger(__name__)


class DatabasePool:
    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def create_pool(cls, min_size: int = 5, max_size: int = 20):
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
                logger.error(f"Failed to initialize database pool: {e}")
                raise

    @classmethod
    @asynccontextmanager
    async def acquire(cls):
        """
        Получает соединение из пула
        """
        if cls._pool is None:
            raise RuntimeError("Database pool is not initialized")
        # Сначала получаем корутину от базового пула
        acquisition_coroutine = cls._pool.acquire()

        # Затем ждём результат выполнения этой корутины
        connection = await acquisition_coroutine
        yield connection

    @classmethod
    async def close(cls):
        """
        Закрывает пул соединений
        """
        if cls._pool is not None:
            await asyncio.wait_for(cls._pool.close(), timeout=5)
            cls._pool = None
            logger.info("Database pool closed")
