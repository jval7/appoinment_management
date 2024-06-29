from typing import Self, Any

import pydantic

from app.appointment_management.domain.enums import PaymentState
from app.commons import base_types


class Command(pydantic.BaseModel):
    requester_phone_number: str

    @classmethod
    def get_command_name(cls) -> str:
        return cls.__name__


def _parse_date(data: dict[str, Any]) -> dict[str, Any]:
    if isinstance(data["date"], str):
        data["date"] = base_types.Iso8601Datetime.from_str(date=data["date"])
    return data


def _normalize(name: str | None) -> str | None:
    if name is not None:
        return " ".join((word.capitalize()) for word in name.split(" "))
    return None


class GetAppointments(Command):
    date: base_types.Iso8601Datetime
    _normalize_date = pydantic.model_validator(mode="before")(_parse_date)


class CreateAppointment(Command):
    name: str
    identification: str
    age: int
    phone_number: str  # TODO: validate phone number, add country code
    email: pydantic.EmailStr
    date: base_types.Iso8601Datetime
    motive: str
    payment_state: PaymentState = pydantic.Field(default=PaymentState.PENDING)
    _normalize_date = pydantic.model_validator(mode="before")(_parse_date)
    _normalize_name = pydantic.field_validator("name")(_normalize)


class ModifyAppointment(Command):
    id: str
    name: str | None = None
    identification: str | None = None
    age: int | None = None
    phone_number: str | None = None
    email: pydantic.EmailStr | None = None
    date: base_types.Iso8601Datetime | None = None
    motive: str | None = None
    payment_state: PaymentState | None = None
    _normalize_name = pydantic.field_validator("name")(_normalize)

    @pydantic.model_validator(mode="after")
    def check_fields(self) -> Self:
        if not any([self.name, self.identification, self.phone_number, self.email, self.date, self.motive, self.payment_state, self.age]):
            raise ValueError("At least one field must be provided")

        return self


class DeleteAppointment(Command):
    id: str
