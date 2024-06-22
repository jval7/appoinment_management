from app.appointment_management.domain import ports, models, exceptions
from app.appointment_management.services import process_request_strategies as strategies


class AppointmentManagementHandler:
    def __init__(
        self,
        db_adapter,
        messages: ports.Messages,
        llm_executor: ports.LlmAdapter,
        appointment_created_response: str,
        appointment_modified_response: str,
        appointment_deleted_response: str,
    ) -> None:
        self._db_adapter = db_adapter
        self._llm_executor = llm_executor
        self._messages = messages
        self._appointment_created_response = appointment_created_response
        self._appointment_modified_response = appointment_modified_response
        self._appointment_deleted_response = appointment_deleted_response
        self._process_request_strategies: dict[type[models.BaseParameters], strategies.Strategy] = {
            models.CreateAppointmentParams: strategies.CreateAppointmentStrategy(response=self._appointment_created_response),
            models.ModifyAppointmentParams: strategies.ModifyAppointmentStrategy(response=self._appointment_modified_response),
            models.DeleteAppointmentParams: strategies.DeleteAppointmentStrategy(response=self._appointment_deleted_response),
            models.GetAppointments: strategies.GetAppointmentsStrategy(),
        }

    def process_request(self, prompt: str, professional_phone_number: str) -> None:
        try:
            model_params = self._llm_executor(professional_prompt=prompt)
        except exceptions.InvalidCrudType:
            self._messages.reply(message="No se pudo procesar la solicitud", from_="", to=professional_phone_number)
            return
        except exceptions.FieldNotFoundError:
            self._messages.reply(message="Falta algún campo para realizar la operación", from_="", to=professional_phone_number)
            return

        strategy = self._process_request_strategies.get(type(model_params))
        if not strategy:
            raise exceptions.InvalidModelParams(f"Invalid model_params: {model_params}")
        strategy.execute(
            model_params=model_params,
            db_adapter=self._db_adapter,
            messages=self._messages,
            professional_phone_number=professional_phone_number,
        )
