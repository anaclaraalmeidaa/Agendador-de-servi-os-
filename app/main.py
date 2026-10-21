from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.config import SESSION_COOKIE_SECURE, SESSION_SECRET
from app.routers import auth, professional, public_booking

app = FastAPI(title="Agendador")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET, same_site="lax", https_only=SESSION_COOKIE_SECURE)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
from app.templating import templates
app.include_router(auth.router)
app.include_router(professional.router)
app.include_router(public_booking.router)

@app.get("/", response_class=HTMLResponse)
def home(request: Request): return templates.TemplateResponse(request=request, name="home.html", context={})
