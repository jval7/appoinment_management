import abc

import pydantic

from app.appointment_management.domain import models


class LlmAdapter(abc.ABC):
    @abc.abstractmethod
    def __call__(self, professional_prompt: str) -> models.BaseParameters: ...


class DbAdapter(abc.ABC):
    @abc.abstractmethod
    def create_appointment(self, model_params: models.CreateAppointmentParams) -> str: ...
    @abc.abstractmethod
    def get_appointments(self, number_of_appointments: int) -> list: ...
    @abc.abstractmethod
    def modify_appointment(self, model_params: models.ModifyAppointmentParams) -> str: ...

    @abc.abstractmethod
    def delete_appointment(self, model_params: models.DeleteAppointmentParams) -> str: ...


class Messages(abc.ABC):
    @abc.abstractmethod
    def reply(self, message: str, from_: str, to: str) -> None: ...

    @abc.abstractmethod
    def start_conversation(self, to: str) -> None: ...

    @abc.abstractmethod
    def send_email(self, email: str, message: str) -> None: ...

    class Notifications(abc.ABC):
        @abc.abstractmethod
        def __call__(self, phone_number: str, email: str): ...
