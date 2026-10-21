from urllib.parse import unquote, urlparse, parse_qs
from app.services.whatsapp import whatsapp_url

def test_whatsapp_link_uses_contact_and_encoded_summary():
    link = whatsapp_url("+55 (11) 99999-0000", "Corte: 19/10/2026 às 10:30")
    parsed = urlparse(link)
    assert parsed.netloc == "wa.me" and parsed.path == "/5511999990000"
    assert parse_qs(parsed.query)["text"][0] == "Corte: 19/10/2026 às 10:30"
