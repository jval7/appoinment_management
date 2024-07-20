import requests

from app.appointment_management.domain import ports
from app.commons import logger


class FakeNotifications(ports.Notificator):
    def reply(self, message: str, to: str) -> None:
        print(f"Message: {message} sent to {to}")

    def start_conversation(self, template: str, to: str, parameters: list[str]) -> None:
        print(f"Conversation started with {to} and template: {template}")

    def send_email(self, email: str, message: str) -> None:
        print(f"Email: {email} sent with message: {message}")


class Notifications(ports.Notificator):
    def __init__(self, http_client: requests.Session, url: str, headers: dict[str, str], number_id: str) -> None:
        self._http_client = http_client
        self._url = url.replace("{number_id}", number_id)
        self._headers = headers

    def reply(self, message: str, to: str) -> None:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"body": message},
        }
        response = self._http_client.post(url=self._url, headers=self._headers, json=data)
        if not response.ok:
            logger.warning("Error sending message to %s: %s", to, response.text)

    def start_conversation(self, template: str, to: str, parameters: list[str]) -> None:
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template,
                "language": {"code": "es"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [{"type": "text", "text": parameter} for parameter in parameters],
                    }
                ],
            },
        }
        response = self._http_client.post(url=self._url, headers=self._headers, json=data)
        if not response.ok:
            logger.warning("Error starting conversation with %s: %s", to, response.text)

    def send_email(self, email: str, message: str) -> None:
        # self._http_client.post(url=self._url, headers=self._headers)
        print("correo enviado")
