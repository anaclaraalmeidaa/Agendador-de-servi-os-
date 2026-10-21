from datetime import datetime, time, timezone
from app.models import Appointment, Service, SchedulePeriod
from app.services.availability import available_slots
from app.services.appointments import book
import pytest

def test_available_slots_only_inside_hours_and_future(db, professional):
    service = db.query(Service).filter_by(professional_id=professional.id).one()
    slots = available_slots(db, professional, service, datetime(2030,1,7).date(), datetime(2030,1,6,tzinfo=timezone.utc))
    assert len(slots) == 16 and slots[0].hour == 12

def test_postgres_rejects_overlapping_reservations(db, professional):
    service = db.query(Service).filter_by(professional_id=professional.id).one()
    start = datetime(2030,1,7,12,tzinfo=timezone.utc)
    book(db, professional, service, start, "Uma", "11999999999")
    with pytest.raises(ValueError, match="reservado"):
        book(db, professional, service, start, "Dois", "11888888888")

def test_cancelled_reservation_releases_time(db, professional):
    from app.services.appointments import cancel
    service = db.query(Service).filter_by(professional_id=professional.id).one()
    start = datetime(2030,1,7,12,tzinfo=timezone.utc)
    appt = book(db, professional, service, start, "Uma", "11999999999")
    cancel(db, appt, datetime(2030,1,7,8,tzinfo=timezone.utc))
    book(db, professional, service, start, "Dois", "11888888888")

def test_public_page_and_csrf_protected_booking(client, professional, db):
    service = db.query(Service).filter_by(professional_id=professional.id).one()
    response = client.get(f"/p/{professional.slug}")
    assert response.status_code == 200 and "Corte" in response.text
    token = client.cookies.get("session")
    assert token

def test_unknown_public_profile_is_404(client):
    assert client.get("/p/inexistente").status_code == 404
