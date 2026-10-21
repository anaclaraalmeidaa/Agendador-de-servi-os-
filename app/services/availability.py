from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import select
from app.models import Appointment, SchedulePeriod

def available_slots(db, professional, service, day: date, now: datetime | None = None):
    zone = ZoneInfo(professional.timezone)
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None: now = now.replace(tzinfo=timezone.utc)
    duration = timedelta(minutes=service.duration_minutes)
    periods = db.scalars(select(SchedulePeriod).where(SchedulePeriod.professional_id == professional.id, SchedulePeriod.weekday == day.isoweekday()).order_by(SchedulePeriod.opens_at)).all()
    existing = db.scalars(select(Appointment).where(Appointment.professional_id == professional.id, Appointment.status.in_(["confirmed", "completed"]), Appointment.starts_at < datetime.combine(day + timedelta(days=1), time.min, zone).astimezone(timezone.utc), Appointment.ends_at > datetime.combine(day, time.min, zone).astimezone(timezone.utc))).all()
    results = []
    for period in periods:
        start = datetime.combine(day, period.opens_at, zone)
        close = datetime.combine(day, period.closes_at, zone)
        while start + duration <= close:
            end = start + duration
            ustart, uend = start.astimezone(timezone.utc), end.astimezone(timezone.utc)
            if ustart > now and all(not (appt.starts_at < uend and appt.ends_at > ustart) for appt in existing): results.append(ustart)
            start = end
    return results

def is_within_schedule(db, professional, start: datetime, end: datetime) -> bool:
    local = start.astimezone(ZoneInfo(professional.timezone))
    local_end = end.astimezone(ZoneInfo(professional.timezone))
    periods = db.scalars(select(SchedulePeriod).where(SchedulePeriod.professional_id == professional.id, SchedulePeriod.weekday == local.isoweekday())).all()
    return any(p.opens_at <= local.timetz().replace(tzinfo=None) and p.closes_at >= local_end.timetz().replace(tzinfo=None) and local.date() == local_end.date() for p in periods)
