import asyncio
import functools
import logging
import os
import time
from typing import Any, Callable, Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: type[Exception] | tuple[type[Exception], ...] = Exception,
    on_retry: Optional[Callable[[Exception, int], None]] = None,
) -> Callable:
    """
    Декоратор для повторного выполнения функции при возникновении исключений.

    Args:
        max_attempts: Максимальное количество попыток выполнения
        delay: Начальная задержка между попытками в секундах
        backoff: Множитель для увеличения задержки после каждой попытки
        exceptions: Исключение или кортеж исключений, при которых нужно повторять попытку
        on_retry: Функция обратного вызова, которая будет вызвана при каждой повторной попытке.
                 Принимает исключение и номер текущей попытки.

    Returns:
        Декоратор для функции

    Example:
        @retry(max_attempts=3, delay=1.0, backoff=2.0)
        def my_function():
            # код функции
            pass

        @retry(exceptions=(ValueError, TypeError))
        def another_function():
            # код функции
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception: Exception | None = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts - 1:
                        raise

                    if on_retry:
                        on_retry(e, attempt + 1)

                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed: {str(e)}. "
                        f"Retrying in {current_delay} seconds..."
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

            # Эта строка теоретически никогда не должна выполниться
            raise last_exception or RuntimeError("Unexpected error in retry decorator")

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception: Exception | None = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts - 1:
                        raise

                    if on_retry:
                        on_retry(e, attempt + 1)

                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed: {str(e)}. "
                        f"Retrying in {current_delay} seconds..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff

            # Эта строка теоретически никогда не должна выполниться
            raise last_exception or RuntimeError("Unexpected error in retry decorator")

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def get_required_env_vars(*var_names: str) -> list[str]:
    """
    Проверяет, что все переменные окружения, указанные в var_names (как строки имен),
    установлены. Возвращает список значений найденных переменных.
    Если какая-либо переменная не установлена, вызывает исключение ValueError,
    перечисляя имена отсутствующих переменных.
    """
    found_vars_values = []
    missing_vars_names = []

    for name in var_names:
        value = os.getenv(name)
        if value is None:
            missing_vars_names.append(name)
        else:
            found_vars_values.append(value)

    if missing_vars_names:
        raise ValueError(
            f"Не установлены обязательные переменные окружения: {', '.join(missing_vars_names)}"
        )

    return found_vars_values
