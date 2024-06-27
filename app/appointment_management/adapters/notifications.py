import requests

from app.appointment_management.domain import ports
from app.commons import logger


class FakeNotifications(ports.Messages):
    def reply(self, message: str, to: str) -> None:
        print(f"Message: {message} sent to {to}")

    def start_conversation(self, to: str) -> None:
        print(f"Conversation started with {to}")

    def send_email(self, email: str, message: str) -> None:
        print(f"Email: {email} sent with message: {message}")


class Notifications(ports.Messages):
    def __init__(self, http_client: requests.Session, url: str, headers: dict[str, str]) -> None:
        self._http_client = http_client
        self._url = url
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
            logger.warning(f"Error sending message to {to}: {response.text}")

    def start_conversation(self, to: str) -> None:
        self._http_client.post(url=self._url, headers=self._headers)

    def send_email(self, email: str, message: str) -> None:
        # self._http_client.post(url=self._url, headers=self._headers)
        print("correo enviado")
