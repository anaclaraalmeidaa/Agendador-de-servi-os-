from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models import Appointment, Professional, Service
from app.services.availability import available_slots, is_within_schedule

def book(db, professional: Professional, service: Service, start: datetime, name: str, phone: str):
    now = datetime.now(timezone.utc)
    if start.tzinfo is None: raise ValueError("Escolha um horário válido.")
    end = start + timedelta(minutes=service.duration_minutes)
    if start <= now: raise ValueError("Não é possível agendar no passado.")
    if not is_within_schedule(db, professional, start, end): raise ValueError("Esse horário está fora do atendimento.")
    local_day = start.astimezone(ZoneInfo(professional.timezone)).date()
    if start.astimezone(timezone.utc) not in available_slots(db, professional, service, local_day, now):
        raise ValueError("Esse horário acabou de ser reservado. Escolha outro horário.")
    appt = Appointment(professional_id=professional.id, service_id=service.id, starts_at=start, ends_at=end, service_name=service.name, duration_minutes=service.duration_minutes, client_name=name.strip(), client_phone=phone.strip())
    db.add(appt)
    try: db.commit()
    except IntegrityError as exc:
        db.rollback()
        if "appointments_no_overlap" in str(exc): raise ValueError("Esse horário acabou de ser reservado. Escolha outro horário.") from exc
        raise
    return appt

def cancel(db, appointment, now=None):
    now = now or datetime.now(timezone.utc)
    if appointment.status != "confirmed": raise ValueError("Este agendamento não pode mais ser cancelado.")
    if appointment.starts_at - now < timedelta(hours=2): raise ValueError("O cancelamento precisa ser feito com pelo menos 2 horas de antecedência.")
    appointment.status = "cancelled"; appointment.cancelled_at = now
    db.commit()

from app.services.whatsapp import whatsapp_url
