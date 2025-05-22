import os
from dotenv import load_dotenv

load_dotenv()


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
