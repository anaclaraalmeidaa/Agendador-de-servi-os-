# Tasks: Agendamento Online

**Input**: Design documents from `/specs/001-agendamento-online/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/web.md`, `quickstart.md`

**Tests**: Included because the feature specification and project requirements explicitly require automated pytest coverage, especially for scheduling conflicts.

**Organization**: Tasks are grouped by the four user stories in `spec.md`. All task lines use the required checkbox, sequential ID, optional parallel marker, story label where applicable, and concrete file path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the Python web project and the one-command Compose environment.

- [X] T001 Create `pyproject.toml` with Python 3.12 metadata and runtime dependencies FastAPI, SQLAlchemy 2.x, Alembic, psycopg 3, Jinja2, python-multipart, and pytest/HTTPX test dependencies.
- [X] T002 [P] Create `Dockerfile` and `.dockerignore` to build the single Python web application image from the project root.
- [X] T003 [P] Create `compose.yaml` with the `web` and PostgreSQL 18 `db` services, database `pg_isready` healthcheck, `web` dependency on `service_healthy`, a named development data volume, and an opt-in isolated `tests`/`test-db` profile; make `docker compose up` build and start the site.
- [X] T004 [P] Create `.env.example` with development-only placeholders and `.gitignore` rules that exclude `.env`, local credentials, caches, and test artifacts.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Provide shared configuration, database, schema, authentication, and test infrastructure before user-story work.

- [X] T005 Create `app/__init__.py`, `app/config.py`, `app/database.py`, and `app/main.py` with environment-based settings, SQLAlchemy connection/session lifecycle, FastAPI initialization, and Jinja/static mounts.
- [X] T006 [P] Configure Alembic in `alembic.ini` and `migrations/env.py` to use the application settings and SQLAlchemy metadata.
- [X] T007 Create `app/models.py` for Professional, Service, SchedulePeriod, and Appointment using the data-model fields and constraints; require non-empty professional email/name/slug and service name, positive integer `duration_minutes`, weekday values 1–7, `closes_at > opens_at`, `ends_at > starts_at`, and appointment duration snapshots.
- [X] T008 Create the initial Alembic migration in `migrations/versions/` for the four core entities, foreign keys, unique professional email/slug, service-to-professional ownership, positive duration/time checks, and appointment status values `confirmed`, `cancelled`, and `completed`.
- [X] T009 [P] Create `tests/conftest.py` and `pytest.ini` with pytest configuration, a dedicated test database URL, transaction/session fixtures, and a real PostgreSQL fixture; do not use SQLite for PostgreSQL constraint tests.
- [X] T010 Create `app/security.py` and `app/csrf.py` with signed professional sessions, secure cookie settings, password-hash verification, and CSRF token creation/validation for all state-changing forms, including HTMX requests.
- [X] T011 Create `docker/entrypoint.sh` and update `compose.yaml` so the web service applies Alembic migrations after PostgreSQL is healthy and before starting the FastAPI server; keep all credentials and session signing keys in environment configuration.
- [X] T012 Create `scripts/create_professional.py` to provision the initial professional account from interactive or environment-provided credentials without storing plaintext passwords or committing secrets.

**Checkpoint**: The stack starts with `docker compose up`; migrations and the test harness are ready for all stories.

---

## Phase 3: User Story 1 - Publicar serviços e horários (Priority: P1)

**Goal**: Let one professional manage services and recurring opening periods and obtain the public booking link.

**Independent Test**: Authenticate a provisioned professional, create a service and weekly schedule, and verify the public page shows the active service and the stable link.

### Tests for User Story 1

- [X] T013 [P] [US1] Add pytest unit tests in `tests/unit/test_professional_setup.py` for required non-empty service names, positive integer duration, weekdays 1–7, and opening periods with `closes_at > opens_at`.
- [X] T014 [P] [US1] Add pytest HTTP tests in `tests/web/test_professional_services.py` for authenticated service create/edit, invalid-form messages in Portuguese, and rejection of another professional's service IDs.
- [X] T015 [P] [US1] Add pytest HTTP tests in `tests/web/test_professional_schedule.py` for schedule create/edit, invalid periods, and ownership enforcement.
- [X] T016 [P] [US1] Add pytest HTTP tests in `tests/web/test_public_profile.py` for the public slug page, active-service listing, stable shareable link, and safe empty/unknown profile states.

### Implementation for User Story 1

- [X] T017 [US1] Implement professional login/logout routes with CSRF-protected forms and Portuguese feedback in `app/routers/auth.py` and `app/templates/professional/login.html`.
- [X] T018 [US1] Implement service create/edit and per-professional ownership validation in `app/services/professional_setup.py` and `app/routers/professional.py`, preserving the positive integer duration and non-empty name rules.
- [X] T019 [US1] Implement recurring schedule period create/edit and validation in `app/services/professional_setup.py` and `app/routers/professional.py`, preserving weekday 1–7 and `closes_at > opens_at`.
- [X] T020 [US1] Create Portuguese Jinja templates for the professional service and schedule forms in `app/templates/professional/services.html` and `app/templates/professional/schedule.html`, with mobile-friendly controls and HTMX-enhanced feedback.
- [X] T021 [US1] Implement the public profile route and service listing in `app/routers/public_booking.py` and `app/templates/public/profile.html`, using a stable `/p/{slug}` link and exposing no private agenda or client data.

**Checkpoint**: US1 can be demonstrated without implementing booking: the professional configures services/hours and shares the public page.

---

## Phase 4: User Story 2 - Reservar um horário disponível (Priority: P1)

**Goal**: Let an unauthenticated client see valid availability and book without an account while PostgreSQL prevents overlapping bookings.

**Independent Test**: Use a real PostgreSQL test database to confirm valid booking, reject past/out-of-hours/conflicting requests, accept adjacent intervals and distinct professionals, release canceled intervals, and prove exactly one of two concurrent overlapping inserts commits.

### Tests for User Story 2

- [X] T022 [P] [US2] Add PostgreSQL integration tests in `tests/integration/test_booking_constraints.py` for the GiST exclusion rule: overlapping `confirmed` intervals for one professional conflict; `[start, end)` adjacent intervals and equal intervals for different professionals succeed; canceled rows do not block; completed rows remain blocking.
- [X] T023 [P] [US2] Add concurrent PostgreSQL transaction tests in `tests/integration/test_concurrent_booking.py` proving only one overlapping booking for the same professional commits and the losing request receives the named exclusion violation.
- [X] T024 [P] [US2] Add pytest unit tests in `tests/unit/test_availability.py` for starts advancing by the selected service's duration from each opening period, full-duration fit before close, future-only starts, and local-time handling.
- [X] T025 [P] [US2] Add pytest HTTP tests in `tests/web/test_public_booking.py` for service/date selection, name-and-phone-only booking, invalid input, past/out-of-hours rejection, refreshed availability, and clear Portuguese conflict feedback.

### Implementation for User Story 2

- [X] T026 [US2] Add an Alembic migration in `migrations/versions/` that enables `btree_gist` and adds the partial `EXCLUDE USING gist` constraint on professional equality and `tstzrange(starts_at, ends_at, '[)')` overlap for `confirmed` and `completed` appointments.
- [X] T027 [US2] Implement availability generation in `app/services/availability.py` using each service duration as the start-time increment and the professional's IANA time zone; return only future intervals fully contained in an opening period and not overlapping blocking appointments.
- [X] T028 [US2] Implement booking validation and persistence in `app/services/appointments.py`, snapshotting service name/duration and rechecking the slot inside the write transaction while treating the database exclusion constraint as authoritative.
- [X] T029 [US2] Implement public availability and booking form routes in `app/routers/public_booking.py`, including ordinary full-page and HTMX fragment responses, CSRF validation, and conflict mapping only for the named exclusion constraint.
- [X] T030 [US2] Create Jinja public availability, booking, validation-error, and confirmation templates in `app/templates/public/availability.html`, `app/templates/public/booking_form.html`, and `app/templates/public/confirmation.html` with Portuguese messages and mobile layouts.
- [X] T031 [US2] Add booking transaction rollback and user-safe error handling in `app/services/appointments.py` so a failed conflict leaves no partial appointment and other database failures are not mislabeled as availability conflicts.

**Checkpoint**: US2 is the core booking MVP when combined with US1; database constraints prove no overlapping booking can be committed under concurrency.

---

## Phase 5: User Story 3 - Consultar e cancelar agendamentos (Priority: P2)

**Goal**: Let the professional see their daily agenda and cancel their own appointments at least two hours before start.

**Independent Test**: View one local-date agenda, cancel an owned appointment at exactly two hours and earlier, confirm release, and verify cancellation at less than two hours is refused.

### Tests for User Story 3

- [X] T032 [P] [US3] Add pytest unit tests in `tests/unit/test_cancellation.py` for the exact cancellation boundary: two hours or more is allowed; less than two hours is refused; successful cancellation sets `cancelled_at` and releases the slot.
- [X] T033 [P] [US3] Add pytest HTTP tests in `tests/web/test_professional_agenda.py` for local-date agenda filtering, Portuguese appointment details, cross-account access rejection, and CSRF-protected cancellation.
- [X] T034 [P] [US3] Add integration tests in `tests/integration/test_cancellation_releases_slot.py` proving a canceled interval no longer conflicts in PostgreSQL and the public availability page shows it as free within 5 seconds.

### Implementation for User Story 3

- [X] T035 [US3] Implement professional-local-date agenda queries and ownership filtering in `app/services/appointments.py` and `app/routers/professional.py`.
- [X] T036 [US3] Implement cancellation eligibility and state transition in `app/services/appointments.py`: allow only the owning professional, only a confirmed booking, and only when at least two hours remain; store `cancelled_at` and translate the below-limit case into a Portuguese message.
- [X] T037 [US3] Create the daily agenda and cancellation confirmation/error templates in `app/templates/professional/agenda.html` and `app/templates/professional/cancel_result.html`, with responsive layout and clear local date/time.

**Checkpoint**: US3 can be tested independently against seeded professional and appointment data after the shared database foundation.

---

## Phase 6: User Story 4 - Abrir conversa no WhatsApp após confirmar (Priority: P2)

**Goal**: Show a user-initiated WhatsApp link after booking with the professional's contact and a prefilled service/date/time message.

**Independent Test**: Confirm a booking and verify the rendered WhatsApp link targets the professional and URL-encodes service, local date, and time without sending a message.

### Tests for User Story 4

- [X] T038 [P] [US4] Add pytest unit tests in `tests/unit/test_whatsapp_link.py` for destination formatting and URL-encoding of service name, local date, and appointment time.
- [X] T039 [P] [US4] Add pytest HTTP/template tests in `tests/web/test_confirmation.py` for the confirmation page link, safe invalid confirmation IDs, and confirmation that no outbound message is sent.

### Implementation for User Story 4

- [X] T040 [US4] Implement a WhatsApp click-to-chat URL builder in `app/services/whatsapp.py` using the professional's configured number and the encoded appointment summary; do not call an external API.
- [X] T041 [US4] Render the user-clicked WhatsApp action in `app/templates/public/confirmation.html` and keep confirmation lookup free of client PII for invalid or unknown identifiers.

**Checkpoint**: US4 adds a voluntary contact action after booking and does not change booking success if WhatsApp cannot open.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Complete project documentation and run the end-to-end acceptance path.

- [X] T042 [P] Create `README.md` with install/configure/use instructions, professional provisioning, exact `docker compose up` startup, test command, and secret-handling guidance.
- [X] T043 [P] Add responsive base styles, accessible form labels, focus states, and Portuguese shared messages in `app/templates/base.html` and `app/static/css/site.css`.
- [X] T044 [P] Add the pinned local HTMX asset and its license notice in `app/static/js/htmx.min.js` and `app/static/js/README.md`.
- [X] T045 Review `compose.yaml`, `.env.example`, `.gitignore`, and `README.md` to confirm no real passwords/keys are tracked and that production secret configuration is documented.
- [X] T046 Execute the scenarios from `specs/001-agendamento-online/quickstart.md` and record the verified startup, mobile booking, cancellation boundary, and concurrent PostgreSQL conflict outcomes in `README.md`.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; creates the Python package and Compose services.
- **Foundational (Phase 2)**: Depends on setup; blocks all story work by providing database, migrations, session/CSRF, and test fixtures.
- **US1 (Phase 3, P1)**: Depends on the foundation; creates the professional's services, schedule, login, and public page.
- **US2 (Phase 4, P1)**: Depends on the foundation and US1's professional/service/schedule entities; this is the first end-to-end booking increment.
- **US3 (Phase 5, P2)**: Depends on appointment persistence from US2.
- **US4 (Phase 6, P2)**: Depends on booking confirmation from US2 and the professional WhatsApp number from US1.
- **Polish (Phase 7)**: Depends on all stories selected for the release.

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2; independently delivers configuration and a shareable public professional page.
- **US2 (P1)**: Starts after Phase 2 but needs US1's service and schedule records for a usable end-to-end flow. Its core booking service can be developed against fixtures; MVP release requires US1 + US2.
- **US3 (P2)**: Requires US2's Appointment model and persistence.
- **US4 (P2)**: Requires US2's successful booking confirmation and US1's professional WhatsApp contact.

### Parallel Opportunities

- Setup tasks T002–T004 can proceed in parallel in separate files.
- Foundational tasks T006 and T009 can proceed in parallel after package setup; entity/migration tasks follow them.
- Within US1, independent unit/HTTP test files T013–T016 can be drafted in parallel after fixtures exist.
- Within US2, constraint, concurrency, availability, and route test files T022–T025 can be drafted in parallel; database integration tests require the PostgreSQL test service.
- Within US3 and US4, test files are separate and can be developed in parallel after shared fixtures and booking persistence exist.
- US3 and US4 can proceed in parallel after US2 is complete because they touch separate service/template areas.

## Parallel Example: User Story 2

```text
Task T022: PostgreSQL exclusion-constraint tests in tests/integration/test_booking_constraints.py
Task T023: Concurrent insert tests in tests/integration/test_concurrent_booking.py
Task T024: Availability-generation tests in tests/unit/test_availability.py
Task T025: Public booking HTTP tests in tests/web/test_public_booking.py
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete US1 so a professional can create the service and opening periods.
3. Complete US2, including the database exclusion migration and PostgreSQL concurrency tests.
4. Validate the MVP using the first two user journeys in `quickstart.md`. US1 alone is not a usable booking product; the MVP is US1 + US2.

### Incremental Delivery

1. Deliver the configured public page and booking flow (US1 + US2).
2. Add professional daily agenda and two-hour cancellation (US3).
3. Add the user-initiated WhatsApp confirmation link (US4).
4. Complete cross-cutting documentation, secret review, and quickstart acceptance.

### Parallel Team Strategy

Complete setup and foundation together. Once US2 is complete, separate contributors can implement US3 cancellation/agenda and US4 WhatsApp confirmation in parallel, coordinating only through the shared appointment and confirmation contract.

## Notes

- Every task line uses a markdown checkbox, sequential task ID, optional parallel marker, required story label in story phases, and a concrete file path.
- `[P]` is used only where file ownership is independent and the task has no unfinished prerequisite.
- Booking availability checks improve user feedback, but only the PostgreSQL exclusion constraint guarantees the no-overlap invariant.
- The feature remains a single server-rendered app; no separate frontend project, payments, automatic messages, or native app are introduced.





