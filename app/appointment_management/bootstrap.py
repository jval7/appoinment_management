from __future__ import annotations

import functools
import inspect
from collections.abc import Callable

import requests
from openai import OpenAI
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.appointment_management import adapters
from app.appointment_management import configurations
from app.appointment_management.domain import ports
from app.appointment_management.services import process_request, handler_manager, handlers


class BootStrap:
    def __init__(
        self,
        llm_adapter: ports.LlmAdapter | None = None,
        db_adapter: ports.DbAdapter | None = None,
        crud_notificator: ports.Notificator | None = None,
        patient_notificator: ports.Notificator | None = None,
        calendar_adapter: ports.Calendar | None = None,
        h_manager: handler_manager.HandlerManager | None = None,
    ) -> None:
        self._calendar_adapter = calendar_adapter
        self._llm_adapter = llm_adapter
        self._db_adapter = db_adapter
        self._crud_notificator = crud_notificator
        self._patient_notificator = patient_notificator
        self._handler_manager = h_manager

    def setup_dependencies(self) -> process_request.AppointmentManagementHandler:
        configs = configurations.configs
        if not self._llm_adapter:
            openai_client = OpenAI(base_url=configs.openai_url, api_key=configs.openai_api_key)
            self._llm_adapter = adapters.OpenaiExecutor(
                model="gpt-3.5-turbo-0125",
                openai_client=openai_client,
                base_prompt=configurations.base_prompt,
                max_tokens=1000,
                temperature=0,
            )
        if not self._db_adapter:
            self._db_adapter = adapters.DynamoDb(table_name=configs.table_name)
        if not self._crud_notificator:
            self._crud_notificator = self._setup_notificator(configs.crud_number_id, configs)
        if not self._patient_notificator:
            self._patient_notificator = self._setup_notificator(configs.notificator_number_id, configs)
        if not self._calendar_adapter:
            http_client = requests.Session()
            retry = Retry(
                total=3,  # Total number of retries
                backoff_factor=1,  # Time to sleep between retries
                status_forcelist=[429, 500, 502, 503, 504],  # Status codes to retry on
            )
            adapter = HTTPAdapter(max_retries=retry)
            http_client.mount("https://", adapter)
            self._calendar_adapter = adapters.GoogleCalendar(http_client=http_client)
        if not self._handler_manager:
            dependencies = {
                "db_adapter": self._db_adapter,
                "calendar_adapter": self._calendar_adapter,
                "notificator": self._patient_notificator,
                "payment_pending_message": configs.payment_pending_message,
                "cancellation_policy_message": configs.cancellation_policy_message,
            }
            injected_command_handlers = {
                command_type: _inject_dependencies(handler, dependencies) for command_type, handler in handlers.COMMAND_HANDLERS.items()
            }
            self._handler_manager = handler_manager.HandlerManager(command_handlers=injected_command_handlers)

        return process_request.AppointmentManagementHandler(
            llm_executor=self._llm_adapter,
            notificator=self._crud_notificator,
            h_manager=self._handler_manager,
            calendar_adapter=self._calendar_adapter,
        )

    @staticmethod
    def _setup_notificator(number_id: str, configs: configurations.Configs) -> ports.Notificator:
        http_client = requests.Session()
        retry = Retry(
            total=3,  # Total number of retries
            backoff_factor=1,  # Time to sleep between retries
            status_forcelist=[429, 500, 502, 503, 504],  # Status codes to retry on
        )
        adapter = HTTPAdapter(max_retries=retry)
        http_client.mount("https://", adapter)
        return adapters.Notifications(http_client=http_client, url=configs.wsp_url, headers=configs.wsp_headers, number_id=number_id)


def _inject_dependencies(handler: Callable, dependencies: dict) -> Callable:
    params = inspect.signature(handler).parameters
    deps = {name: dependency for name, dependency in dependencies.items() if name in params}
    return functools.partial(handler, **deps)


# app = _BootStrap(llm_adapter=adapters.FakeOpenaiClient(), db_adapter=adapters.InMemoryDb(db={"1": {"id": "1"}})).setup_dependencies()
# app = _BootStrap(db_adapter=adapters.InMemoryDb(db={"1": {"id": "1"}}),messages=adapters.FakeNotifications()).setup_dependencies()
