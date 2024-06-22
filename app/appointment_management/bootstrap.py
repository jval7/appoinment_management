from __future__ import annotations

from openai import OpenAI
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
        messages_config = configurations.Configs()
        if not self._llm_adapter:
            openai_client = OpenAI(base_url=messages_config.openai_url, api_key=messages_config.openai_api_key)
            self._llm_adapter = adapters.OpenaiExecutor(
                model="gpt-3.5-turbo-0125",
                openai_client=openai_client,
                base_prompt=configurations.base_prompt,
                max_tokens=100,
                temperature=0,
            )
        if not self._db_adapter:
            self._db_adapter = adapters.InMemoryDb()
        if not self._messages:
            http_client = requests.Session()

            retry = Retry(
                total=0,  # Total number of retries
                backoff_factor=0.1,  # Time to sleep between retries
                status_forcelist=[429, 500, 502, 503, 504],  # Status codes to retry on
            )
            adapter = HTTPAdapter(max_retries=retry)
            http_client.mount("https://", adapter)
            self._messages = adapters.Notifications(http_client=http_client, url=messages_config.url, headers=messages_config.headers)
        return handlers.AppointmentManagementHandler(
            llm_executor=self._llm_adapter,
            messages=self._messages,
            db_adapter=self._db_adapter,
            appointment_created_response="Cita creada exitosamente",
            appointment_modified_response="Cita modificada exitosamente",
            appointment_deleted_response="Cita eliminada exitosamente",
        )


# app = _BootStrap(llm_adapter=adapters.FakeOpenaiClient()).setup_dependencies()
app = _BootStrap().setup_dependencies()
