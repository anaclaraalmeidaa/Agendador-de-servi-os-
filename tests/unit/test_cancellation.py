from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import pytest
from app.services.appointments import cancel

@pytest.mark.parametrize("hours,allowed", [(3, True), (2, True), (1, False)])
def test_cancellation_boundary(hours, allowed):
    now = datetime(2030, 1, 1, tzinfo=timezone.utc)
    appt = SimpleNamespace(status="confirmed", starts_at=now + timedelta(hours=hours), cancelled_at=None)
    if allowed:
        cancel(SimpleNamespace(commit=lambda: None), appt, now)
        assert appt.status == "cancelled" and appt.cancelled_at == now
    else:
        with pytest.raises(ValueError, match="2 horas"):
            cancel(None, appt, now)
