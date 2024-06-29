from app.commons import base_types


class PaymentState(base_types.BaseEnum):
    PENDING = "PENDIENTE"
    ELECTRONIC_PAY = "PAGO ELECTRONICO"
    CASH_PAY = "PAGO EN EFECTIVO"
