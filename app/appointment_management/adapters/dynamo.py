from app.appointment_management.domain import ports


class DynamoDbAdapter(ports.DbAdapter):
    def __init__(self, dynamo_client) -> None:
        self._dynamo_client = dynamo_client

    def create_appointment(self, model_params: ports.models.CreateAppointmentParams) -> str:
        print(model_params)

    def modify_appointment(self, model_params: ports.models.ModifyAppointmentParams) -> str:
        print(model_params)

    def delete_appointment(self, model_params: ports.models.DeleteAppointmentParams) -> str:
        print(model_params)
