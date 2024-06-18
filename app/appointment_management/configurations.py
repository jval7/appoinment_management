from __future__ import annotations

from typing import Self

import pydantic
import pydantic_settings

base_prompt = """Interpreta el siguiente mensaje y devuelve tu respuesta en formato JSON. Si falta alguno de los campos, omítelo. Hay tres posibles respuestas:

1. Crear una cita:
{
  "command": "CreateAppointmentParams",
  "name": "nombre del paciente",
  "identification": "identificación del paciente",
  "phone_number": "número de teléfono del paciente",
  "email": "email del paciente",
  "date": "fecha de la cita en formato ISO8601",
  "motive": "motivo de la cita"
}

2. Modificar una cita:
{
  "command": "ModifyAppointmentParams",
  "appointment_id": "id de la cita a modificar",
  "name": "nombre del paciente",
  "identification": "identificación del paciente",
  "phone_number": "número de teléfono del paciente",
  "email": "email del paciente",
  "date": "fecha de la cita en formato ISO8601",
  "motive": "motivo de la cita",
  "payment_state": "estado del pago"
}

3. Eliminar una cita:
{
  "command": "DeleteAppointmentParams",
  "appointment_id": "id de la cita a eliminar"
}

Es importante que el JSON resultante esté completo y bien estructurado.

el mensaje a interpretar es el siguiente:


"""


class MessagesConfig(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    token: str
    number_id: str
    url: str
    headers: dict[str, str] = pydantic.Field(default_factory=dict)

    @pydantic.model_validator(mode="after")
    def check_fields(self) -> Self:
        if not all([self.token, self.number_id, self.url]):
            raise ValueError("All fields must be provided")
        self.url.replace("{number_id}", self.number_id)
        self.headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        return self


