"""Конфигурация pytest."""

import os
import sys
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

import pytest

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset singleton instance before each test."""
    from atk.db.postgres import PostgresPool

    PostgresPool._instance = None
    PostgresPool._pool = None
    yield


@pytest.fixture
def mock_env_vars():
    """Fixture to set up required environment variables."""
    os.environ.update(
        {
            "POSTGRES_USER": "test_user",
            "POSTGRES_PASSWORD": "test_password",
            "POSTGRES_HOST": "localhost",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DBNAME": "test_db",
        }
    )
    yield
    # Cleanup
    for var in [
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DBNAME",
    ]:
        os.environ.pop(var, None)


@pytest.fixture
def mock_pool():
    """Fixture to mock asyncpg.create_pool."""
    with patch("asyncpg.create_pool", new_callable=AsyncMock) as mock:
        pool_instance = AsyncMock()

        # Мокаем acquire как асинхронный контекстный менеджер
        @asynccontextmanager
        async def mock_acquire():
            yield pool_instance.acquire.return_value

        # Настраиваем метод acquire возвращать асинхронный менеджер
        pool_instance.acquire = AsyncMock(side_effect=mock_acquire)
        mock.return_value = pool_instance
        yield mock


@pytest.fixture
def mock_smtp():
    """Fixture to mock aiosmtplib.SMTP."""
    with patch("aiosmtplib.SMTP", new_callable=AsyncMock) as mock:
        smtp_instance = AsyncMock()
        mock.return_value = smtp_instance
        yield mock


@pytest.fixture
def mock_pandas():
    """Fixture to mock pandas DataFrame."""
    with patch("pandas.DataFrame") as mock:
        df_instance = mock.return_value
        yield mock


@pytest.fixture
def mock_openpyxl():
    """Fixture to mock openpyxl Workbook."""
    with patch("openpyxl.Workbook") as mock:
        workbook_instance = mock.return_value
        yield mock
