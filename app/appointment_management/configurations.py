from __future__ import annotations

from typing import Self  # type: ignore

import pydantic
import pydantic_settings

base_prompt = """Interpreta el siguiente mensaje y devuelve tu respuesta en formato JSON. Si falta alguno de los campos,
 omítelo. Hay 4 posibles respuestas:

1. Crear una cita:
{
  "command": "CreateAppointment",
  "name": "nombre del paciente",
  "identification": "identificación del paciente",
  "age": "edad del paciente, este campo debe ser un entero",
  "phone_number": "número de teléfono del paciente",
  "email": "email del paciente",
  "date": "fecha de la cita en formato ISO8601",
  "motive": "motivo de la cita"
  "payment_state": "estado del pago('PENDIENTE'(default), 'PAGO ELECTRONICO', 'PAGO EN EFECTIVO')"
}

2. Modificar o actualizar cita, aqui puede ir cualquier instrucción relacionada con modificar (como agregar pago, cambiar telefono, etc):
{
  "command": "ModifyAppointment",
  "id": "id de la cita a modificar",
  "name": "nombre del paciente",
  "identification": "identificación del paciente",
  "age": "edad del paciente, este campo debe ser un entero",
  "phone_number": "número de teléfono del paciente",
  "email": "email del paciente",
  "date": "fecha de la cita en formato ISO8601",
  "motive": "motivo de la cita",
  "payment_state": "estado del pago('PENDIENTE'(default), 'PAGO ELECTRONICO', 'PAGO EN EFECTIVO')"
}

3. Eliminar una cita, ejemplo (eliminar cita XXXX):
{
  "command": "DeleteAppointment",
  "id": "XXXX"
}

4. Listar citas por fecha( te pueden pedir "dame las siguientes citas):
{
  "command": "GetAppointments",
  "date": "fecha de la cita en formato ISO8601"
}



Si el mensaje no tiene relación con alguna de estas 4 opciones, devuelve:
{
  "command": "InvalidCommand"
}

Es importante que el JSON resultante esté completo y bien estructurado.

el mensaje a interpretar es el siguiente:


"""


class Configs(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    wsp_token: str
    number_id: str
    wsp_url: str
    wsp_headers: dict[str, str] = pydantic.Field(default_factory=dict)
    openai_url: str | None = None
    openai_api_key: str = "123"
    table_name: str

    @pydantic.model_validator(mode="after")
    def check_fields(self) -> Self:
        if not all([self.wsp_token, self.number_id, self.wsp_url]):
            raise ValueError("All fields must be provided")
        self.wsp_url = self.wsp_url.replace("{number_id}", self.number_id)
        self.wsp_headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.wsp_token}"}
        return self
