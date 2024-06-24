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
        # self._appointment_created_response = appointment_created_response
        # self._appointment_modified_response = appointment_modified_response
        # self._appointment_deleted_response = appointment_deleted_response
        # self._process_request_strategies: dict[type[commands.Command], handlers.Strategy] = {
        #     commands.CreateAppointment: handlers.create_appointment(response=self._appointment_created_response),
        #     commands.GetAppointments: handlers.get_appointments(),
        # }
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
        response = self._handler_manager(cmd=cmd)
        self._messages.reply(message=response, to=requester_phone_number)
        # handler_strategy = self._process_request_strategies.get(type(cmd))
        # if not handler_strategy:
        #     raise exceptions.InvalidModelParams(f"Invalid cmd: {cmd}")
        # handler_strategy.execute(
        #     cmd=cmd,
        #     db_adapter=self._db_adapter,
        #     messages=self._messages,
        #     professional_phone_number=professional_phone_number,
        # )
