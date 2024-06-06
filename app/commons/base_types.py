import enum

import pydantic


class BaseEnum(str, enum.Enum):
    # This is a hack to allow the use of enum values as default values in pydantic models
    def _generate_next_value_(name, start, count, last_values) -> str:  # type: ignore # pylint: disable=no-self-argument
        return name


class ValueObject(pydantic.BaseModel):
    class Config:
        frozen = True
