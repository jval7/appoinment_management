import enum

from app.commons import base_types


class PaymentState(base_types.BaseEnum):
    PENDING = "PENDIENTE"
    ELECTRONIC_PAY = "PAGO ELECTRONICO"
    CASH_PAY = "PAGO EN EFECTIVO"


class AppointmentState(base_types.BaseEnum):
    NOT_PAID = enum.auto()
    PAID = enum.auto()
    # POLICIES_SENT = enum.auto()
    # FIRST_REMINDER_SENT = enum.auto()
    # FINAL_REMINDER_SENT = enum.auto()
