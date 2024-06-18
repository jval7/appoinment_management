import json

import pydantic
from openai import OpenAI

from app.appointment_management.domain import ports, models, exceptions


class OpenaiExecutor(ports.LlmAdapter):
    def __init__(self, model: str, openai_client: OpenAI, base_prompt: str, max_tokens: int, temperature: float) -> None:
        self._model = model
        self._openai_client = openai_client
        self._base_prompt = base_prompt
        self._max_tokens = max_tokens
        self._temperature = temperature

    def __call__(self, professional_prompt: str) -> models.BaseParameters:
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
        return self._string_to_domain(response.choices[0].message.content)

    @staticmethod
    def _string_to_domain(json_string: str) -> models.BaseParameters:
        dict_obj = json.loads(json_string)
        crud_type = dict_obj.pop("command")
        try:
            if crud_type == models.CreateAppointmentParams.get_command_name():
                params = models.CreateAppointmentParams.parse_obj(dict_obj)
            elif crud_type == models.ModifyAppointmentParams.get_command_name():
                params = models.ModifyAppointmentParams.parse_obj(dict_obj)
            elif crud_type == models.DeleteAppointmentParams.get_command_name():
                params = models.DeleteAppointmentParams.parse_obj(dict_obj)
            else:
                raise exceptions.InvalidCrudType(f"Invalid crud_type: {crud_type}")
        except pydantic.ValidationError as e:
            raise exceptions.FieldNotFoundError(f"Field not found: {e}") from e
        return params
