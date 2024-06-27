import enum
import random
import string
import time
import uuid
from datetime import datetime

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

    def __eq__(self, other):
        if isinstance(other, Iso8601Datetime):
            return self.date == other.date
        elif isinstance(other, str):
            return self.date == datetime.fromisoformat(other)
        else:
            return False

    @classmethod
    def from_str(cls, date: str) -> "Iso8601Datetime":
        return cls(date=datetime.fromisoformat(date))

    def to_str(self) -> str:
        return self.date.strftime("%Y-%m-%dT%H:%M")

    def to_str_short_date(self) -> str:
        return self.date.strftime("%Y-%m-%d")

    def to_str_hour_minute(self) -> str:
        return self.date.strftime("%H:%M")

    def __str__(self) -> str:
        return self.date.strftime("%Y-%m-%dT%H:%M")

    @staticmethod
    def now() -> "Iso8601Datetime":
        return Iso8601Datetime(date=datetime.now())


class IDGenerator:
    @staticmethod
    def human_friendly(size: int = 4) -> str:
        if size < 1:
            raise ValueError("The size must be greater than zero")

        return "".join(random.SystemRandom().choices(string.ascii_uppercase + string.digits, k=size))

    @staticmethod
    def uuid() -> str:
        return str(uuid.uuid4())


