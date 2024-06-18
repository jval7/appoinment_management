import enum

from app.commons import base_types


class PaymentState(base_types.BaseEnum):
    PENDING = enum.auto()
    ELECTRONIC_PAY = enum.auto()
    CASH_PAY = enum.auto()
