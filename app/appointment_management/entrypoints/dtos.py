import json
from typing import Any

import pydantic


class _Message(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)
    from_: str = pydantic.Field(..., alias="from")
    id: str
    timestamp: str
    text: dict[str, str] | None = None
    type: str


class _Value(pydantic.BaseModel):
    messages: list[_Message] | None = None
    statuses: list | None = None


class _Change(pydantic.BaseModel):
    value: _Value


class _Entry(pydantic.BaseModel):
    changes: list[_Change]


class _Body(pydantic.BaseModel):
    entry: list[_Entry]


class Event(pydantic.BaseModel):
    body: _Body

    @pydantic.model_validator(mode="before")
    @classmethod
    def parse_body(cls, data: dict[str, Any]) -> dict[str, Any]:
        if isinstance(data["body"], str):
            data["body"] = json.loads(data["body"])
        return data

    def _get_messages(self) -> list[_Message] | None:
        return self.body.entry[0].changes[0].value.messages

    def get_text_message(self) -> str | None:
        messages = self._get_messages()
        if messages and len(messages) > 0:
            if messages[0].type == "text":
                if messages[0].text:
                    response = messages[0].text.get("body")
                    return response
        return None

    def get_requester_phone_number(self) -> str | None:
        messages = self._get_messages()
        if messages and len(messages) > 0:
            return messages[0].from_
        return None
