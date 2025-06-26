"""Модуль для работы с базой данных Oracle."""

import cx_Oracle_async
from cx_Oracle_async.connections import AsyncConnectionWrapper
import asyncio
from contextlib import asynccontextmanager
import logging
from typing import Optional, AsyncGenerator

from atk.common import get_required_env_vars

logger = logging.getLogger(__name__)


class OraclePool:
    _instance: Optional["OraclePool"] = None
    _pool: Optional[AsyncConnectionWrapper] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def _declare(cls):
        async with cls.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "declare lock_id integer; begin lock_id := ibs.executor.lock_open; end;"
                )

    @classmethod
    async def create_pool(cls, min_size: int = 5, max_size: int = 20) -> None:
        """
        Инициализирует пул соединений
        """
        if cls._pool is None:
            try:
                user, password, host, port, service_name = get_required_env_vars(
                    "ORACLE_USER",
                    "ORACLE_PASSWORD",
                    "ORACLE_HOST",
                    "ORACLE_PORT",
                    "ORACLE_SERVICE_NAME",
                )
                cls._pool = await cx_Oracle_async.create_pool(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    service_name=service_name,
                    min=min_size,
                    max=max_size,
                    timeout=60,
                )
                logger.info("Oracle Database pool initialized successfully")
            except Exception as e:
                logger.error("Failed to initialize Oracle database pool: %s", e)
                raise

    @classmethod
    @asynccontextmanager
    async def acquire(cls) -> AsyncGenerator[AsyncConnectionWrapper, None]:
        """
        Получает соединение из пула
        """
        if cls._pool is None:
            raise RuntimeError("Oracle Database pool is not initialized")
        # Сначала получаем корутину от базового пула
        acquisition_coroutine = cls._pool.acquire()

        # Затем ждём результат выполнения этой корутины
        connection = await acquisition_coroutine
        yield connection
        await cls._pool.release(connection)

    @classmethod
    async def close(cls) -> None:
        """
        Закрывает пул соединений
        """
        if cls._pool is not None:
            await cls._pool.close()
            cls._pool = None
            logger.info("Oracle Database pool closed")
