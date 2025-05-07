from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Period:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        """Проверяет корректность периода после инициализации."""
        if self.start > self.end:
            raise ValueError("Начало периода не может быть позже конца периода")

    def __str__(self) -> str:
        return f"{self.start.strftime('%d.%m.%Y %H:%M:%S')} - {self.end.strftime('%d.%m.%Y %H:%M:%S')}"

    def __repr__(self) -> str:
        return f"Period(start={self.start}, end={self.end})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Period):
            return False
        return self.start == other.start and self.end == other.end

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash((self.start, self.end))

    def __contains__(self, item: datetime) -> bool:
        return self.start <= item <= self.end

    def duration(self) -> timedelta:
        """Возвращает длительность периода."""
        return self.end - self.start

    def overlaps(self, other: "Period") -> bool:
        """Проверяет, пересекается ли период с другим периодом."""
        return self.start <= other.end and other.start <= self.end

    def intersection(self, other: "Period") -> Optional["Period"]:
        """Возвращает пересечение двух периодов или None, если периоды не пересекаются."""
        if not self.overlaps(other):
            return None
        return Period(start=max(self.start, other.start), end=min(self.end, other.end))

    def union(self, other: "Period") -> "Period":
        """Возвращает объединение двух периодов."""
        return Period(start=min(self.start, other.start), end=max(self.end, other.end))

    def shift(self, delta: timedelta) -> "Period":
        """Сдвигает период на указанный интервал времени."""
        return Period(start=self.start + delta, end=self.end + delta)

    def expand(self, delta: timedelta) -> "Period":
        """Расширяет период на указанный интервал времени в обе стороны."""
        return Period(start=self.start - delta, end=self.end + delta)

    def is_adjacent(self, other: "Period") -> bool:
        """Проверяет, являются ли периоды смежными (имеют общую границу)."""
        return self.end == other.start or self.start == other.end

    def split(self, delta: timedelta) -> list["Period"]:
        """Разбивает период на подпериоды указанной длительности."""
        if delta <= timedelta(0):
            raise ValueError("Длительность подпериода должна быть положительной")

        result = []
        current_start = self.start

        while current_start < self.end:
            current_end = min(current_start + delta, self.end)
            result.append(Period(current_start, current_end))
            current_start = current_end

        return result
