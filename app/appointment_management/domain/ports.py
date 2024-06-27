import abc

from app.appointment_management.domain import commands, models


class LlmAdapter(abc.ABC):
    @abc.abstractmethod
    def __call__(self, professional_prompt: str, requester_phone_number: str) -> commands.Command: ...


class DbAdapter(abc.ABC):
    @abc.abstractmethod
    def save_agenda(self, agenda: models.Agenda) -> None: ...

    @abc.abstractmethod
    def get_agenda(self, agenda_id: str) -> models.Agenda: ...


class Messages(abc.ABC):
    @abc.abstractmethod
    def reply(self, message: str, to: str) -> None: ...

    @abc.abstractmethod
    def start_conversation(self, to: str) -> None: ...

    @abc.abstractmethod
    def send_email(self, email: str, message: str) -> None: ...

    class Notifications(abc.ABC):
        @abc.abstractmethod
        def __call__(self, phone_number: str, email: str): ...
