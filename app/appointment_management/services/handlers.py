import enum
from collections.abc import Callable

from app.appointment_management.domain import commands, ports, enums
from app.commons import Iso8601Datetime, base_types

_agenda_id = "1"


def create_appointment(
    cmd: commands.CreateAppointment,
    db_adapter: ports.DbAdapter,
    calendar_adapter: ports.Calendar,
    notificator: ports.Notificator,
    payment_pending_message: str,
    cancellation_policy_message: str,
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
    calendar_adapter.add_event(appointment=appointment)
    if cmd.payment_state == enums.PaymentState.PENDING:
        notificator.reply(message=payment_pending_message, to=cmd.phone_number)
    elif cmd.payment_state != enums.PaymentState.PENDING:
        notificator.reply(message=cancellation_policy_message, to=cmd.phone_number)
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
    calendar_adapter: ports.Calendar,
    notificator: ports.Notificator,
    cancellation_policy_message: str,
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
    if any([cmd.date, cmd.payment_state]):
        calendar_adapter.update_event(appointment=appointment)
        if cmd.payment_state != enums.PaymentState.PENDING:
            notificator.reply(message=cancellation_policy_message, to=appointment.patient.phone_number)
    return f"Cita actualizada con id: *{appointment.id}*"


def delete_appointment(
    cmd: commands.DeleteAppointment,
    db_adapter: ports.DbAdapter,
    calendar_adapter: ports.Calendar,
) -> str:
    agenda = db_adapter.get_agenda(agenda_id=_agenda_id)
    agenda.delete_appointment(appointment_id=cmd.id)
    db_adapter.save_agenda(agenda)
    calendar_adapter.remove_event(id_=cmd.id)
    return f"Cita eliminada con id: *{cmd.id}*"


class WspTemplates(base_types.BaseEnum):
    PaymentPending = enum.auto()
    Reminder = enum.auto()


def notify_patients(
    cmd: commands.NotifyPatients,
    db_adapter: ports.DbAdapter,
    number_of_days: int,
    notificator: ports.Notificator,
) -> None:
    agenda = db_adapter.get_agenda(agenda_id=_agenda_id)
    appointments = agenda.get_list_of_appointments_by_range(
        start_date=cmd.date, end_date=cmd.date + Iso8601Datetime.time_delta(days=number_of_days)
    )
    notification_days = [7, 3, 1]
    for appointment in appointments:
        days_between_created_at_and_date = (appointment.created_at - appointment.date).days
        days_until_appointment = (appointment.date - cmd.date).days

        # Define the days when notifications should be sent

        # Check if the appointment is in the notification_days
        if days_until_appointment in notification_days:
            # For NOT_PAID state, avoid sending notifications on consecutive days (8 and 7)
            if appointment.appointment_state == enums.AppointmentState.NOT_PAID:
                if days_until_appointment == 7 and days_between_created_at_and_date == 8:
                    continue
                if days_until_appointment == 3 and days_between_created_at_and_date == 4:
                    continue
                notificator.start_conversation(template=WspTemplates.PaymentPending, to=appointment.patient.phone_number)
            # For PAID state, avoid sending reminders on consecutive days
            elif appointment.appointment_state == enums.AppointmentState.PAID:
                if days_until_appointment == 1:
                    notificator.start_conversation(template=WspTemplates.Reminder, to=appointment.patient.phone_number)
                elif not (days_until_appointment + 1 == days_between_created_at_and_date):
                    notificator.start_conversation(template=WspTemplates.Reminder, to=appointment.patient.phone_number)


COMMAND_HANDLERS: dict[type[commands.Command], Callable] = {
    commands.CreateAppointment: create_appointment,
    commands.GetAppointments: get_appointments_by_date,
    commands.ModifyAppointment: modify_appointment,
    commands.DeleteAppointment: delete_appointment,
    commands.NotifyPatients: notify_patients,
}
