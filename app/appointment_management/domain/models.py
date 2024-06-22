import abc
from collections.abc import Callable
from typing import Self, Any

from app.commons import base_types
from app.appointment_management.domain import enums, ports
import pydantic


class BaseParameters(pydantic.BaseModel):
    @classmethod
    def get_command_name(cls) -> str:
        return cls.__name__


class GetAppointments(BaseParameters):
    number_of_appointments: int = 5


class CreateAppointmentParams(BaseParameters):
    appointment_id: base_types.HumanFriendlyId = pydantic.Field(default_factory=base_types.HumanFriendlyId)
    name: str
    identification: str
    phone_number: str
    email: pydantic.EmailStr
    date: base_types.Iso8601Datetime
    motive: str
    payment_state: enums.PaymentState = pydantic.Field(default=enums.PaymentState.PENDING)

    @pydantic.model_validator(mode="before")
    @classmethod
    def parse_date(cls, data: dict[str, Any]) -> dict[str, Any]:
        data["date"] = base_types.Iso8601Datetime(date=data["date"])
        return data

    def __str__(self) -> str:
        return f"Id: {self.appointment_id},  Nombre: {self.name}, Fecha: {str(self.date)}, Estado de pago: {self.payment_state.value}"


class ModifyAppointmentParams(BaseParameters):
    appointment_id: base_types.HumanFriendlyId
    name: str | None = None
    identification: str | None = None
    phone_number: str | None = None
    email: pydantic.EmailStr | None = None
    date: base_types.Iso8601Datetime | None = None
    motive: str | None = None
    payment_state: enums.PaymentState | None = None

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


class DeleteAppointmentParams(BaseParameters):
    appointment_id: base_types.HumanFriendlyId

    @pydantic.model_validator(mode="before")
    @classmethod
    def parse_appointment_id(cls, data: dict[str, Any]) -> dict[str, Any]:
        data["appointment_id"] = base_types.HumanFriendlyId(value=data["appointment_id"])
        return data


class ExecutionParameters(pydantic.BaseModel):
    command: Callable
    parameters: BaseParameters
