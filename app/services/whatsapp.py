from urllib.parse import quote

def whatsapp_url(phone: str, message: str) -> str:
    digits = "".join(character for character in phone if character.isdigit())
    if not digits: raise ValueError("O profissional não cadastrou um telefone válido para WhatsApp.")
    return f"https://wa.me/{digits}?text={quote(message)}"
