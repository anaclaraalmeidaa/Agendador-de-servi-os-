import uuid
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, ForeignKeyConstraint, Integer, String, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
class Base(DeclarativeBase): pass
class Professional(Base):
    __tablename__ = "professionals"
    __table_args__ = (CheckConstraint("length(trim(name)) > 0", name="ck_professional_name_nonempty"), CheckConstraint("length(trim(email)) > 0", name="ck_professional_email_nonempty"), CheckConstraint("length(trim(slug)) > 0", name="ck_professional_slug_nonempty"))
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=False, default="")
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="America/Sao_Paulo")
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    services: Mapped[list["Service"]] = relationship(back_populates="professional", cascade="all, delete-orphan")
    periods: Mapped[list["SchedulePeriod"]] = relationship(back_populates="professional", cascade="all, delete-orphan")
class Service(Base):
    __tablename__ = "services"
    __table_args__ = (UniqueConstraint("id", "professional_id", name="uq_service_owner"), CheckConstraint("duration_minutes > 0", name="ck_service_duration_positive"), CheckConstraint("length(trim(name)) > 0", name="ck_service_name_nonempty"))
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    professional_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("professionals.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    professional: Mapped[Professional] = relationship(back_populates="services")
class SchedulePeriod(Base):
    __tablename__ = "schedule_periods"
    __table_args__ = (CheckConstraint("weekday BETWEEN 1 AND 7", name="ck_period_weekday"), CheckConstraint("closes_at > opens_at", name="ck_period_hours"))
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    professional_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("professionals.id", ondelete="CASCADE"), nullable=False)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)
    opens_at: Mapped[object] = mapped_column(Time, nullable=False)
    closes_at: Mapped[object] = mapped_column(Time, nullable=False)
    professional: Mapped[Professional] = relationship(back_populates="periods")
class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (ForeignKeyConstraint(["service_id", "professional_id"], ["services.id", "services.professional_id"], name="fk_appointment_service_owner"), CheckConstraint("ends_at > starts_at", name="ck_appointment_interval"), CheckConstraint("duration_minutes > 0", name="ck_appointment_duration"), CheckConstraint("length(trim(client_name)) > 0", name="ck_appointment_client_name"), CheckConstraint("status IN ('confirmed','cancelled','completed')", name="ck_appointment_status"))
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    professional_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("professionals.id", ondelete="CASCADE"), nullable=False)
    service_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    starts_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    service_name: Mapped[str] = mapped_column(String(120), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    client_name: Mapped[str] = mapped_column(String(120), nullable=False)
    client_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    confirmation_token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, default=lambda: uuid.uuid4().hex)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="confirmed")
    cancelled_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))
