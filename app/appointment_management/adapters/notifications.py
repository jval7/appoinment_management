from typing import Any

import pydantic_settings

from app.appointment_management.domain import ports
import requests


class Notifications(ports.Messages):
    def __init__(self, http_client: requests.Session, url: str, headers: dict[str, str]) -> None:
        self._http_client = http_client
        self._url = url
        self._headers = headers

    def reply(self, message: str, from_: str, to: str) -> None:
        self._http_client.post(url=self._url, headers=self._headers)

    def start_conversation(self, to: str) -> None:
        self._http_client.post(url=self._url, headers=self._headers)

    def send_email(self, email: str, message: str) -> None:
        self._http_client.post(url=self._url, headers=self._headers)
