import json
from typing import List, Any

import pydantic


class _Message(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)
    from_: str = pydantic.Field(..., alias="from")
    id: str
    timestamp: str
    text: dict[str, str] | None = None
    type: str


class _Value(pydantic.BaseModel):
    messages: List[_Message] | None = None
    statuses: List | None = None


class _Change(pydantic.BaseModel):
    value: _Value


class _Entry(pydantic.BaseModel):
    changes: List[_Change]


class _Body(pydantic.BaseModel):
    entry: List[_Entry]


class Event(pydantic.BaseModel):
    body: _Body

    @pydantic.model_validator(mode="before")
    @classmethod
    def parse_body(cls, data: dict[str, Any]) -> dict[str, Any]:
        data["body"] = json.loads(data["body"])
        return data

    def _get_messages(self) -> List[_Message] | None:
        return self.body.entry[0].changes[0].value.messages

    def get_text_message(self) -> str | None:
        messages = self._get_messages()
        if messages and len(messages) > 0:
            if messages[0].type == "text":
                return messages[0].text["body"]
        return None

    def get_requester_phone_number(self) -> str | None:
        messages = self._get_messages()
        if messages and len(messages) > 0:
            return messages[0].from_
        return None
