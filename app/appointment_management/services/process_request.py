from app.appointment_management.domain import ports, exceptions
from app.appointment_management.services import handler_manager


class AppointmentManagementHandler:
    def __init__(
        self,
        messages: ports.Messages,
        llm_executor: ports.LlmAdapter,
        h_manager: handler_manager.HandlerManager,
    ) -> None:
        self._llm_executor = llm_executor
        self._messages = messages
        self._handler_manager = h_manager

    def process_request(self, prompt: str, requester_phone_number: str) -> None:
        try:
            cmd = self._llm_executor(professional_prompt=prompt, requester_phone_number=requester_phone_number)
        except exceptions.InvalidCrudType:
            self._messages.reply(message="No se pudo procesar la solicitud", to=requester_phone_number)
            return
        except exceptions.FieldNotFoundError:
            self._messages.reply(message="Falta algún campo para realizar la operación", to=requester_phone_number)
            return
        try:
            response = self._handler_manager(cmd=cmd)
            self._messages.reply(message=response, to=requester_phone_number)
        except exceptions.ScheduleAlreadyTaken:
            self._messages.reply(message="El horario indicado se encuentra ocupado", to=requester_phone_number)
        except exceptions.AppointmentNotFound:
            self._messages.reply(message="No se encontró la cita", to=requester_phone_number)

    # def manage_notifications(self, broadcaster_phone:str) -> None:
