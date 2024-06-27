import json

from app.appointment_management.bootstrap import app
from app.appointment_management.entrypoints import dtos
from app.commons import logger


def lambda_handler(event, context):
    logger.info(f"event: {event}")
    event_dto = dtos.Event.parse_obj(event)

    prompt = event_dto.get_text_message()
    if prompt:
        requester_phone_number = event_dto.get_requester_phone_number()
        if requester_phone_number:
            app.process_request(prompt=prompt, requester_phone_number=requester_phone_number)


e = {
    "body": {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "<WHATSAPP_BUSINESS_ACCOUNT_ID>",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "<BUSINESS_DISPLAY_PHONE_NUMBER>",
                                "phone_number_id": "<BUSINESS_PHONE_NUMBER_ID>",
                            },
                            "contacts": [{"profile": {"name": "<WHATSAPP_USER_NAME>"}, "wa_id": "<WHATSAPP_USER_ID>"}],
                            "messages": [
                                {
                                    "from": "573127457050",
                                    "id": "<WHATSAPP_MESSAGE_ID>",
                                    "timestamp": "<WEBHOOK_SENT_TIMESTAMP>",
                                    "text": {
                                        "body": ""},
                                    "type": "text",
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }
}


def inject_prompt(event, prompt):
    event["body"]["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"] = prompt
    event["body"] = json.dumps(event["body"])
    return event


prompt1 = """crear cita con los siguientes datos:

 juan carlos, cedula: 123456789,telefono:3114326789,email:jj@test.com, 29 años, motivo de consulta: ansiedad, fecha: lunes 24 de junio del 2024 a las 4 pm"""

prompt2 = """crear cita con los siguientes datos:

 juan carlos, cedula: 123456789,telefono:3114326789,email:jj@test.com, 29 años, motivo de consulta: ansiedad, fecha: lunes 24 de junio del 2024 a las 3 pm"""

prompt3 = """ dame las citas para el lunes 24 de junio del 2024"""


lambda_handler(inject_prompt(e.copy(), prompt1), None)
lambda_handler(inject_prompt(e.copy(), prompt2), None)
lambda_handler(inject_prompt(e.copy(), prompt3), None)
prompt4 = input("ingrese el prompt:")
prompt5 ="" or input("ingrese el prompt:")
lambda_handler(inject_prompt(e.copy(), prompt4), None)

lambda_handler(inject_prompt(e.copy(), prompt5), None)
