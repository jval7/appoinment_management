from __future__ import annotations

import functools
import inspect
from collections.abc import Callable
from typing import Any

import melitk
from melitk import restclient

from app import adapters
from app import configurations
from app.domain import models
from app.services import handlers
from app.services import manager


class BootStrap:
    _instance = None
    _handler_manager: manager.HandlerManager

    def __new__(cls, *args: Any, **kwargs: Any) -> BootStrap:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        prompt_evaluator: adapters.AbstractPromptEvaluator | None = None,
        image_evaluator: adapters.AbstractImageEvaluator | None = None,
    ) -> None:
        self._initialized: bool
        if self._initialized:
            return
        self._initialized = True
        self._prompt_evaluator = prompt_evaluator
        self._image_evaluator = image_evaluator
        self.init()

    def get_handler_manager(self) -> manager.HandlerManager:
        return self._handler_manager

    def init(self) -> None:
        """
        Initialize the handler manager, this method is useful when refreshing the configurations.
         We can call it after refreshing to load all the dependencies again
        """
        self._set_up_dependencies()
        dependencies = {"prompt_evaluator": self._prompt_evaluator, "image_evaluator": self._image_evaluator}
        injected_command_handlers = {
            command_type: _inject_dependencies(handler, dependencies) for command_type, handler in handlers.COMMAND_HANDLERS.items()
        }
        self._handler_manager = manager.HandlerManager(command_handlers=injected_command_handlers)

    def _set_up_dependencies(self) -> None:
        if not self._prompt_evaluator:
            prompt_evaluator_params = configurations.confs.get_value("prompt_evaluator")
            http_prompt_evaluator_client = melitk.restclient.new_restclient(
                engine="async",
                config={
                    "READ_TIMEOUT": prompt_evaluator_params["ReadTimeout"],
                    "CONNECT_TIMEOUT": prompt_evaluator_params["ConnectTimeout"],
                    "NUM_POOLS": prompt_evaluator_params["NumPools"],
                    "MAX_SIZE": prompt_evaluator_params["MaxSizePool"],
                    "RETRY_STRATEGY": restclient.SimpleRetryStrategy(
                        delay=prompt_evaluator_params["RetryDelay"], retry_count=prompt_evaluator_params["MaxRetry"]
                    ),
                },
            )
            self._prompt_evaluator = adapters.PromptEvaluator(
                http_client=http_prompt_evaluator_client,  # type: ignore
                prompt_injection_url=prompt_evaluator_params["prompt_injection_url"],
            )
        if not self._image_evaluator:
            image_evaluator_params = configurations.confs.get_value("image_evaluator")
            http_image_evaluator_client = melitk.restclient.new_restclient(
                engine="async",
                config={
                    "READ_TIMEOUT": image_evaluator_params["ReadTimeout"],
                    "CONNECT_TIMEOUT": image_evaluator_params["ConnectTimeout"],
                    "NUM_POOLS": image_evaluator_params["NumPools"],
                    "MAX_SIZE": image_evaluator_params["MaxSizePool"],
                    "RETRY_STRATEGY": restclient.SimpleRetryStrategy(
                        delay=image_evaluator_params["RetryDelay"], retry_count=image_evaluator_params["MaxRetry"]
                    ),
                },
            )
            self._image_evaluator = adapters.ImageEvaluator(
                http_client=http_image_evaluator_client,  # type: ignore
                model_url=image_evaluator_params["image_evaluator_url"],
            )


def _inject_dependencies(handler: Callable, dependencies: dict) -> models.Handler:
    params = inspect.signature(handler).parameters
    deps = {name: dependency for name, dependency in dependencies.items() if name in params}
    return models.Handler(is_coroutine=inspect.iscoroutinefunction(handler), handler=functools.partial(handler, **deps))


def get_handler_manager() -> manager.HandlerManager:
    return BootStrap().get_handler_manager()
