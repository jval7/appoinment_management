import json
import os
from typing import cast

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from app.appointment_management.domain import ports, enums, models
from app.commons import base_types, logger


class GoogleCalendar(ports.Calendar):
    def __init__(self, http_client: requests.Session) -> None:
        self._http_client = http_client
        self._scopes = ["https://www.googleapis.com/auth/calendar"]
        self._token_file = self._authenticate()
        self._url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
        self._token = self._token_file["token"]
        self._headers = {"Authorization": f"Bearer {self._token}"}

    def _authenticate(self) -> dict:
        creds = None

        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self._scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("client_secret_app_escritorio_oauth.json", self._scopes)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run

        return cast(dict, json.loads(creds.to_json()))

    def add_event(
        self,
        appointment: models.Appointment,
    ) -> None:

        event_body = {
            "id": (appointment.id.lower() + "test"),
            "summary": appointment.patient.name.upper(),
            "start": {"dateTime": appointment.date.to_str_isoformat()},
            "end": {"dateTime": (appointment.date + base_types.Iso8601Datetime.time_delta(hours=1)).to_str_isoformat()},
            "colorId": self.get_color_id(appointment.appointment_state),
        }

        response = self._http_client.post(url=self._url, headers=self._headers, json=event_body)

        if response.status_code == 200:
            logger.info("Event added successfully: %s with id: %s", response.json(), appointment.id.lower() + "test")
        else:
            logger.warning("Error adding event: %s", response.text)

    def remove_event(self, id_: str) -> None:
        response = self._http_client.delete(url=f"{self._url}/{id_.lower()+'test'}", headers=self._headers)

        if response.status_code == 204:
            logger.info("Event deleted successfully: %s", id_)
        else:
            logger.warning("Error deleting event: %s", response.text)

    def update_event(self, appointment: models.Appointment) -> None:
        event_body = {
            "summary": appointment.patient.name.upper(),
            "start": {"dateTime": appointment.date.to_str_isoformat()},
            "end": {"dateTime": (appointment.date + base_types.Iso8601Datetime.time_delta(hours=1)).to_str_isoformat()},
            "colorId": self.get_color_id(appointment.appointment_state),
        }
        response = self._http_client.patch(url=f"{self._url}/{appointment.id.lower()+'test'}", headers=self._headers, json=event_body)

        if response.status_code == 200:
            logger.info("Event updated successfully: %s", response.json())
        else:
            logger.warning("Error updating event: %s with id: %s", response.text, appointment.id.lower() + "test")

    @staticmethod
    def get_color_id(color: enums.AppointmentState) -> int:
        colors = {
            enums.AppointmentState.NOT_PAID: 4,  # Red
            enums.AppointmentState.PAID: 5,  # Yellow
            # enums.AppointmentState.POLICIES_SENT: 9, # blue
            # enums.AppointmentState.FINAL_REMINDER_SENT: 10,  # Green
        }
        return colors.get(color, 4)
