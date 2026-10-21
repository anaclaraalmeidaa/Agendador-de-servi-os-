from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from threading import Barrier
from sqlalchemy.exc import IntegrityError
from tests.conftest import TestingSession
from app.models import Appointment, Service

def test_only_one_concurrent_insert_commits(professional):
    barrier = Barrier(2)
    read_db = TestingSession()
    service_id = read_db.query(Service).filter_by(professional_id=professional.id).one().id
    read_db.close()
    def insert(name):
        db = TestingSession()
        try:
            start = datetime(2030,1,7,12,tzinfo=timezone.utc)
            db.add(Appointment(professional_id=professional.id, service_id=service_id, starts_at=start, ends_at=start+timedelta(minutes=30), service_name="Corte", duration_minutes=30, client_name=name, client_phone="11999999999", status="confirmed"))
            barrier.wait(timeout=10)
            db.commit(); return "ok"
        except IntegrityError as exc:
            db.rollback()
            return "conflict" if "appointments_no_overlap" in str(exc) else "unexpected"
        finally: db.close()
    with ThreadPoolExecutor(max_workers=2) as pool: results = list(pool.map(insert, ["Um", "Dois"]))
    assert sorted(results) == ["conflict", "ok"]
