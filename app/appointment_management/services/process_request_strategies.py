from abc import ABC, abstractmethod

from app.appointment_management.domain import models, ports


class Strategy(ABC):
    @abstractmethod
    def execute(
        self, model_params: models.BaseParameters, db_adapter: ports.DbAdapter, messages: ports.Messages, professional_phone_number: str
    ) -> None:
        pass


class CreateAppointmentStrategy(Strategy):
    def __init__(self, response: str) -> None:
        self._response = response

    def execute(
        self,
        model_params: models.CreateAppointmentParams,
        db_adapter: ports.DbAdapter,
        messages: ports.Messages,
        professional_phone_number: str,
    ) -> None:
        db_adapter.create_appointment(model_params)
        messages.reply(message=self._response + " " + str(model_params.appointment_id), to=professional_phone_number, from_="")
        messages.send_email(email=model_params.email, message=self._response)


class ModifyAppointmentStrategy(Strategy):
    def __init__(self, response: str) -> None:
        self._response = response

    def execute(
        self,
        model_params: models.CreateAppointmentParams,
        db_adapter: ports.DbAdapter,
        messages: ports.Messages,
        professional_phone_number: str,
    ):
        db_adapter.modify_appointment(model_params)
        messages.reply(message=self._response, to=professional_phone_number, from_="")
        return self._response


class DeleteAppointmentStrategy(Strategy):
    def __init__(self, response: str) -> None:
        self._response = response

    def execute(
        self,
        model_params: models.DeleteAppointmentParams,
        db_adapter: ports.DbAdapter,
        messages: ports.Messages,
        professional_phone_number: str,
    ):
        db_adapter.delete_appointment(model_params)
        messages.reply(message=self._response, to=professional_phone_number, from_="")
        return self._response


class GetAppointmentsStrategy(Strategy):
    def execute(
        self,
        model_params: models.GetAppointments,
        db_adapter: ports.DbAdapter,
        messages: ports.Messages,
        professional_phone_number: str,
    ):
        appointments = db_adapter.get_appointments(number_of_appointments=model_params.number_of_appointments)
        if not appointments:
            messages.reply(message="No hay citas", to=professional_phone_number, from_="")
            return
        appointments_str = "\n\n".join(map(str, appointments))
        messages.reply(message=appointments_str, to=professional_phone_number, from_="")
        return
