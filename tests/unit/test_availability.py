from datetime import datetime, timezone
from app.models import Service
from app.services.availability import available_slots

def test_slots_advance_by_service_duration_and_fit_before_close(db, professional):
    service = db.query(Service).filter_by(professional_id=professional.id).one()
    slots = available_slots(db, professional, service, datetime(2030, 1, 7).date(), datetime(2030, 1, 6, tzinfo=timezone.utc))
    assert len(slots) == 16
    assert (slots[1] - slots[0]).total_seconds() == 1800
    assert slots[-1].hour == 19 and slots[-1].minute == 30

def test_busy_slot_is_removed_from_public_availability(db, professional):
    from app.services.appointments import book
    service = db.query(Service).filter_by(professional_id=professional.id).one()
    day = datetime(2030, 1, 7).date()
    first = available_slots(db, professional, service, day, datetime(2030, 1, 6, tzinfo=timezone.utc))[0]
    book(db, professional, service, first, "Cliente", "11999999999")
    assert first not in available_slots(db, professional, service, day, datetime(2030, 1, 6, tzinfo=timezone.utc))
