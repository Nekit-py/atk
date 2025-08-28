from datetime import datetime, timedelta

import pytest

from atk.dates.models import Period


@pytest.fixture
def base_period():
    return Period(start=datetime(2024, 1, 1, 10, 0), end=datetime(2024, 1, 1, 12, 0))


@pytest.fixture
def overlapping_period():
    return Period(start=datetime(2024, 1, 1, 11, 0), end=datetime(2024, 1, 1, 13, 0))


@pytest.fixture
def non_overlapping_period():
    return Period(start=datetime(2024, 1, 1, 13, 0), end=datetime(2024, 1, 1, 14, 0))


def test_period_creation():
    """Тест создания периода."""
    start = datetime(2024, 1, 1, 10, 0)
    end = datetime(2024, 1, 1, 12, 0)
    period = Period(start, end)

    assert period.start == start
    assert period.end == end


def test_invalid_period():
    """Тест создания некорректного периода."""
    start = datetime(2024, 1, 1, 12, 0)
    end = datetime(2024, 1, 1, 10, 0)

    with pytest.raises(
        ValueError, match="Начало периода не может быть позже конца периода"
    ):
        Period(start, end)


def test_period_str(base_period):
    """Тест строкового представления периода."""
    expected = "01.01.2024 10:00:00 - 01.01.2024 12:00:00"
    assert str(base_period) == expected


def test_period_repr(base_period):
    """Тест представления периода для отладки."""
    expected = "Period(start=2024-01-01 10:00:00, end=2024-01-01 12:00:00)"
    assert repr(base_period) == expected


def test_period_equality(base_period):
    """Тест сравнения периодов."""
    same_period = Period(
        start=datetime(2024, 1, 1, 10, 0), end=datetime(2024, 1, 1, 12, 0)
    )
    different_period = Period(
        start=datetime(2024, 1, 1, 10, 0), end=datetime(2024, 1, 1, 13, 0)
    )

    assert base_period == same_period
    assert base_period != different_period
    assert base_period != "not a period"


def test_period_contains(base_period):
    """Тест проверки вхождения даты в период."""
    inside = datetime(2024, 1, 1, 11, 0)
    outside = datetime(2024, 1, 1, 13, 0)
    boundary_start = datetime(2024, 1, 1, 10, 0)
    boundary_end = datetime(2024, 1, 1, 12, 0)

    assert inside in base_period
    assert outside not in base_period
    assert boundary_start in base_period
    assert boundary_end in base_period


def test_period_duration(base_period):
    """Тест вычисления длительности периода."""
    expected = timedelta(hours=2)
    assert base_period.duration() == expected


def test_period_overlaps(base_period, overlapping_period, non_overlapping_period):
    """Тест проверки пересечения периодов."""
    assert base_period.overlaps(overlapping_period)
    assert not base_period.overlaps(non_overlapping_period)


def test_period_intersection(base_period, overlapping_period, non_overlapping_period):
    """Тест получения пересечения периодов."""
    intersection = base_period.intersection(overlapping_period)
    assert intersection is not None
    assert intersection.start == datetime(2024, 1, 1, 11, 0)
    assert intersection.end == datetime(2024, 1, 1, 12, 0)

    assert base_period.intersection(non_overlapping_period) is None


def test_period_union(base_period, overlapping_period):
    """Тест объединения периодов."""
    union = base_period.union(overlapping_period)
    assert union.start == datetime(2024, 1, 1, 10, 0)
    assert union.end == datetime(2024, 1, 1, 13, 0)


def test_period_shift(base_period):
    """Тест сдвига периода."""
    delta = timedelta(hours=2)
    shifted = base_period.shift(delta)

    assert shifted.start == datetime(2024, 1, 1, 12, 0)
    assert shifted.end == datetime(2024, 1, 1, 14, 0)


def test_period_expand(base_period):
    """Тест расширения периода."""
    delta = timedelta(hours=1)
    expanded = base_period.expand(delta)

    assert expanded.start == datetime(2024, 1, 1, 9, 0)
    assert expanded.end == datetime(2024, 1, 1, 13, 0)


def test_period_is_adjacent():
    """Тест проверки смежности периодов."""
    p1 = Period(start=datetime(2024, 1, 1, 10, 0), end=datetime(2024, 1, 1, 12, 0))
    p2 = Period(start=datetime(2024, 1, 1, 12, 0), end=datetime(2024, 1, 1, 14, 0))
    p3 = Period(start=datetime(2024, 1, 1, 13, 0), end=datetime(2024, 1, 1, 15, 0))

    assert p1.is_adjacent(p2)
    assert not p1.is_adjacent(p3)


def test_period_split():
    """Тест разбиения периода на подпериоды."""
    period = Period(start=datetime(2024, 1, 1, 10, 0), end=datetime(2024, 1, 1, 12, 0))

    # Разбиение на часовые интервалы
    sub_periods = period.split(timedelta(hours=1))

    assert len(sub_periods) == 2
    assert sub_periods[0].start == datetime(2024, 1, 1, 10, 0)
    assert sub_periods[0].end == datetime(2024, 1, 1, 11, 0)
    assert sub_periods[1].start == datetime(2024, 1, 1, 11, 0)
    assert sub_periods[1].end == datetime(2024, 1, 1, 12, 0)


def test_period_split_invalid_delta():
    """Тест разбиения периода с некорректной длительностью."""
    period = Period(start=datetime(2024, 1, 1, 10, 0), end=datetime(2024, 1, 1, 12, 0))

    with pytest.raises(
        ValueError, match="Длительность подпериода должна быть положительной"
    ):
        period.split(timedelta(0))

    with pytest.raises(
        ValueError, match="Длительность подпериода должна быть положительной"
    ):
        period.split(timedelta(-1))
