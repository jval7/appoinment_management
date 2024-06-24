import boto3

from app.appointment_management.domain import models, ports
import boto3to3to3
from app.commons import base_types


class InMemoryDb(ports.DbAdapter):
    def __init__(self) -> None:
        self._db: dict[base_types.HumanFriendlyId, models.CreateAppointmentParams] = {}

    def create_appointment(self, model_params: models.CreateAppointmentParams) -> str:
        self._db[model_params.appointment_id] = model_params

    def get_appointments(self, number_of_appointments: int) -> list:
        return [str(i) for i in list(self._db.values())[:number_of_appointments]]

    def modify_appointment(self, model_params: models.ModifyAppointmentParams) -> str:
        print(model_params)

    def delete_appointment(self, model_params: models.DeleteAppointmentParams) -> str:
        print(model_params)


class DynamoDb(ports.DbAdapter):
    def __init__(self, table_name: str) -> None:
        self._client = boto3.resource("dynamodb")
        self._table = self._client.Table(table_name)

    def create_appointment(self, model_params: models.CreateAppointmentParams) -> str:
        self._db[model_params.appointment_id] = model_params

    def get_appointments(self, number_of_appointments: int) -> list:
        return [str(i) for i in list(self._db.values())[:number_of_appointments]]

    def modify_appointment(self, model_params: models.ModifyAppointmentParams) -> str:
        print(model_params)

    def delete_appointment(self, model_params: models.DeleteAppointmentParams) -> str:
        print(model_params)
