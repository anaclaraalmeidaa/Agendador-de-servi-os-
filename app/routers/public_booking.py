from datetime import date, datetime
from zoneinfo import ZoneInfo
from uuid import UUID
from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.csrf import csrf_for, csrf_valid
from app.database import get_db
from app.models import Appointment, Professional, Service
from app.services.availability import available_slots
from app.services.appointments import book, whatsapp_url
from app.templating import templates
router = APIRouter()

def booking_error(request: Request, slug: str, message: str, status_code: int):
    if request.headers.get("HX-Request") == "true":
        return HTMLResponse(f"<p role=\"alert\">{message}</p>", status_code=200)
    return templates.TemplateResponse(request=request, name="public/validation_error.html", context={"slug": slug, "message": message}, status_code=status_code)

@router.get("/p/{slug}", response_class=HTMLResponse)
def profile(slug: str, request: Request, db: Session = Depends(get_db)):
    pro = db.scalar(select(Professional).where(Professional.slug == slug))
    today = datetime.now(ZoneInfo(pro.timezone)).date().isoformat() if pro else date.today().isoformat()
    return templates.TemplateResponse(request=request, name="public/profile.html", context={"professional": pro, "services": pro.services if pro else [], "csrf": csrf_for(request), "today": today, "slot_options": [], "availability_error": ""}, status_code=200 if pro else 404)

@router.get("/p/{slug}/availability")
def availability(slug: str, request: Request, service_id: UUID, dia: date = Query(alias="date"), db: Session = Depends(get_db)):
    pro = db.scalar(select(Professional).where(Professional.slug == slug)); service = db.get(Service, service_id) if pro else None
    if not pro or not service or service.professional_id != pro.id or not service.active: return HTMLResponse("<p>Serviço indisponível.</p>", status_code=404)
    slots = [] if dia < datetime.now(ZoneInfo(pro.timezone)).date() else available_slots(db, pro, service, dia)
    slot_options = [(slot.isoformat(), slot.astimezone(ZoneInfo(pro.timezone)).strftime("%H:%M")) for slot in slots]
    if request.headers.get("HX-Request") != "true":
        response = templates.TemplateResponse(request=request, name="public/profile.html", context={"professional": pro, "services": pro.services, "csrf": csrf_for(request), "today": datetime.now(ZoneInfo(pro.timezone)).date().isoformat(), "slot_options": slot_options, "service": service, "slug": slug, "availability_error": ""})
    else:
        response = templates.TemplateResponse(request=request, name="public/availability.html", context={"slot_options": slot_options, "csrf": csrf_for(request), "slug": slug, "service": service, "professional": pro, "day": dia.isoformat()})
    response.headers["Cache-Control"] = "no-store"
    return response

@router.post("/p/{slug}/appointments")
def create_booking(slug: str, request: Request, service_id: UUID = Form(), starts_at: str = Form(), client_name: str = Form(), client_phone: str = Form(), csrf_token: str = Form(), db: Session = Depends(get_db)):
    pro = db.scalar(select(Professional).where(Professional.slug == slug)); service = db.get(Service, service_id) if pro else None
    if not csrf_valid(request, csrf_token): return booking_error(request, slug, "Formulário expirado. Atualize a página e tente novamente.", 400)
    if not pro or not service or service.professional_id != pro.id or not service.active: return booking_error(request, slug, "Serviço indisponível.", 404)
    if not client_name.strip() or not client_phone.strip(): return booking_error(request, slug, "Informe seu nome e telefone.", 400)
    try: appt = book(db, pro, service, datetime.fromisoformat(starts_at), client_name, client_phone)
    except ValueError as exc: return booking_error(request, slug, str(exc), 409)
    return RedirectResponse(f"/confirmation/{appt.confirmation_token}", status_code=303)

@router.get("/confirmation/{token}", response_class=HTMLResponse)
def confirmation(token: str, request: Request, db: Session = Depends(get_db)):
    appt = db.scalar(select(Appointment).where(Appointment.confirmation_token == token))
    if not appt: return HTMLResponse("Agendamento não encontrado.", status_code=404)
    pro = db.get(Professional, appt.professional_id)
    msg = f"Olá, {pro.name}! Confirmei {appt.service_name} para {appt.starts_at.strftime('%d/%m/%Y às %H:%M')}. Sou {appt.client_name}."
    local_start = appt.starts_at.astimezone(ZoneInfo(pro.timezone))
    msg = f"Olá, {pro.name}! Confirmei {appt.service_name} para {local_start.strftime('%d/%m/%Y às %H:%M')}. Sou {appt.client_name}."
    return templates.TemplateResponse(request=request, name="public/confirmation.html", context={"appointment": appt, "professional": pro, "whatsapp": whatsapp_url(pro.phone, msg), "local_start": local_start})
