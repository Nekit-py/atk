import os
import pytest
import asyncpg
from unittest.mock import patch, AsyncMock, MagicMock
from db.postgres import DatabasePool


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset singleton instance before each test."""
    DatabasePool._instance = None
    DatabasePool._pool = None
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
        mock.return_value = pool_instance
        yield mock


@pytest.mark.asyncio
async def test_create_pool_success(mock_env_vars, mock_pool):
    """Test successful pool creation."""
    # Execute
    await DatabasePool.create_pool()

    # Assert
    mock_pool.assert_called_once_with(
        user="test_user",
        password="test_password",
        host="localhost",
        port="5432",
        database="test_db",
        min_size=5,
        max_size=20,
        command_timeout=60,
    )


@pytest.mark.asyncio
async def test_create_pool_custom_size(mock_env_vars, mock_pool):
    """Test pool creation with custom size parameters."""
    # Execute
    await DatabasePool.create_pool(min_size=10, max_size=30)

    # Assert
    mock_pool.assert_called_once_with(
        user="test_user",
        password="test_password",
        host="localhost",
        port="5432",
        database="test_db",
        min_size=10,
        max_size=30,
        command_timeout=60,
    )


@pytest.mark.asyncio
async def test_create_pool_missing_env_vars(mock_pool):
    """Test pool creation with missing environment variables."""
    # Execute and Assert
    with pytest.raises(ValueError) as exc_info:
        await DatabasePool.create_pool()

    assert "Не установлены обязательные переменные окружения" in str(exc_info.value)
    mock_pool.assert_not_called()


@pytest.mark.asyncio
async def test_create_pool_error(mock_env_vars, mock_pool):
    """Test pool creation with database error."""
    # Setup
    mock_pool.side_effect = asyncpg.PostgresError("Connection failed")

    # Execute and Assert
    with pytest.raises(asyncpg.PostgresError) as exc_info:
        await DatabasePool.create_pool()

    assert "Connection failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_acquire_without_pool():
    """Test acquire without initialized pool."""
    # Execute and Assert
    with pytest.raises(RuntimeError) as exc_info:
        async with DatabasePool.acquire():
            pass

    assert "Database pool is not initialized" in str(exc_info.value)


@pytest.mark.asyncio
async def test_acquire_success(mock_env_vars, mock_pool):
    """Test successful connection acquisition."""
    # Создаем мок соединения
    mock_connection = AsyncMock()

    # Мокаем пул: его метод acquire возвращает асинхронный контекстный менеджер
    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = mock_connection
    mock_context_manager.__aexit__.return_value = None

    # Мокаем сам пул
    mock_pool.return_value.acquire = AsyncMock(return_value=mock_context_manager)

    # Инициализация пула
    await DatabasePool.create_pool()

    # Теперь при вызове acquire() внутри DatabasePool acquire() вернется контекст менеджер,
    # который мы замокали
    async with DatabasePool.acquire() as connection:
        # Проверяем, что connection — это наш мок
        assert connection == mock_connection

    # Проверяем, что acquire был вызван
    mock_pool.return_value.acquire.assert_called_once()


@pytest.mark.asyncio
async def test_close_pool(mock_env_vars, mock_pool):
    """Test pool closure."""
    # Setup
    pool_instance = AsyncMock()
    mock_pool.return_value = pool_instance

    # Execute
    await DatabasePool.create_pool()
    await DatabasePool.close()

    # Assert
    pool_instance.close.assert_called_once()


@pytest.mark.asyncio
async def test_singleton_pattern():
    """Test that DatabasePool is a singleton."""
    # Execute
    instance1 = DatabasePool()
    instance2 = DatabasePool()

    # Assert
    assert instance1 is instance2
