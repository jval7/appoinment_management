from collections.abc import Callable

from app.appointment_management.domain import commands, ports


def create_appointment(
    model_params: commands.CreateAppointment,
    db_adapter: ports.DbAdapter,
) -> None:
    db_adapter.create_appointment(model_params)


def get_appointments(
    model_params: commands.GetAppointments,
    db_adapter: ports.DbAdapter,
):
    appointments = db_adapter.get_appointments(number_of_appointments=model_params.number_of_appointments)
    if not appointments:
        messages.reply(message="No hay citas", from_="")
        return
    appointments_str = "\n\n".join(map(str, appointments))
    return


COMMAND_HANDLERS: dict[type[commands.Command], Callable] = {
    commands.CreateAppointment: create_appointment,
    commands.GetAppointments: get_appointments,
}
