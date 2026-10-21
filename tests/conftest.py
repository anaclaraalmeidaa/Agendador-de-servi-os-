import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.database import get_db
from app.main import app
from app.models import Base, Professional, Service, SchedulePeriod
from app.security import hash_password

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", os.getenv("DATABASE_URL", "postgresql+psycopg://agendador_test:test-only@localhost:5433/agendador_test"))
engine = create_engine(TEST_DATABASE_URL)
TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

@pytest.fixture(scope="session", autouse=True)
def schema():
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gist"))
    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE appointments DROP CONSTRAINT IF EXISTS appointments_no_overlap"))
        conn.execute(text("ALTER TABLE appointments ADD CONSTRAINT appointments_no_overlap EXCLUDE USING gist (professional_id WITH =, tstzrange(starts_at, ends_at, '[)') WITH &&) WHERE (status IN ('confirmed','completed'))"))
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture(autouse=True)
def clean_db():
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE appointments, schedule_periods, services, professionals CASCADE"))

@pytest.fixture
def db():
    session = TestingSession()
    try: yield session
    finally: session.close()

@pytest.fixture
def professional(db):
    p = Professional(name="Ana", email="ana@example.com", slug="ana", phone="5511999999999", password_hash=hash_password("senha-segura-teste"))
    db.add(p); db.flush()
    service = Service(professional_id=p.id, name="Corte", duration_minutes=30)
    db.add(service)
    db.add(SchedulePeriod(professional_id=p.id, weekday=1, opens_at=__import__('datetime').time(9), closes_at=__import__('datetime').time(17)))
    db.commit()
    return p

@pytest.fixture
def client(db):
    def override(): yield db
    app.dependency_overrides[get_db] = override
    with TestClient(app) as test_client: yield test_client
    app.dependency_overrides.clear()
