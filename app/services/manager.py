from typing import Any

from app import commons
from app.commons import logs
from app.domain import commands, models

logger = logs.logger


class HandlerManager:
    def __init__(self, command_handlers: dict[type[commands.Command], models.Handler]) -> None:
        self._command_handlers = command_handlers

    @commons.timeit(func_name="handler time")
    async def handle_command(self, cmd: commands.Command) -> Any:
        logger.info("Handling command %s", cmd.get_command_name())
        try:
            handler = self._command_handlers[type(cmd)]
            if handler.is_coroutine:
                response = await handler.handler(cmd)
            else:
                response = handler.handler(cmd)
        except Exception:  # This broad exception is intentional to get any exception and log it
            logger.exception("Error handling command %s", cmd.get_command_name(), exc_info=True)
            raise
        return response
