from collections.abc import Callable

from app.appointment_management.domain import commands, ports

_agenda_id = "1"


def create_appointment(
    cmd: commands.CreateAppointment,
    db_adapter: ports.DbAdapter,
) -> str:
    agenda = db_adapter.get_agenda(agenda_id=_agenda_id)
    appointment = agenda.add_appointment(
        name=cmd.name,
        identification=cmd.identification,
        age=cmd.age,
        phone_number=cmd.phone_number,
        email=cmd.email,
        date=cmd.date,
        motive=cmd.motive,
        payment_state=cmd.payment_state,
    )
    db_adapter.save_agenda(agenda)

    return f"Cita creada con id: *{appointment.id}*"


def get_appointments_by_date(
    cmd: commands.GetAppointments,
    db_adapter: ports.DbAdapter,
) -> str:
    agenda = db_adapter.get_agenda(agenda_id=_agenda_id)
    appointments = agenda.get_appointments_by_date(date=cmd.date)
    if not appointments:
        return "No se encontraron citas para la fecha indicada"
    appointments_str = [f"- {app}\n\n" for app in appointments]
    return f"Citas encontradas:\n\n {appointments_str}"


def modify_appointment(
    cmd: commands.ModifyAppointment,
    db_adapter: ports.DbAdapter,
) -> str:
    agenda = db_adapter.get_agenda(agenda_id=_agenda_id)
    appointment = agenda.modify_appointment(
        id_=cmd.id,
        name=cmd.name,
        identification=cmd.identification,
        age=cmd.age,
        phone_number=cmd.phone_number,
        email=cmd.email,
        date=cmd.date,
        motive=cmd.motive,
        payment_state=cmd.payment_state,
    )
    db_adapter.save_agenda(agenda)
    return f"Cita actualizada con id: *{appointment.id}*"


def delete_appointment(
    cmd: commands.DeleteAppointment,
    db_adapter: ports.DbAdapter,
) -> str:
    agenda = db_adapter.get_agenda(agenda_id=_agenda_id)
    agenda.delete_appointment(appointment_id=cmd.id)
    db_adapter.save_agenda(agenda)
    return f"Cita eliminada con id: *{cmd.id}*"


# def notify_patients(
#     cmd: commands.NotifyPatients,
#     messages: ports.Messages,
# ) -> str:
#     messages.send_message(message=cmd.message, to=cmd.to)
#     return "Mensaje enviado a los pacientes"


COMMAND_HANDLERS: dict[type[commands.Command], Callable] = {
    commands.CreateAppointment: create_appointment,
    commands.GetAppointments: get_appointments_by_date,
    commands.ModifyAppointment: modify_appointment,
    commands.DeleteAppointment: delete_appointment,
}
