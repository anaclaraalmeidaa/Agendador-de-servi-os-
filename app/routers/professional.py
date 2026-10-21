from datetime import date, datetime, time, timezone
from uuid import UUID
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.config import BASE_URL
from app.csrf import csrf_for, csrf_valid
from app.database import get_db
from app.models import Appointment, Professional, SchedulePeriod, Service
from app.services.appointments import cancel
from app.services.professional_setup import create_service as add_service, create_period as add_period, update_service
from app.templating import templates
router = APIRouter(prefix="/profissional")

def mutation_redirect(request: Request, url: str):
    if request.headers.get("HX-Request") == "true":
        return HTMLResponse("", headers={"HX-Redirect": url})
    return RedirectResponse(url, status_code=303)

def current(request, db):
    identity = request.session.get("professional_id")
    return db.get(Professional, UUID(identity)) if identity else None

@router.get("/agenda")
def agenda(request: Request, dia: date | None = None, erro: str | None = None, db: Session = Depends(get_db)):
    pro = current(request, db)
    if not pro: return RedirectResponse("/login", status_code=303)
    db.expire(pro, ["services", "periods"])
    zone = ZoneInfo(pro.timezone)
    day = dia or datetime.now(zone).date()
    start = datetime.combine(day, time.min, zone).astimezone(timezone.utc); end = datetime.combine(day, time.max, zone).astimezone(timezone.utc)
    items = db.scalars(select(Appointment).where(Appointment.professional_id == pro.id, Appointment.starts_at >= start, Appointment.starts_at <= end).order_by(Appointment.starts_at)).all()
    return templates.TemplateResponse(request=request, name="professional/agenda.html", context={"professional": pro, "appointments": items, "day": day, "zone": zone, "error_message": {"cancelamento":"Não foi possível cancelar. Verifique a regra de 2 horas.", "servico":"Confira o nome e a duração do serviço.", "horario":"Confira o dia e os horários informados."}.get(erro, ""), "csrf": csrf_for(request), "public_url": f"{BASE_URL}/p/{pro.slug}"})

@router.post("/servicos")
def create_service(request: Request, name: str = Form(), duration_minutes: int = Form(), csrf_token: str = Form(), db: Session = Depends(get_db)):
    pro = current(request, db)
    if not pro: return RedirectResponse("/login", status_code=303)
    if not csrf_valid(request, csrf_token): return mutation_redirect(request, "/profissional/agenda?erro=servico")
    try: add_service(db, pro, name, duration_minutes)
    except ValueError: return mutation_redirect(request, "/profissional/agenda?erro=servico")
    return mutation_redirect(request, "/profissional/agenda")

@router.post("/servicos/{service_id}")
def edit_service(service_id: UUID, request: Request, name: str = Form(), duration_minutes: int = Form(), csrf_token: str = Form(), db: Session = Depends(get_db)):
    pro = current(request, db); service = db.get(Service, service_id) if pro else None
    if not pro: return RedirectResponse("/login", status_code=303)
    if not csrf_valid(request, csrf_token) or not service or service.professional_id != pro.id: return mutation_redirect(request, "/profissional/agenda?erro=servico")
    try: update_service(service, name, duration_minutes)
    except ValueError: return mutation_redirect(request, "/profissional/agenda?erro=servico")
    db.commit()
    return mutation_redirect(request, "/profissional/agenda")

@router.post("/horarios")
def create_period(request: Request, weekday: int = Form(), opens_at: str = Form(), closes_at: str = Form(), csrf_token: str = Form(), db: Session = Depends(get_db)):
    pro = current(request, db)
    if not pro: return RedirectResponse("/login", status_code=303)
    if not csrf_valid(request, csrf_token): return mutation_redirect(request, "/profissional/agenda?erro=horario")
    try: add_period(db, pro, weekday, opens_at, closes_at)
    except ValueError: return mutation_redirect(request, "/profissional/agenda?erro=horario")
    return mutation_redirect(request, "/profissional/agenda")

@router.post("/horarios/{period_id}")
def edit_period(period_id: UUID, request: Request, weekday: int = Form(), opens_at: str = Form(), closes_at: str = Form(), csrf_token: str = Form(), db: Session = Depends(get_db)):
    pro = current(request, db); period = db.get(SchedulePeriod, period_id) if pro else None
    if not pro: return RedirectResponse("/login", status_code=303)
    if not csrf_valid(request, csrf_token) or not period or period.professional_id != pro.id or weekday not in range(1, 8) or closes_at <= opens_at: return mutation_redirect(request, "/profissional/agenda?erro=horario")
    try:
        from app.services.professional_setup import validate_period
        period.weekday, period.opens_at, period.closes_at = validate_period(weekday, opens_at, closes_at)
    except ValueError: return mutation_redirect(request, "/profissional/agenda?erro=horario")
    db.commit()
    return mutation_redirect(request, "/profissional/agenda")

@router.post("/agendamentos/{appointment_id}/cancelar")
def cancel_appointment(appointment_id: UUID, request: Request, csrf_token: str = Form(), db: Session = Depends(get_db)):
    pro = current(request, db); appt = db.get(Appointment, appointment_id) if pro else None
    if not pro: return RedirectResponse("/login", status_code=303)
    if not csrf_valid(request, csrf_token) or not appt or appt.professional_id != pro.id: return mutation_redirect(request, "/profissional/agenda?erro=cancelamento")
    try: cancel(db, appt)
    except ValueError: return mutation_redirect(request, "/profissional/agenda?erro=cancelamento")
    return mutation_redirect(request, "/profissional/agenda")
