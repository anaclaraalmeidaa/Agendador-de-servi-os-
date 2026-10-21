import getpass, os, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import select
from app.database import SessionLocal
from app.models import Professional
from app.security import hash_password

def main():
    name = os.getenv("PROFESSIONAL_NAME") or input("Nome: ").strip()
    email = (os.getenv("PROFESSIONAL_EMAIL") or input("E-mail: ")).strip().lower()
    slug = (os.getenv("PROFESSIONAL_SLUG") or input("Link (slug): ")).strip().lower()
    phone = (os.getenv("PROFESSIONAL_PHONE") or input("Telefone WhatsApp com DDI: ")).strip()
    password = os.getenv("PROFESSIONAL_PASSWORD") or getpass.getpass("Senha: ")
    if not name or not re.fullmatch(r"[a-z0-9-]{3,80}", slug) or len(password) < 12:
        sys.exit("Informe nome, slug simples e uma senha com pelo menos 12 caracteres.")
    with SessionLocal() as db:
        if db.scalar(select(Professional).where((Professional.email == email) | (Professional.slug == slug))): sys.exit("E-mail ou link já cadastrado.")
        db.add(Professional(name=name, email=email, slug=slug, phone=phone, password_hash=hash_password(password)))
        db.commit()
    print(f"Profissional criado. Link: {os.getenv('BASE_URL', 'http://localhost:8000').rstrip('/')}/p/{slug}")
if __name__ == "__main__": main()
