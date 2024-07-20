import datetime as dt
import enum
import random
import uuid
from datetime import datetime
from typing import cast, Any

from babel.dates import format_datetime

import pytz  # type: ignore

import pydantic


class BaseEnum(str, enum.Enum):
    # This is a hack to allow the use of enum values as default values in pydantic models
    def _generate_next_value_(name, start, count, last_values) -> str:  # type: ignore # pylint: disable=no-self-argument
        return name


class ValueObject(pydantic.BaseModel):
    class Config:
        frozen = True


class Iso8601Datetime(ValueObject):
    date: datetime

    @staticmethod
    def time_delta(**kwargs: Any) -> dt.timedelta:
        days = kwargs.get("days", 0.0)
        hours = kwargs.get("hours", 0.0)
        return dt.timedelta(days=days, hours=hours)

    def __sub__(self, other: "Iso8601Datetime") -> dt.timedelta:
        if isinstance(other, Iso8601Datetime):
            return self.date - other.date
        raise TypeError(f"Unsupported operation between instances of 'Iso8601Datetime' and '{type(other).__name__}'")

    def __le__(self, other: "Iso8601Datetime") -> bool:
        if isinstance(other, Iso8601Datetime):
            return self.date <= other.date
        raise TypeError(f"Unsupported comparison between instances of 'Iso8601Datetime' and '{type(other).__name__}'")

    def __add__(self, other: dt.timedelta) -> "Iso8601Datetime":
        return Iso8601Datetime(date=self.date + other)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Iso8601Datetime):
            return self.date == other.date
        if isinstance(other, str):
            try:
                return self.date == datetime.fromisoformat(other)
            except ValueError:
                return False
        return False

    @classmethod
    def from_str(cls, date: str) -> "Iso8601Datetime":
        return cls(date=datetime.fromisoformat(date))

    def to_str_words(self) -> str:
        return cast(str, format_datetime(self.date, "EEEE d 'de' MMMM 'de' y 'a las' HH:mm", locale="es_CO"))

    def to_str(self) -> str:
        return self.date.strftime("%Y-%m-%dT%H:%M")

    def to_str_isoformat(self) -> str:
        return self.date.isoformat()

    def to_str_short_date(self) -> str:
        return self.date.strftime("%Y-%m-%d")

    def to_str_hour_minute(self) -> str:
        return self.date.strftime("%H:%M")

    # def __str__(self) -> str:
    #     return self.date.strftime("%Y-%m-%dT%H:%M")

    @staticmethod
    def now() -> "Iso8601Datetime":
        date = datetime.now(pytz.timezone("America/Bogota")).replace(hour=0, minute=0, second=0, microsecond=0)
        return Iso8601Datetime(date=date)


class IDGenerator:
    @staticmethod
    def human_friendly(size: int = 4) -> str:
        if size < 1:
            raise ValueError("The size must be greater than zero")

        # Base32hex alphabet
        base32hex_alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUV"

        # Generate a random string of the specified size
        return "".join(random.choice(base32hex_alphabet) for _ in range(size))  # nosec

    @staticmethod
    def uuid() -> str:
        return str(uuid.uuid4())
