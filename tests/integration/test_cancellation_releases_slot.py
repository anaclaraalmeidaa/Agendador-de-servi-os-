from datetime import datetime, timezone
from app.models import Service
from app.services.appointments import book, cancel
from app.services.availability import available_slots

def test_cancellation_releases_database_and_public_availability_slot(db, professional, client):
    service = db.query(Service).filter_by(professional_id=professional.id).one()
    day = datetime(2030, 1, 7).date()
    start = available_slots(db, professional, service, day, datetime(2030, 1, 6, tzinfo=timezone.utc))[0]
    params = {"service_id": str(service.id), "date": day.isoformat()}
    before = client.get("/p/ana/availability", params=params, headers={"HX-Request":"true"})
    assert start.isoformat() in before.text
    appt = book(db, professional, service, start, "Cliente", "11999999999")
    assert start not in available_slots(db, professional, service, day, datetime(2030, 1, 6, tzinfo=timezone.utc))
    occupied = client.get("/p/ana/availability", params=params, headers={"HX-Request":"true"})
    assert start.isoformat() not in occupied.text
    cancel(db, appt, datetime(2030, 1, 6, 8, tzinfo=timezone.utc))
    assert start in available_slots(db, professional, service, day, datetime(2030, 1, 6, tzinfo=timezone.utc))
    after = client.get("/p/ana/availability", params=params, headers={"HX-Request":"true"})
    assert start.isoformat() in after.text
