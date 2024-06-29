
import datetime as dt
import json
import os.path

# from googleapiclient.discovery import build
from pprint import pprint
from typing import Dict, Optional

import pytz
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleCalendarManager:
    def __init__(self):
        self._token = self._authenticate()

    @staticmethod
    def _authenticate() -> Dict:
        creds = None

        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("client_secret_app_escritorio_oauth.json", SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        # return build("calendar", "v3", credentials=creds)
        return json.loads(creds.to_json())

    def get_upcoming_events(
        self,
        max_results: int = 10,
        time_min: Optional[str] = None,  # 2021-12-01T00:00:00Z
        time_max: Optional[str] = None,  # 2021-12-01T00:00:00Z
    ):
        token = self._token["token"]
        url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events"
        headers = {"Authorization": f"Bearer {token}"}
        time_min = time_min or dt.datetime.utcnow().isoformat() + "Z"
        time_max = (
            time_max or (dt.datetime.now() + dt.timedelta(days=3)).replace(hour=23, minute=59, second=0, microsecond=0).isoformat() + "Z"
        )

        response = requests.get(
            url,
            headers=headers,
            params={
                "maxResults": max_results,
                "timeMin": time_min,
                "timeMax": time_max,
            },
        )
        pprint(response.json())
        if response.status_code == 200:
            events = response.json().get("items", [])
            if not events:
                print("No upcoming events found.")
            else:
                print("Upcoming events:")
                for event in events:
                    start = event["start"].get("dateTime", event["start"].get("date"))
                    print(f"{start} - {event['summary']}")
                return events
        else:
            print(f"Error: {response.status_code} - {response.text}")

    def get_free_busy_agenda(self, time_min: Optional[str] = None, time_max: Optional[str] = None):
        token = self._token["token"]
        url = f"https://www.googleapis.com/calendar/v3/freeBusy"
        headers = {"Authorization": f"Bearer {token}"}
        time_min = time_min or dt.datetime.now(pytz.timezone("America/Bogota")).isoformat()
        time_max = (
            time_max or (dt.datetime.now() + dt.timedelta(days=3)).replace(hour=23, minute=59, second=0, microsecond=0).isoformat() + "Z"
        )

        response = requests.post(
            url,
            headers=headers,
            json={
                "timeMin": time_min,
                "timeMax": time_max,
                "timeZone": "America/Bogota",
                "items": [{"id": "primary"}],
            },
        )
        # pprint(response.json())
        if response.status_code == 200:
            pprint(response.json())
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def add_event(
        self,
        summary: str,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
    ):
        token = self._token["token"]
        url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events"
        headers = {"Authorization": f"Bearer {token}"}

        event_body = {
            "summary": summary,
            "start": {"dateTime": start_time},
            "end": {"dateTime": end_time},
        }

        if description:
            event_body["description"] = description

        response = requests.post(url, headers=headers, json=event_body)

        if response.status_code == 200:
            print("Event added successfully.")
        else:
            print(f"Error: {response.status_code} - {response.text}")


start_time = (dt.datetime.now() + dt.timedelta(days=1)).isoformat() + "Z"  # Tomorrow
end_time = (dt.datetime.now() + dt.timedelta(days=1, hours=2)).isoformat() + "Z"  # 2 hours later


calendar = GoogleCalendarManager()
# calendar.get_free_busy_agenda()
# calendar.get_upcoming_events()
calendar.add_event(
    summary="Test Event",
    start_time=start_time,
    end_time=end_time,
    description="This is a test event added via script.",
)
