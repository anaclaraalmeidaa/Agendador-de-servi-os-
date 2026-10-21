from app.models import Professional, Service

def test_public_profile_lists_active_services(client, professional, db):
    response = client.get("/p/ana")
    assert response.status_code == 200 and "Corte" in response.text and "Agende com Ana" in response.text and "/p/ana/availability" in response.text

def test_unknown_profile_does_not_show_private_data(client, professional):
    response = client.get("/p/nao-existe")
    assert response.status_code == 404 and professional.email not in response.text
