from typing import Any

import pydantic
from typing_extensions import Annotated

from app.appointment_management.domain import enums
from app.commons import base_types
from app.appointment_management.domain import exceptions


###############################################################################
#                                    Entity                                   #
###############################################################################
# def validate_id(cls, data: dict[str, Any]) -> dict[str, Any]:
#     id_ = data.get("id")
#     if id_ and isinstance(id_, str):
#         data["id"] = base_types.HumanFriendlyId(value=id_)
#     return data


class Patient(pydantic.BaseModel):
    id: str = pydantic.Field(default_factory=base_types.IDGenerator.human_friendly)
    name: str
    identification: str
    phone_number: str
    email: pydantic.EmailStr
    age: int

    # _cast_id = pydantic.model_validator(mode="before")(validate_id)

    def __str__(self) -> str:
        return f"Nombre: {self.name}, Identificación: {self.identification}, Número de teléfono: {self.phone_number}, Email: {self.email}, Edad: {self.age}"


class Appointment(pydantic.BaseModel):
    id: str = pydantic.Field(default_factory=base_types.IDGenerator.human_friendly)
    date: Annotated[base_types.Iso8601Datetime, pydantic.PlainSerializer(lambda x: x.to_str())]
    motive: str
    payment_state: enums.PaymentState = pydantic.Field(default=enums.PaymentState.PENDING)
    patient: Patient
    # _cast_id = pydantic.model_validator(mode="before")(validate_id)

    def __str__(self) -> str:
        return "\n".join(
            [
                f"Id: {self.id}",
                f"Fecha: {str(self.date)}",
                f"Motivo: {self.motive}",
                f"Estado de pago: *{self.payment_state.value}*",
                f"Paciente: {str(self.patient.name)}",
            ]
        )

    @pydantic.model_validator(mode="before")
    @classmethod
    def parse_date(cls, data: dict[str, Any]) -> dict[str, Any]:
        if isinstance(data["date"], str):
            data["date"] = base_types.Iso8601Datetime.from_str(date=data["date"])
        return data


###############################################################################
#                                  AGGREGATE                                  #
###############################################################################


class Agenda(pydantic.BaseModel):
    id: str = pydantic.Field(default_factory=base_types.IDGenerator.human_friendly)
    appointments_id: dict[str, Appointment] = pydantic.Field(default_factory=dict)
    calendar: dict[str, dict[str, str]] = pydantic.Field(default_factory=dict)
    # _cast_id = pydantic.model_validator(mode="before")(validate_id)

    # agenda = {
    #     appointments_id: {
    #         "app1": Appointment(),
    #         "app2": Appointment(),
    #     },
    #     calendar: {
    #         "2024-07-06": {
    #             "h1": "app1",
    #             "h2": "app2",
    #         }
    #     },
    # }
    def _validate_appointment_id(self, appointment: Appointment) -> None:
        while appointment.id in self.appointments_id:
            appointment.id = base_types.IDGenerator.human_friendly()

    def add_appointment(
        self,
        name: str,
        identification: str,
        age: int,
        phone_number: str,
        email: pydantic.EmailStr,
        date: base_types.Iso8601Datetime,
        motive: str,
        payment_state: enums.PaymentState,
    ) -> Appointment:
        appointment = Appointment(
            date=date,
            motive=motive,
            payment_state=payment_state,
            patient=Patient(
                name=name,
                identification=identification,
                phone_number=phone_number,
                email=email,
                age=age,
            ),
        )
        self._validate_appointment_id(appointment=appointment)
        self.appointments_id[appointment.id] = appointment
        short_date = appointment.date.to_str_short_date()
        hour_minute = appointment.date.to_str_hour_minute()
        self.calendar.setdefault(short_date, {})
        if hour_minute in self.calendar[short_date]:
            raise exceptions.ScheduleAlreadyTaken(f"The schedule {hour_minute} is already taken")
        self.calendar[short_date][hour_minute] = appointment.id
        return appointment

    def get_appointment_by_id(self, appointment_id: str) -> Appointment:
        appointment = self.appointments_id.get(appointment_id)
        if not appointment:
            raise exceptions.AppointmentNotFound(f"The appointment with id {appointment_id} was not found")
        return appointment

    def modify_appointment(
        self,
        id_: str,
        name: str | None = None,
        identification: str | None = None,
        age: int | None = None,
        phone_number: str | None = None,
        email: pydantic.EmailStr | None = None,
        date: base_types.Iso8601Datetime | None = None,
        motive: str | None = None,
        payment_state: enums.PaymentState | None = None,
    ) -> Appointment:

        original_appointment = self.appointments_id.get(id_)
        if not original_appointment:
            raise exceptions.AppointmentNotFound(f"The appointment with id {id_} was not found")
        updated_appoint = Appointment(
            id=id_,
            date=date or original_appointment.date,
            motive=motive or original_appointment.motive,
            payment_state=payment_state or original_appointment.payment_state,
            patient=Patient(
                name=name or original_appointment.patient.name,
                identification=identification or original_appointment.patient.identification,
                phone_number=phone_number or original_appointment.patient.phone_number,
                email=email or original_appointment.patient.email,
                age=age or original_appointment.patient.age,
            ),
        )

        if updated_appoint.date != original_appointment.date:
            updated_short_date = updated_appoint.date.to_str_short_date()
            updated_hour_minute = updated_appoint.date.to_str_hour_minute()
            if updated_hour_minute in self.calendar[updated_short_date]:
                raise exceptions.ScheduleAlreadyTaken(
                    f"The schedule {updated_hour_minute} is already taken by appointment {self.calendar[updated_short_date][updated_hour_minute]}"
                )
            del self.calendar[original_appointment.date.to_str_short_date()][original_appointment.date.to_str_hour_minute()]
            self.calendar[updated_short_date][updated_hour_minute] = updated_appoint.id
        self.appointments_id[updated_appoint.id] = updated_appoint
        return updated_appoint

    def delete_appointment(self, appointment_id: str) -> None:
        appointment = self.appointments_id.get(appointment_id)
        if not appointment:
            raise exceptions.AppointmentNotFound(f"The appointment with id {appointment_id} was not found")
        del self.appointments_id[appointment_id]
        del self.calendar[appointment.date.to_str_short_date()][appointment.date.to_str_hour_minute()]
        return None

    def get_appointments_by_date(self, date: base_types.Iso8601Datetime) -> list[Appointment]:
        day = self.calendar.get(date.to_str_short_date())
        if not day:
            return []
        appointments_id = day.values()
        appointments = [self.appointments_id[app_id] for app_id in appointments_id]
        return appointments
