import os
import pytest
from atk.common import get_required_env_vars


def test_get_required_env_vars_all_present():
    """Test when all required environment variables are present."""
    # Setup
    os.environ["TEST_VAR1"] = "value1"
    os.environ["TEST_VAR2"] = "value2"

    # Execute
    result = get_required_env_vars("TEST_VAR1", "TEST_VAR2")

    # Assert
    assert result == ["value1", "value2"]

    # Cleanup
    del os.environ["TEST_VAR1"]
    del os.environ["TEST_VAR2"]


def test_get_required_env_vars_some_missing():
    """Test when some required environment variables are missing."""
    # Setup
    os.environ["TEST_VAR1"] = "value1"
    # TEST_VAR2 is not set

    # Execute and Assert
    with pytest.raises(ValueError) as exc_info:
        get_required_env_vars("TEST_VAR1", "TEST_VAR2")

    assert "Не установлены обязательные переменные окружения: TEST_VAR2" in str(
        exc_info.value
    )

    # Cleanup
    del os.environ["TEST_VAR1"]


def test_get_required_env_vars_all_missing():
    """Test when all required environment variables are missing."""
    # Execute and Assert
    with pytest.raises(ValueError) as exc_info:
        get_required_env_vars("TEST_VAR1", "TEST_VAR2", "TEST_VAR3")

    assert (
        "Не установлены обязательные переменные окружения: TEST_VAR1, TEST_VAR2, TEST_VAR3"
        in str(exc_info.value)
    )


def test_get_required_env_vars_empty_list():
    """Test with empty list of required variables."""
    result = get_required_env_vars()
    assert result == []


def test_get_required_env_vars_empty_values():
    """Test with empty string values."""
    # Setup
    os.environ["TEST_VAR1"] = ""
    os.environ["TEST_VAR2"] = ""

    # Execute
    result = get_required_env_vars("TEST_VAR1", "TEST_VAR2")

    # Assert
    assert result == ["", ""]

    # Cleanup
    del os.environ["TEST_VAR1"]
    del os.environ["TEST_VAR2"]
