import enum

from app.commons import base_types


class AppointmentState(base_types.BaseEnum):
    PENDING = enum.auto()
    CANCELLED = enum.auto()
    COMPLETED = enum.auto()


class PaymentState(base_types.BaseEnum):
    PENDING = enum.auto()
    ELECTRONIC_PAY = enum.auto()
    CASH_PAY = enum.auto()
