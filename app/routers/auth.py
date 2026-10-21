from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.csrf import csrf_for, csrf_valid
from app.database import get_db
from app.models import Professional
from app.security import verify_password
from app.templating import templates
router = APIRouter()

@router.get("/login")
def login_page(request: Request): return templates.TemplateResponse(request=request, name="professional/login.html", context={"csrf": csrf_for(request), "message": ""})

@router.post("/login")
def login(request: Request, email: str = Form(), password: str = Form(), csrf_token: str = Form(), db: Session = Depends(get_db)):
    if not csrf_valid(request, csrf_token): return templates.TemplateResponse(request=request, name="professional/login.html", context={"csrf": csrf_for(request), "message": "Formulário expirado. Tente novamente."}, status_code=400)
    pro = db.scalar(select(Professional).where(Professional.email == email.strip().lower()))
    if not pro or not verify_password(password, pro.password_hash): return templates.TemplateResponse(request=request, name="professional/login.html", context={"csrf": csrf_for(request), "message": "E-mail ou senha inválidos."}, status_code=400)
    request.session.clear(); request.session["professional_id"] = str(pro.id)
    return RedirectResponse("/profissional/agenda", status_code=303)

@router.post("/logout")
def logout(request: Request, csrf_token: str = Form()):
    if not csrf_valid(request, csrf_token): return RedirectResponse("/login", status_code=303)
    request.session.clear()
    return RedirectResponse("/", status_code=303)
