from app.commons import base_types
from typing import Self, Any
import pydantic
import enum

from app.commons import base_types


class PaymentState(base_types.BaseEnum):
    PENDING = enum.auto()
    ELECTRONIC_PAY = enum.auto()
    CASH_PAY = enum.auto()


class Command(pydantic.BaseModel):
    @classmethod
    def get_command_name(cls) -> str:
        return cls.__name__


class GetAppointments(Command):
    number_of_appointments: int = 5


class CreateAppointment(Command):
    appointment_id: base_types.HumanFriendlyId = pydantic.Field(default_factory=base_types.HumanFriendlyId)
    name: str
    identification: str
    phone_number: str
    email: pydantic.EmailStr
    date: base_types.Iso8601Datetime
    motive: str
    payment_state: PaymentState = pydantic.Field(default=PaymentState.PENDING)

    @pydantic.model_validator(mode="before")
    @classmethod
    def parse_date(cls, data: dict[str, Any]) -> dict[str, Any]:
        data["date"] = base_types.Iso8601Datetime(date=data["date"])
        return data

    def __str__(self) -> str:
        return f"Id: {self.appointment_id},  Nombre: {self.name}, Fecha: {str(self.date)}, Estado de pago: {self.payment_state.value}"


class ModifyAppointment(Command):
    appointment_id: base_types.HumanFriendlyId
    name: str | None = None
    identification: str | None = None
    phone_number: str | None = None
    email: pydantic.EmailStr | None = None
    date: base_types.Iso8601Datetime | None = None
    motive: str | None = None
    payment_state: PaymentState | None = None

    @pydantic.model_validator(mode="before")
    @classmethod
    def parse_appointment_id(cls, data: dict[str, Any]) -> dict[str, Any]:
        data["appointment_id"] = base_types.HumanFriendlyId(value=data["appointment_id"])
        return data

    @pydantic.model_validator(mode="after")
    def check_fields(self) -> Self:
        if not any([self.name, self.identification, self.phone_number, self.email, self.date, self.motive, self.payment_state]):
            raise ValueError("At least one field must be provided")

        return self


class DeleteAppointment(Command):
    appointment_id: base_types.HumanFriendlyId

    @pydantic.model_validator(mode="before")
    @classmethod
    def parse_appointment_id(cls, data: dict[str, Any]) -> dict[str, Any]:
        data["appointment_id"] = base_types.HumanFriendlyId(value=data["appointment_id"])
        return data
