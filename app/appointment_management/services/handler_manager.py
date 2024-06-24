from collections.abc import Callable
from typing import Any

from app.appointment_management.domain import commands
from app.commons import logs

logger = logs.logger


class HandlerManager:
    def __init__(self, command_handlers: dict[type[commands.Command], Callable]) -> None:
        self._command_handlers = command_handlers

    def __call__(self, cmd: commands.Command) -> Any:
        logger.info("Handling command %s", cmd.get_command_name())
        try:
            handler = self._command_handlers[type(cmd)]
            response = handler(cmd)
        except Exception:  # This broad exception is intentional to get any exception and log it
            logger.exception("Error handling command %s", cmd.get_command_name(), exc_info=True)
            raise
        return response
