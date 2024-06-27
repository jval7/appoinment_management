from typing import Any

import boto3

from app.appointment_management.domain import models, ports, commands, exceptions
from app.commons import base_types


class InMemoryDb(ports.DbAdapter):
    def __init__(self, db: dict | None = None) -> None:
        self._db: dict[str, dict[str, Any]] = db or {}

    def save_agenda(self, agenda: models.Agenda) -> None:
        self._db[agenda.id] = agenda.model_dump()

    def get_agenda(self, agenda_id: str) -> models.Agenda:
        agenda = self._db.get(agenda_id)
        if agenda is None:
            raise exceptions.AgentNotFound("Agenda not found")
        return models.Agenda.parse_obj(agenda)


class DynamoDb(ports.DbAdapter):
    def __init__(self, table_name: str) -> None:
        self._client = boto3.resource("dynamodb")
        self._table = self._client.Table(table_name)

    def save_agenda(self, agenda: models.Agenda) -> None:
        self._table.put_item(Item=agenda.model_dump())

    def get_agenda(self, agenda_id: str) -> models.Agenda:
        response = self._table.get_item(Key={"id": agenda_id})
        if "Item" not in response:
            raise exceptions.AgentNotFound("Agenda not found")
        print(response)
        return models.Agenda.parse_obj(response["Item"])
