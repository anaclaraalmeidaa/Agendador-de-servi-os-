# Implementation Plan: Agendamento Online

**Branch**: `001-agendamento-online` | **Date**: 2026-10-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-agendamento-online/spec.md`; user-selected stack: Python with FastAPI, PostgreSQL in Docker, Jinja, HTMX, pytest; local startup with `docker compose up`; database-enforced appointment exclusivity.

## Summary

Deliver a small server-rendered booking website for one professional per account and public link. FastAPI serves Jinja pages and HTML forms; HTMX enhances availability and form feedback. PostgreSQL stores services, recurring opening periods, and appointments. A partial GiST exclusion constraint using `btree_gist` is the authoritative guard against overlapping appointment intervals for the same professional, including concurrent requests. Docker Compose builds and starts the app and database from one command, while pytest runs against a separate PostgreSQL test service.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, SQLAlchemy 2.x, Alembic, psycopg 3, Jinja2, HTMX (local static asset), pytest, HTTPX/TestClient

**Storage**: PostgreSQL 18; `btree_gist` extension; named volume for local development data

**Testing**: pytest unit and HTTP-flow tests; PostgreSQL integration and concurrent-booking tests via isolated Compose test database

**Target Platform**: Docker Compose on developer machines; browser-based desktop and mobile website

**Project Type**: Server-rendered web application

**Performance Goals**: No throughput or latency target is specified for the initial small-business release. Public availability must reflect reservations and cancellations within the five-second success criterion.

**Constraints**: `docker compose up` starts the website and database; PostgreSQL itself enforces no overlapping blocking appointments per professional; clients do not need accounts; all UI and messages are in Portuguese; secret values are environment-provided and never committed; cancellations require at least two hours' notice; no payments, automatic messaging, or native mobile app.

**Scale/Scope**: One professional per account/link; individual service catalog and weekly opening periods; daily agenda; no production scale target specified.

## Constitution Check

### Before Phase 0

- **Exclusive scheduling**: Pass. The database exclusion constraint is authoritative; the app also rechecks availability and maps conflicts to Portuguese feedback.
- **Website booking without client accounts**: Pass. Booking uses a public page and a name and phone only.
- **Automated quality checks**: Pass. pytest covers business rules and PostgreSQL integration/concurrency behavior.
- **Mobile and Portuguese UX**: Pass. Responsive Jinja templates and Portuguese messages are required; HTMX does not replace usable HTML forms.
- **Simplicity and focus**: Pass. One web application and one database; payments, automated messages, and native apps stay out of scope.
- **Product/security constraints**: Pass. Secrets are environment-provided; README and test coverage are planned.

### Post-design gate

Pass. The design has one application service, one PostgreSQL database, server-rendered HTML, and no additional product capabilities. `btree_gist` is required to express the requested interval invariant in the database; no simpler unique index can enforce variable-length overlap.

## Project Structure

```text
compose.yaml
Dockerfile
.dockerignore
.gitignore
.env.example
README.md
app/
├── __init__.py
├── main.py
├── config.py
├── database.py
├── models.py
├── security.py
├── csrf.py
├── routers/
│   ├── auth.py
│   ├── public_booking.py
│   └── professional.py
├── services/
│   ├── availability.py
│   └── appointments.py
├── templates/
│   ├── base.html
│   ├── public/
│   └── professional/
└── static/
    ├── css/site.css
    └── js/htmx.min.js
migrations/
├── env.py
└── versions/
tests/
├── conftest.py
├── unit/
├── web/
└── integration/
    ├── test_booking_constraints.py
    └── test_concurrent_booking.py
specs/001-agendamento-online/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/web.md
```

**Structure Decision**: One Python web project at repository root. Keep routes, business rules, data access, templates, and static assets in the same app. Alembic migrations are versioned separately. Tests are separated by unit, HTTP, and real-PostgreSQL integration scope. Docker Compose defines the normal app/database stack and an opt-in isolated test database/service.

