import re
from app.models import Professional
from app.security import hash_password

def signed_in(client, db, pro):
    page = client.get("/login")
    csrf = re.search(r'name="csrf_token" value="([^"]+)', page.text).group(1)
    response = client.post("/login", data={"email":pro.email,"password":"senha-segura-teste","csrf_token":csrf}, follow_redirects=False)
    assert response.status_code == 303
    dashboard = client.get("/profissional/agenda")
    return re.search(r'name="csrf_token" value="([^"]+)', dashboard.text).group(1)

def test_professional_can_add_service(client, db, professional):
    csrf = signed_in(client, db, professional)
    response = client.post("/profissional/servicos", data={"name":"Barba","duration_minutes":20,"csrf_token":csrf}, follow_redirects=False)
    assert response.status_code == 303
    assert "Barba" in client.get("/profissional/agenda").text

def test_professional_can_edit_owned_service(client, db, professional):
    from app.models import Service
    service = db.query(Service).filter_by(professional_id=professional.id).one()
    csrf = signed_in(client, db, professional)
    response = client.post(f"/profissional/servicos/{service.id}", data={"name":"Corte premium","duration_minutes":45,"csrf_token":csrf}, follow_redirects=False)
    db.refresh(service)
    assert response.status_code == 303 and service.name == "Corte premium" and service.duration_minutes == 45

def test_service_id_from_another_professional_is_rejected(client, db, professional):
    from app.models import Service
    other = Professional(name="Outra", email="outra@example.com", slug="outra", phone="5511888888888", password_hash=hash_password("x"))
    db.add(other); db.flush(); service = Service(professional_id=other.id, name="Privado", duration_minutes=30); db.add(service); db.commit()
    csrf = signed_in(client, db, professional)
    result = client.post(f"/profissional/servicos/{service.id}", data={"name":"Alterado","duration_minutes":40,"csrf_token":csrf}, follow_redirects=False)
    assert result.status_code == 303
    assert service.name == "Privado"

def test_invalid_service_form_shows_portuguese_feedback(client, db, professional):
    csrf = signed_in(client, db, professional)
    client.post("/profissional/servicos", data={"name":"   ","duration_minutes":0,"csrf_token":csrf}, follow_redirects=False)
    response = client.get("/profissional/agenda?erro=servico")
    assert "Confira o nome e a duração" in response.text
