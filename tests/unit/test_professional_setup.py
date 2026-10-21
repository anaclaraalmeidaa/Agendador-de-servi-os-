from datetime import date, datetime, time, timedelta, timezone
from types import SimpleNamespace
import pytest
from app.services.appointments import cancel, whatsapp_url
from app.services.professional_setup import validate_period, validate_service

def test_setup_rejects_blank_name_and_nonpositive_duration():
    with pytest.raises(ValueError): validate_service("   ", 30)
    with pytest.raises(ValueError): validate_service("Corte", 0)

def test_period_setup_rejects_invalid_weekday_and_closing_time():
    with pytest.raises(ValueError): validate_period(8, "09:00", "10:00")
    with pytest.raises(ValueError): validate_period(1, "12:00", "10:00")

def test_service_duration_must_be_positive():
    from app.models import Service
    assert Service.__table__.constraints
    assert "duration_minutes > 0" in " ".join(str(c.sqltext) for c in Service.__table__.constraints if hasattr(c, "sqltext"))

def test_period_requires_valid_weekday_and_order():
    from app.models import SchedulePeriod
    checks = " ".join(str(c.sqltext) for c in SchedulePeriod.__table__.constraints if hasattr(c, "sqltext"))
    assert "weekday BETWEEN 1 AND 7" in checks and "closes_at > opens_at" in checks

@pytest.mark.parametrize("delta, allowed", [(timedelta(hours=3), True), (timedelta(hours=1), False), (timedelta(hours=2), True)])
def test_cancellation_two_hour_boundary(delta, allowed):
    now = datetime(2030, 1, 1, tzinfo=timezone.utc)
    appointment = SimpleNamespace(status="confirmed", starts_at=now+delta, cancelled_at=None)
    if allowed: cancel(SimpleNamespace(commit=lambda: None), appointment, now)
    else:
        with pytest.raises(ValueError): cancel(None, appointment, now)

def test_whatsapp_url_encodes_message():
    url = whatsapp_url("+55 (11) 99999-0000", "Olá, Ana! horário 10:00")
    assert url.startswith("https://wa.me/5511999990000?") and "%C3%81" not in url
