import os
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://agendador:desenvolvimento-local@localhost:5432/agendador")
SESSION_SECRET = os.getenv("SESSION_SECRET", "dev-only-change-this-secret")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
