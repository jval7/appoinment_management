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
        messages: ports.Messages | None = None,
        h_manager: handler_manager.HandlerManager | None = None,
    ) -> None:
        self._llm_adapter = llm_adapter
        self._db_adapter = db_adapter
        self._messages = messages
        self._handler_manager = h_manager

    def setup_dependencies(self) -> process_request.AppointmentManagementHandler:
        configs = configurations.Configs()
        if not self._llm_adapter:
            openai_client = OpenAI(base_url=configs.openai_url, api_key=configs.openai_api_key)
            self._llm_adapter = adapters.OpenaiExecutor(
                model="gpt-3.5-turbo-0125",
                openai_client=openai_client,
                base_prompt=configurations.base_prompt,
                max_tokens=100,
                temperature=0,
            )
        if not self._db_adapter:
            self._db_adapter = adapters.DynamoDb(table_name=configs.table_name)
        if not self._messages:
            http_client = requests.Session()
            retry = Retry(
                total=3,  # Total number of retries
                backoff_factor=1,  # Time to sleep between retries
                status_forcelist=[429, 500, 502, 503, 504],  # Status codes to retry on
            )
            adapter = HTTPAdapter(max_retries=retry)
            http_client.mount("https://", adapter)
            self._messages = adapters.Notifications(http_client=http_client, url=configs.wsp_url, headers=configs.wsp_headers)
        if not self._handler_manager:
            dependencies = {"db_adapter": self._db_adapter}
            injected_command_handlers = {
                command_type: _inject_dependencies(handler, dependencies) for command_type, handler in handlers.COMMAND_HANDLERS.items()
            }
            self._handler_manager = handler_manager.HandlerManager(command_handlers=injected_command_handlers)
        return process_request.AppointmentManagementHandler(
            llm_executor=self._llm_adapter,
            messages=self._messages,
            h_manager=self._handler_manager,
        )


def _inject_dependencies(handler: Callable, dependencies: dict) -> Callable:
    params = inspect.signature(handler).parameters
    deps = {name: dependency for name, dependency in dependencies.items() if name in params}
    return functools.partial(handler, **deps)


# app = _BootStrap(llm_adapter=adapters.FakeOpenaiClient(), db_adapter=adapters.InMemoryDb(db={"1": {"id": "1"}})).setup_dependencies()
# app = _BootStrap(db_adapter=adapters.InMemoryDb(db={"1": {"id": "1"}}),messages=adapters.FakeNotifications()).setup_dependencies()
