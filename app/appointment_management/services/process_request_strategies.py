from abc import ABC, abstractmethod

from app.appointment_management.domain import models, ports


class Strategy(ABC):
    @abstractmethod
    def execute(self, model_params: models.BaseParameters, db_adapter: ports.DbAdapter, messages: ports.Messages, requester: str) -> None:
        pass


class CreateAppointmentStrategy(Strategy):
    def __init__(self, response: str) -> None:
        self._response = response

    def execute(
        self, model_params: models.CreateAppointmentParams, db_adapter: ports.DbAdapter, messages: ports.Messages, requester: str
    ) -> None:
        db_adapter.create_appointment(model_params)
        messages.reply(message=self._response, to=requester)
        messages.send_email(email=model_params.email, message=self._response)


class ModifyAppointmentStrategy(Strategy):
    def __init__(self, response: str) -> None:
        self._response = response

    def execute(self, model_params: models.CreateAppointmentParams, db_adapter: ports.DbAdapter, messages: ports.Messages, requester: str):
        db_adapter.modify_appointment(model_params)
        messages.reply(message=self._response, to=requester)
        return self._response


class DeleteAppointmentStrategy(Strategy):
    def __init__(self, response: str) -> None:
        self._response = response

    def execute(self, model_params: models.CreateAppointmentParams, db_adapter: ports.DbAdapter, messages: ports.Messages, requester: str):
        db_adapter.delete_appointment(model_params)
        messages.reply(message=self._response, to=requester)
        return self._response
