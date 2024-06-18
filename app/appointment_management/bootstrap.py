from __future__ import annotations

from openai import OpenAI
import requests
from requests.adapters import HTTPAdapter, Retry

from app.appointment_management import adapters
from app.appointment_management import configurations
from app.appointment_management.domain import ports
from app.appointment_management.services import handlers


class _BootStrap:
    def __init__(
        self, llm_adapter: ports.LlmAdapter | None = None, db_adapter: ports.DbAdapter | None = None, messages: ports.Messages | None = None
    ) -> None:
        self._llm_adapter = llm_adapter
        self._db_adapter = db_adapter
        self._messages = messages

    def setup_dependencies(self) -> handlers.AppointmentManagementHandler:
        if not self._llm_adapter:
            openai_client = OpenAI(base_url="https://genai.melioffice.com/v1", api_key="1234")
            self._llm_adapter = adapters.OpenaiExecutor(
                model="gpt-3.5-turbo-0125",
                openai_client=openai_client,
                base_prompt=configurations.base_prompt,
                max_tokens=100,
                temperature=0,
            )
            if not self._db_adapter:
                self._db_adapter = adapters.DynamoDbAdapter(dynamo_client=None)
            return handlers.AppointmentManagementHandler(
                llm_executor=self._llm_adapter,
                db_adapter=self._db_adapter,
                appointment_created_response="Cita creada exitosamente",
                appointment_modified_response="Cita modificada exitosamente",
                appointment_deleted_response="Cita eliminada exitosamente",
            )
        if not self._messages:
            http_client = requests.Session()
            messages_config = configurations.MessagesConfig()
            retries = Retry(total=1, status_forcelist=[429, 500, 502, 503, 504, 404])
            http_client.mount("https://", HTTPAdapter(max_retries=retries))
            self._messages = adapters.Notifications(http_client=http_client, url=messages_config.url, headers=messages_config.headers)


app = _BootStrap().setup_dependencies()

# app.process_request(
#     "Agenda el paciente juan carlos con identificación 1234567890, número de teléfono 3187320987,"
#     " email test@test.com, fecha lunes 17 de abril de 2023 a las 10:00 am, motivo consulta general")

# app.process_request(
#     "modifica la cita con id 1234567890")

# app.process_request(
#     "elimina la cita con id 1234567890")
