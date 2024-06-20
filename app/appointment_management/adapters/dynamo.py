# from app.appointment_management.domain import ports

from boto3 import resource
from boto3.dynamodb.conditions import Attr, Key
from datetime import datetime


class DynamoDbAdapter:
    # def __init__(self, dynamo_client) -> None:
    #     self._dynamo_client = dynamo_client

    def create_appointment(self, data, dynamo_table_name: str) -> None:
        demo_table = resource("dynamodb").Table(dynamo_table_name)
        response = demo_table.put_item(Item=data)
        print(f"insert response: {response}")

    # print(model_params)

    # def modify_appointment(self, model_params: ports.models.ModifyAppointmentParams) -> str:
    #     print(model_params)

    # def delete_appointment(self, model_params: ports.models.DeleteAppointmentParams) -> str:
    #     print(model_params)


data = {
    "customer_id": "cus-10",  # paritation key
    "order_id": "ord-7",  # sort key
    "status": "approved",
    "created_date": datetime.now().isoformat(),
}
dynamo_conection = DynamoDbAdapter()
dynamo_conection.create_appointment(data=data, dynamo_table_name="dynamo-python")
