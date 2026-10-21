from app.models import Appointment, Service
from datetime import datetime, timedelta, timezone

def test_confirmation_link_is_client_initiated_and_unknown_token_is_safe(client):
    assert client.get("/confirmation/unknown").status_code == 404

def test_confirmation_shows_whatsapp_button(client, db, professional):
    service = db.query(Service).filter_by(professional_id=professional.id).one()
    starts = datetime.now(timezone.utc) + timedelta(days=3)
    appt = Appointment(professional_id=professional.id, service_id=service.id, starts_at=starts, ends_at=starts+timedelta(minutes=30), service_name=service.name, duration_minutes=30, client_name="Cliente", client_phone="11999999999")
    db.add(appt); db.commit()
    response = client.get(f"/confirmation/{appt.confirmation_token}")
    assert response.status_code == 200 and "Abrir WhatsApp" in response.text and "wa.me/5511999999999" in response.text
