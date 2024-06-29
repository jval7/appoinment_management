from app.appointment_management import bootstrap, adapters
from app.appointment_management.services import process_request


def bootstrap_test_app() -> process_request.AppointmentManagementHandler:
    return bootstrap.BootStrap(
        db_adapter=adapters.InMemoryDb(db={"1": {"id": "1"}}),
        # messages=adapters.FakeNotifications(),
        # llm_adapter=adapters.FakeOpenaiClient(),
    ).setup_dependencies()


def test_create_appointment() -> None:
    app = bootstrap_test_app()
    prompt = """
    crear cita con los siguientes datos:
        Juan Valdez, cedula: 123456789,telefono:3114326789,email:jj@test.com, edad  28,
         motivo de consulta: ansiedad, fecha: 29 de junio de 2024 a las 1 pm, pago en efectivo
    """
    app.process_request(prompt=prompt, requester_phone_number="573127457050")
