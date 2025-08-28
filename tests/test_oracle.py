import os
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

import cx_Oracle
import pytest

from atk.db.oracle import OraclePool


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset singleton instance before each test."""
    OraclePool._instance = None
    OraclePool._pool = None
    yield


@pytest.fixture
def mock_env_vars():
    """Fixture to set up required environment variables."""
    os.environ.update(
        {
            "ORACLE_USER": "test_user",
            "ORACLE_PASSWORD": "test_password",
            "ORACLE_HOST": "localhost",
            "ORACLE_PORT": "1521",
            "ORACLE_SERVICE_NAME": "test_service",
        }
    )
    yield
    # Cleanup
    for var in [
        "ORACLE_USER",
        "ORACLE_PASSWORD",
        "ORACLE_HOST",
        "ORACLE_PORT",
        "ORACLE_SERVICE_NAME",
    ]:
        os.environ.pop(var, None)


@pytest.mark.asyncio
async def test_create_pool_success(mock_env_vars, mock_pool):
    """Test successful pool creation."""
    # Execute
    await OraclePool.create_pool()

    # Assert
    mock_pool.assert_called_once_with(
        host="localhost",
        port="1521",
        user="test_user",
        password="test_password",
        service_name="test_service",
        min=5,
        max=20,
        timeout=60,
    )


@pytest.mark.asyncio
async def test_create_pool_custom_size(mock_env_vars, mock_pool):
    """Test pool creation with custom size parameters."""
    # Execute
    await OraclePool.create_pool(min_size=10, max_size=30)

    # Assert
    mock_pool.assert_called_once_with(
        host="localhost",
        port="1521",
        user="test_user",
        password="test_password",
        service_name="test_service",
        min=10,
        max=30,
        timeout=60,
    )


@pytest.mark.asyncio
async def test_create_pool_missing_env_vars(mock_pool):
    """Test pool creation with missing environment variables."""
    # Execute and Assert
    with pytest.raises(ValueError) as exc_info:
        await OraclePool.create_pool()

    assert "Не установлены обязательные переменные окружения" in str(exc_info.value)
    mock_pool.assert_not_called()


@pytest.mark.asyncio
async def test_create_pool_error(mock_env_vars, mock_pool):
    """Test pool creation with database error."""
    # Setup
    mock_pool.side_effect = cx_Oracle.DatabaseError("Connection failed")

    # Execute and Assert
    with pytest.raises(cx_Oracle.DatabaseError) as exc_info:
        await OraclePool.create_pool()

    assert "Connection failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_acquire_without_pool():
    """Test acquire without initialized pool."""
    # Execute and Assert
    with pytest.raises(RuntimeError) as exc_info:
        async with OraclePool.acquire():
            pass

    assert "Oracle Database pool is not initialized" in str(exc_info.value)


@pytest.fixture
def mock_pool():
    """Fixture to mock cx_Oracle_async.create_pool."""
    with patch("cx_Oracle_async.create_pool", new_callable=AsyncMock) as mock:
        pool_instance = AsyncMock()

        # Мокаем acquire как асинхронный контекстный менеджер
        @asynccontextmanager
        async def mock_acquire():
            yield pool_instance.acquire.return_value

        # Настраиваем метод acquire возвращать асинхронный менеджер
        pool_instance.acquire = AsyncMock(side_effect=mock_acquire)
        mock.return_value = pool_instance
        yield mock


@pytest.mark.asyncio
async def test_close_pool(mock_env_vars, mock_pool):
    """Test pool closure."""
    # Setup
    pool_instance = AsyncMock()
    mock_pool.return_value = pool_instance

    # Execute
    await OraclePool.create_pool()
    await OraclePool.close()

    # Assert
    pool_instance.close.assert_called_once()


@pytest.mark.asyncio
async def test_singleton_pattern():
    """Test that OraclePool is a singleton."""
    # Execute
    instance1 = OraclePool()
    instance2 = OraclePool()

    # Assert
    assert instance1 is instance2


@pytest.mark.asyncio
async def test_acquire_connection_success(mock_env_vars, mock_pool):
    """Test successful connection acquisition."""
    # Setup
    pool_instance = AsyncMock()
    mock_pool.return_value = pool_instance

    connection_mock = AsyncMock()
    pool_instance.acquire.return_value = connection_mock

    # Execute
    await OraclePool.create_pool()

    async with OraclePool.acquire() as connection:
        assert connection == connection_mock

    # Assert
    pool_instance.acquire.assert_called_once()


@pytest.mark.asyncio
async def test_close_pool_already_closed(mock_env_vars, mock_pool):
    """Test closing already closed pool."""
    # Setup
    pool_instance = AsyncMock()
    mock_pool.return_value = pool_instance

    # Execute
    await OraclePool.create_pool()
    await OraclePool.close()
    await OraclePool.close()  # Second close should not raise error

    # Assert
    pool_instance.close.assert_called_once()  # Should only be called once


@pytest.mark.asyncio
async def test_create_pool_already_exists(mock_env_vars, mock_pool):
    """Test creating pool when it already exists."""
    # Setup
    pool_instance = AsyncMock()
    mock_pool.return_value = pool_instance

    # Execute
    await OraclePool.create_pool()
    await OraclePool.create_pool()  # Second creation should be ignored

    # Assert
    mock_pool.assert_called_once()  # Should only be called once
