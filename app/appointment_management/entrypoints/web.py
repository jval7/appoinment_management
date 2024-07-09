from app.appointment_management.bootstrap import BootStrap
from app.appointment_management.entrypoints import dtos
from app.commons import logger

app = BootStrap().setup_dependencies()


def lambda_handler(event: dict, context: dict) -> None:  # pylint: disable=unused-argument
    logger.info("event: %s", event)
    event_dto = dtos.Event.parse_obj(event)

    prompt = event_dto.get_text_message()
    if prompt:
        requester_phone_number = event_dto.get_requester_phone_number()
        if requester_phone_number:
            app.process_request(prompt=prompt, requester_phone_number=requester_phone_number)
