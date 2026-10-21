def test_agenda_requires_professional_login(client):
    assert client.get("/profissional/agenda", follow_redirects=False).status_code == 303

def test_other_professional_cannot_cancel_appointment(client, db, professional):
    import re
    from datetime import datetime, timedelta, timezone
    from app.models import Appointment, Professional, Service
    from app.security import hash_password
    service = db.query(Service).filter_by(professional_id=professional.id).one()
    starts = datetime.now(timezone.utc) + timedelta(days=2)
    appt = Appointment(professional_id=professional.id, service_id=service.id, starts_at=starts, ends_at=starts+timedelta(minutes=30), service_name=service.name, duration_minutes=30, client_name="Cliente", client_phone="11999999999")
    other = Professional(name="Bia", email="bia@example.com", slug="bia", phone="5511888888888", password_hash=hash_password("senha-segura-teste"))
    db.add_all([appt, other]); db.commit()
    login = client.get("/login")
    csrf = re.search(r'name="csrf_token" value="([^"]+)', login.text).group(1)
    client.post("/login", data={"email":other.email,"password":"senha-segura-teste","csrf_token":csrf})
    csrf = re.search(r'name="csrf_token" value="([^"]+)', client.get("/profissional/agenda").text).group(1)
    result = client.post(f"/profissional/agendamentos/{appt.id}/cancelar", data={"csrf_token":csrf}, follow_redirects=False)
    db.refresh(appt)
    assert result.status_code == 303 and appt.status == "confirmed"

def test_owner_agenda_shows_local_appointment_and_csrf_cancel_works(client, db, professional):
    import re
    from datetime import datetime, timedelta, timezone
    from app.models import Appointment, Service
    service = db.query(Service).filter_by(professional_id=professional.id).one()
    starts = datetime.now(timezone.utc) + timedelta(days=2)
    appt = Appointment(professional_id=professional.id, service_id=service.id, starts_at=starts, ends_at=starts+timedelta(minutes=30), service_name="Corte", duration_minutes=30, client_name="Cliente agenda", client_phone="11999999999")
    db.add(appt); db.commit()
    login = client.get("/login")
    csrf = re.search(r'name="csrf_token" value="([^"]+)', login.text).group(1)
    client.post("/login", data={"email":professional.email,"password":"senha-segura-teste","csrf_token":csrf})
    csrf = re.search(r'name="csrf_token" value="([^"]+)', client.get("/profissional/agenda").text).group(1)
    local_day = starts.astimezone(__import__('zoneinfo').ZoneInfo(professional.timezone)).date().isoformat()
    agenda = client.get("/profissional/agenda", params={"dia":local_day})
    assert "Cliente agenda" in agenda.text and "Corte" in agenda.text
    result = client.post(f"/profissional/agendamentos/{appt.id}/cancelar", data={"csrf_token":csrf}, follow_redirects=False)
    db.refresh(appt)
    assert result.status_code == 303 and appt.status == "cancelled" and appt.cancelled_at is not None
