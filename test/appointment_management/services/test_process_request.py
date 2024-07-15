from app.appointment_management import bootstrap, adapters
from app.appointment_management.services import process_request


def bootstrap_test_app() -> process_request.AppointmentManagementHandler:
    return bootstrap.BootStrap(
        db_adapter=adapters.InMemoryDb(db={"1": {"id": "1"}}),
        crud_notificator=adapters.FakeNotifications(),
        patient_notificator=adapters.FakeNotifications(),
        # llm_adapter=adapters.FakeOpenaiClient(),
    ).setup_dependencies()


def test_create_appointment() -> None:
    app = bootstrap_test_app()
    prompt = """
    crear cita con los siguientes datos:
    Jhon Valderrama , cedula: 123456789,telefono:3114326789,email:jj@test.com,
    29 años, motivo de consulta: ansiedad, fecha: 12 de julio de 2024 a las 3 pm, pago en efectivo
    """
    # prompt = """
    # crear cita con los siguientes datos:
    #     Juan Valdez, cedula: 123456789,telefono:3114326789,email:jj@test.com, edad  28,
    #      motivo de consulta: ansiedad, fecha: 8 de julio de 2024 a las 5 pm, pago realizado
    # """
    app.process_request(prompt=prompt, requester_phone_number="573127457050")
