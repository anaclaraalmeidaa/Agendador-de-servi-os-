from datetime import datetime, timezone
from app.models import Service

def test_booking_requires_name_and_phone_and_returns_confirmation(client, db, professional):
    service = db.query(Service).filter_by(professional_id=professional.id).one()
    profile = client.get("/p/ana/availability", params={"service_id": str(service.id), "date": "2030-01-07"}, headers={"HX-Request": "true"})
    import re
    csrf = re.search(r'name="csrf_token" value="([^"]+)', profile.text).group(1)
    start = datetime(2030,1,7,12,tzinfo=timezone.utc).isoformat()
    response = client.post("/p/ana/appointments", data={"service_id":str(service.id),"starts_at":start,"client_name":"Cliente","client_phone":"11999999999","csrf_token":csrf}, follow_redirects=False)
    assert response.status_code == 303 and response.headers["location"].startswith("/confirmation/")

def test_invalid_csrf_rejects_booking(client, professional, db):
    service = db.query(Service).filter_by(professional_id=professional.id).one()
    response = client.post("/p/ana/appointments", data={"service_id":str(service.id),"starts_at":"2030-01-07T12:00:00+00:00","client_name":"Cliente","client_phone":"11999999999","csrf_token":"bad"})
    assert response.status_code == 400

def test_booking_rejects_past_outside_hours_and_duplicate_slot(client, professional, db):
    service = db.query(Service).filter_by(professional_id=professional.id).one()
    import re
    page = client.get("/p/ana/availability", params={"service_id": str(service.id), "date": "2030-01-07"}, headers={"HX-Request": "true"})
    csrf = re.search(r'name="csrf_token" value="([^"]+)', page.text).group(1)
    base = {"service_id":str(service.id),"client_name":"Cliente","client_phone":"11999999999","csrf_token":csrf}
    past = client.post("/p/ana/appointments", data={**base,"starts_at":"2020-01-06T12:00:00+00:00"})
    outside = client.post("/p/ana/appointments", data={**base,"starts_at":"2030-01-07T11:00:00+00:00"})
    assert past.status_code == outside.status_code == 409
    assert "passado" in past.text and "atendimento" in outside.text
    data = {**base,"starts_at":"2030-01-07T12:00:00+00:00"}
    assert client.post("/p/ana/appointments", data=data, follow_redirects=False).status_code == 303
    conflict = client.post("/p/ana/appointments", data=data)
    assert conflict.status_code == 409 and "reservado" in conflict.text
