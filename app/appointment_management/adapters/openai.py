import json
from collections.abc import Callable
from typing import cast

import pydantic
from openai import OpenAI

from app.appointment_management.domain import ports, exceptions, commands
from app.commons import logger


class FakeOpenaiClient(ports.LlmAdapter):
    def __call__(self, professional_prompt: str, requester_phone_number: str) -> commands.Command:
        return commands.CreateAppointment(
            name="nombre del paciente",
            identification="identificación del paciente",
            age=20,
            phone_number="número de teléfono del paciente",
            email="jj@test.com",
            date="2024-06-19T15:20:30",
            motive="motivo de la cita",
            requester_phone_number=requester_phone_number,
        )


class OpenaiExecutor(ports.LlmAdapter):
    def __init__(self, model: str, openai_client: OpenAI, base_prompt: str, max_tokens: int, temperature: float) -> None:
        self._model = model
        self._openai_client = openai_client
        self._base_prompt = base_prompt
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._domain_strategies_parser: dict[str, Callable[[dict], type[commands.Command]]] = {
            commands.CreateAppointment.get_command_name(): commands.CreateAppointment.parse_obj,
            commands.GetAppointments.get_command_name(): commands.GetAppointments.parse_obj,
            commands.ModifyAppointment.get_command_name(): commands.ModifyAppointment.parse_obj,
            commands.DeleteAppointment.get_command_name(): commands.DeleteAppointment.parse_obj,
        }

    def __call__(self, professional_prompt: str, requester_phone_number: str) -> commands.Command:
        response = self._openai_client.chat.completions.create(
            model=self._model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": self._base_prompt},
                {"role": "user", "content": professional_prompt},
            ],
            max_tokens=self._max_tokens,
            temperature=self._temperature,
        )
        return self._string_to_domain(json_string=response.choices[0].message.content, requester_phone_number=requester_phone_number)

    def _string_to_domain(self, json_string: str, requester_phone_number: str) -> commands.Command:
        logger.info("json_string: %s", json_string)
        dict_obj = json.loads(json_string)  # TODO: validate json_string
        dict_obj["requester_phone_number"] = requester_phone_number
        crud_type = dict_obj.pop("command")  # TODO: validate command
        strategy = self._domain_strategies_parser.get(crud_type)
        if not strategy:
            logger.error("Invalid crud_type: %s", crud_type)
            raise exceptions.InvalidCrudType(f"Invalid crud_type: {crud_type}")
        try:
            command_model = cast(commands.Command, strategy(dict_obj))
        except pydantic.ValidationError as e:
            logger.warning("Error validating params: %s", e)
            # error_type = e.errors()[0]["type"] # TODO: return explicit error type
            # variable = e.errors()[0]["loc"][0]
            raise exceptions.FieldNotFoundError()
        return command_model
