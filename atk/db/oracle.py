"""Модуль для работы с базой данных Oracle."""

import cx_Oracle_async
from cx_Oracle_async.connections import AsyncConnectionWrapper
from contextlib import asynccontextmanager
import logging
from typing import Optional, AsyncGenerator

from atk.common import get_required_env_vars

logger = logging.getLogger(__name__)


class OraclePool:
    """Класс для управления пулами соединений Oracle.

    Реализует паттерн Singleton и поддерживает множественные именованные пулы
    для подключения к разным базам данных Oracle.

    Attributes:
        _instance: Единственный экземпляр класса (Singleton)
        _pools: Словарь именованных пулов соединений
    """

    _instance: Optional["OraclePool"] = None
    _pools: dict[str, AsyncConnectionWrapper] = {}

    def __new__(cls):
        """Создает единственный экземпляр класса (Singleton).

        Returns:
            OraclePool: Единственный экземпляр класса
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def _declare(cls):
        """Выполняет объявление блокировки в Oracle.

        Внутренний метод для работы с блокировками Oracle.
        Используется для специфичных операций с Oracle.
        """
        async with cls._pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "declare lock_id integer; begin lock_id := ibs.executor.lock_open; end;"
                )

    @classmethod
    async def create_pool(
        cls,
        user: str,
        password: str,
        host: str,
        port: int,
        service_name: str,
        *,
        pool_name: str = "default",
        min_size: int = 5,
        max_size: int = 20
    ) -> None:
        """Инициализирует пул соединений Oracle.

        Создает новый пул соединений с указанными параметрами подключения.
        Если пул с таким именем уже существует, метод завершается без ошибки.

        Args:
            user: Имя пользователя для подключения к базе данных
            password: Пароль для подключения к базе данных
            host: Хост сервера Oracle
            port: Порт сервера Oracle
            service_name: Имя сервиса Oracle
            pool_name: Имя пула для идентификации (по умолчанию "default")
            min_size: Минимальное количество соединений в пуле (по умолчанию 5)
            max_size: Максимальное количество соединений в пуле (по умолчанию 20)

        Raises:
            Exception: При ошибке создания пула соединений
        """
        if pool_name not in cls._pools:
            try:
                user, password, host, port, service_name = get_required_env_vars(
                    user, password, host, port, service_name
                )
                cls._pools[pool_name] = await cx_Oracle_async.create_pool(
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
    async def acquire(
        cls, pool_name: str = "default"
    ) -> AsyncGenerator[AsyncConnectionWrapper, None]:
        """Получает соединение из пула.

        Асинхронный контекстный менеджер для получения соединения из пула.
        Автоматически возвращает соединение в пул при выходе из контекста.

        Args:
            pool_name: Имя пула для получения соединения (по умолчанию "default")

        Yields:
            AsyncConnectionWrapper: Соединение с базой данных Oracle

        Raises:
            RuntimeError: Если пул с указанным именем не инициализирован

        Example:
            ```python
            async with OraclePool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute("SELECT 1 FROM DUAL")
                    result = await cursor.fetchone()
                    print(result)
            ```
        """
        if pool_name not in cls._pools:
            raise RuntimeError("Oracle Database pool is not initialized")
        # Сначала получаем корутину от базового пула
        acquisition_coroutine = cls._pools[pool_name].acquire()

        # Затем ждём результат выполнения этой корутины
        connection = await acquisition_coroutine
        try:
            yield connection
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
            logger.info("Все Oracle пулы соединений закрыты")

    @classmethod
    async def close(cls, pool_name: str = "default") -> None:
        """Закрывает конкретный пул соединений.

        Args:
            pool_name: Имя пула для закрытия (по умолчанию "default")

        Raises:
            KeyError: Если пул с указанным именем не существует
        """
        await cls._pools[pool_name].close()
        logger.info("%s Oracle Database pool closed", pool_name)
