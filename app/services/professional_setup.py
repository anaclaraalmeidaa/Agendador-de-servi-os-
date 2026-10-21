from datetime import time
from app.models import Professional, SchedulePeriod, Service

def validate_service(name: str, duration_minutes: int) -> tuple[str, int]:
    clean = name.strip()
    if not clean or len(clean) > 120: raise ValueError("Informe um nome de serviço válido.")
    if isinstance(duration_minutes, bool) or not isinstance(duration_minutes, int) or duration_minutes <= 0: raise ValueError("A duração deve ser maior que zero.")
    return clean, duration_minutes

def validate_period(weekday: int, opens_at: str, closes_at: str) -> tuple[int, time, time]:
    try: opening, closing = time.fromisoformat(opens_at), time.fromisoformat(closes_at)
    except ValueError as exc: raise ValueError("Informe horários válidos.") from exc
    if weekday not in range(1, 8) or closing <= opening: raise ValueError("O dia ou período informado é inválido.")
    return weekday, opening, closing

def create_service(db, professional: Professional, name: str, duration_minutes: int) -> Service:
    clean, duration = validate_service(name, duration_minutes)
    service = Service(professional_id=professional.id, name=clean, duration_minutes=duration)
    db.add(service); db.commit(); return service

def update_service(service: Service, name: str, duration_minutes: int) -> Service:
    clean, duration = validate_service(name, duration_minutes)
    service.name = clean; service.duration_minutes = duration
    return service

def create_period(db, professional: Professional, weekday: int, opens_at: str, closes_at: str) -> SchedulePeriod:
    weekday, opening, closing = validate_period(weekday, opens_at, closes_at)
    period = SchedulePeriod(professional_id=professional.id, weekday=weekday, opens_at=opening, closes_at=closing)
    db.add(period); db.commit(); return period
