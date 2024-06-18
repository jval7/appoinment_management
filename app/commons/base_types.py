import enum
import random
import string
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
    date: str

    def __str__(self) -> str:
        return self.date

    def to_datetime(self) -> datetime:
        return datetime.fromisoformat(self.date)

    @staticmethod
    def now() -> "Iso8601Datetime":
        return Iso8601Datetime(date=datetime.utcnow().isoformat() + "Z")


class IDGenerator:
    @staticmethod
    def human_friendly(size: int = 10) -> str:
        if size < 1:
            raise ValueError("The size must be greater than zero")

        return "".join(random.SystemRandom().choices(string.ascii_uppercase + string.digits, k=size))

    @staticmethod
    def uuid() -> str:
        return str(uuid.uuid4())


class HumanFriendlyId(ValueObject):
    value: str = pydantic.Field(default_factory=IDGenerator.human_friendly)

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.value
