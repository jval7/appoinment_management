from typing import Callable

from app.domain import commands
from app.domain import enums


def process_request(prompt: str,
                    llm_executor: Callable) -> None:
    pass


def create_appointment(db_adapter: Callable, name: str, identification: str, motive: str,
                       appointment_state: enums.AppointmentState = enums.AppointmentState.PENDING,
                       payment_state: enums.PaymentState = enums.PaymentState.PENDING,
                       ) -> None:
    pass


def modify_appointment(db_adapter: Callable, appointment_id: str | None = None, name: str | None = None,
                       identification: str | None = None,
                       motive: str | None = None,
                       appointment_state: enums.AppointmentState | None = None,
                       payment_state: enums.PaymentState | None = None,
                       ) -> None:
    if not any([appointment_id, name, identification, motive, appointment_state, payment_state]):
        raise ValueError("At least one parameter must be provided")


def delete_appointment(db_adapter: Callable, appointment_id: str) -> None:
    pass


def update_appointment(db_dynamo: Callable, appointment_id: str, appointment: dict) -> None:
    pass