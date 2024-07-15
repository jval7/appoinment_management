from typing import Any

from app.appointment_management.bootstrap import BootStrap
from app.appointment_management.entrypoints import dtos
from app.commons import logger
from app.appointment_management import configurations

app = BootStrap().setup_dependencies()
configs = configurations.configs


def lambda_handler(event: dict, context: dict) -> Any | None:  # pylint: disable=unused-argument
    logger.info("event: %s", event)
    event_dto = dtos.Event.parse_obj(event)

    prompt = event_dto.get_text_message()
    if prompt:
        requester_phone_number = event_dto.get_requester_phone_number()
        if requester_phone_number:
            app.process_request(prompt=prompt, requester_phone_number=requester_phone_number)
            return None
    # notifications
    if event_dto.event_type and event_dto.event_type == "notification_event":
        app.process_notifications()
    elif event_dto.queryStringParameters and event_dto.queryStringParameters.get("hub.mode") == "subscribe":
        token = event_dto.queryStringParameters.get("hub.verify_token")
        hub_challenge = event_dto.queryStringParameters.get("hub.challenge")
        if token == configs.fb_verify_token:
            return hub_challenge
    return None


# lambda_handler(event={"event_type": "notification_event"}, context={})
