import re

def test_schedule_create_and_invalid_period(client, db, professional):
    page = client.get("/login")
    csrf = re.search(r'name="csrf_token" value="([^"]+)', page.text).group(1)
    client.post("/login", data={"email":professional.email,"password":"senha-segura-teste","csrf_token":csrf})
    csrf = re.search(r'name="csrf_token" value="([^"]+)', client.get("/profissional/agenda").text).group(1)
    good = client.post("/profissional/horarios", data={"weekday":2,"opens_at":"10:00","closes_at":"14:00","csrf_token":csrf}, follow_redirects=False)
    bad = client.post("/profissional/horarios", data={"weekday":2,"opens_at":"14:00","closes_at":"10:00","csrf_token":csrf}, follow_redirects=False)
    assert good.status_code == bad.status_code == 303
    db.refresh(professional)
    assert len(professional.periods) == 2
    assert any(period.weekday == 2 and period.opens_at.isoformat() == "10:00:00" for period in professional.periods)

def test_schedule_period_can_be_edited_by_its_owner(client, db, professional):
    page = client.get("/login")
    import re
    csrf = re.search(r'name="csrf_token" value="([^"]+)', page.text).group(1)
    client.post("/login", data={"email":professional.email,"password":"senha-segura-teste","csrf_token":csrf})
    csrf = re.search(r'name="csrf_token" value="([^"]+)', client.get("/profissional/agenda").text).group(1)
    period = professional.periods[0]
    response = client.post(f"/profissional/horarios/{period.id}", data={"weekday":3,"opens_at":"08:00","closes_at":"12:00","csrf_token":csrf}, follow_redirects=False)
    db.refresh(period)
    assert response.status_code == 303 and period.weekday == 3

def test_schedule_id_from_another_professional_cannot_be_edited(client, db, professional):
    import re
    from app.models import Professional, SchedulePeriod
    from datetime import time
    other = Professional(name="Bia", email="bia@example.com", slug="bia", phone="5511888888888", password_hash=professional.password_hash)
    db.add(other); db.flush()
    period = SchedulePeriod(professional_id=other.id, weekday=2, opens_at=time(9), closes_at=time(17)); db.add(period); db.commit()
    page = client.get("/login")
    csrf = re.search(r'name="csrf_token" value="([^"]+)', page.text).group(1)
    client.post("/login", data={"email":professional.email,"password":"senha-segura-teste","csrf_token":csrf})
    response = client.post(f"/profissional/horarios/{period.id}", data={"weekday":3,"opens_at":"10:00","closes_at":"14:00","csrf_token":csrf}, follow_redirects=False)
    db.refresh(period)
    assert response.status_code == 303 and period.weekday == 2
