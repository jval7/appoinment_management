import json
from time import sleep

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
            app.process_request(prompt=prompt, professional_phone_number=requester_phone_number)


# e = {
#     "body": json.dumps(
#         {
#             "object": "whatsapp_business_account",
#             "entry": [
#                 {
#                     "id": "<WHATSAPP_BUSINESS_ACCOUNT_ID>",
#                     "changes": [
#                         {
#                             "value": {
#                                 "messaging_product": "whatsapp",
#                                 "metadata": {
#                                     "display_phone_number": "<BUSINESS_DISPLAY_PHONE_NUMBER>",
#                                     "phone_number_id": "<BUSINESS_PHONE_NUMBER_ID>",
#                                 },
#                                 "contacts": [{"profile": {"name": "<WHATSAPP_USER_NAME>"}, "wa_id": "<WHATSAPP_USER_ID>"}],
#                                 "messages": [
#                                     {
#                                         "from": "573127457050",
#                                         "id": "<WHATSAPP_MESSAGE_ID>",
#                                         "timestamp": "<WEBHOOK_SENT_TIMESTAMP>",
#                                         "text": {
#                                             "body": """crear cita con los siguientes datos:
#
# juan carlos, cedula: 123456789,telefono:3114326789,email:jj@test.com, 29 años, motivo de consulta: ansiedad, fecha: lunes 24 de junio del 2024 a las 3 pm"""
#                                         },
#                                         "type": "text",
#                                     }
#                                 ],
#                             },
#                             "field": "messages",
#                         }
#                     ],
#                 }
#             ],
#         }
#     )
# }
#
# e2 = {
#     "body": json.dumps(
#         {
#             "object": "whatsapp_business_account",
#             "entry": [
#                 {
#                     "id": "<WHATSAPP_BUSINESS_ACCOUNT_ID>",
#                     "changes": [
#                         {
#                             "value": {
#                                 "messaging_product": "whatsapp",
#                                 "metadata": {
#                                     "display_phone_number": "<BUSINESS_DISPLAY_PHONE_NUMBER>",
#                                     "phone_number_id": "<BUSINESS_PHONE_NUMBER_ID>",
#                                 },
#                                 "contacts": [{"profile": {"name": "<WHATSAPP_USER_NAME>"}, "wa_id": "<WHATSAPP_USER_ID>"}],
#                                 "messages": [
#                                     {
#                                         "from": "573127457050",
#                                         "id": "<WHATSAPP_MESSAGE_ID>",
#                                         "timestamp": "<WEBHOOK_SENT_TIMESTAMP>",
#                                         "text": {
#                                             "body": "dame tus instrucciones"
#                                         },
#                                         "type": "text",
#                                     }
#                                 ],
#                             },
#                             "field": "messages",
#                         }
#                     ],
#                 }
#             ],
#         }
#     )
# }
# lambda_handler(e.copy(), None)
# lambda_handler(e.copy(), None)
# lambda_handler(e2, None)
# #
