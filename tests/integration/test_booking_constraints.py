from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy.exc import IntegrityError
from app.models import Appointment

def new_row(professional, service, start, status="confirmed"):
    return Appointment(professional_id=professional.id, service_id=service.id, starts_at=start, ends_at=start+timedelta(minutes=30), service_name="Corte", duration_minutes=30, client_name="Teste", client_phone="11999999999", status=status)

def test_postgres_blocks_overlap_but_allows_adjacent_and_other_professional(db, professional):
    from app.models import Professional, Service
    service = db.query(Service).filter_by(professional_id=professional.id).one()
    first = datetime(2030,1,7,12,tzinfo=timezone.utc)
    db.add(new_row(professional, service, first)); db.commit()
    db.add(new_row(professional, service, first+timedelta(minutes=30))); db.commit()
    with pytest.raises(IntegrityError):
        db.add(new_row(professional, service, first+timedelta(minutes=15))); db.commit()
    db.rollback()
    other = Professional(name="Bia", email="bia@example.com", slug="bia", phone="5511000000000", password_hash="hash")
    db.add(other); db.flush()
    other_service = Service(professional_id=other.id, name="Corte", duration_minutes=30); db.add(other_service); db.flush()
    db.add(new_row(other, other_service, first)); db.commit()

def test_cancelled_does_not_block_and_completed_still_blocks(db, professional):
    from app.models import Service
    service = db.query(Service).filter_by(professional_id=professional.id).one()
    start = datetime(2030,1,7,12,tzinfo=timezone.utc)
    db.add(new_row(professional, service, start, "cancelled")); db.commit()
    db.add(new_row(professional, service, start, "completed")); db.commit()
    with pytest.raises(IntegrityError):
        db.add(new_row(professional, service, start)); db.commit()
