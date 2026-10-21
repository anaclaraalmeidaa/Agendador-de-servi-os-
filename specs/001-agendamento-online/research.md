# Research: Agendamento Online

## Decisions

### PostgreSQL booking conflict enforcement
- **Decision**: PostgreSQL owns the no-overlap invariant through an exclusion constraint. Enable `btree_gist`; compare `professional_id WITH =` and the appointment range `tstzrange(starts_at, ends_at, '[)') WITH &&`. Apply the constraint only to blocking states (`confirmed`, `completed`) so a canceled appointment releases its time.
- **Rationale**: The constraint is checked by the database for concurrent transactions, so correctness does not depend on a prior availability read or a single application process. The half-open range permits adjacent appointments. `UNIQUE(professional_id, starts_at)` would not detect overlaps with different start times.
- **Application behavior**: Availability is advisory. On insert conflict, roll back, map the known exclusion constraint violation to a friendly Portuguese message, and return the client to the available slots. Other database errors remain server errors and are not mislabeled as conflicts.
- **Migration implications**: Install `btree_gist` before creating the exclusion constraint. If appointments already exist at rollout, check for overlapping blocking rows before applying the constraint.
- **Sources**: [PostgreSQL range types and exclusion examples](https://www.postgresql.org/docs/18/rangetypes.html); [CREATE TABLE / EXCLUDE](https://www.postgresql.org/docs/18/sql-createtable.html); [btree_gist](https://www.postgresql.org/docs/18/btree-gist.html).

### Web application and forms
- **Decision**: Use FastAPI with server-rendered Jinja2 pages and ordinary HTML forms. Use HTMX for partial refreshes of availability and form feedback, while retaining a complete-page response path for the same actions.
- **Rationale**: This uses the requested simple web stack without introducing a separate frontend build or client-side state layer. HTMX remains a progressive enhancement; the server validates every action.
- **Security**: Keep state-changing actions on POST. Protect professional sessions with secure cookie settings and CSRF tokens on mutating forms, including HTMX requests. Session cookies contain only a minimal professional identifier and are signed with a secret supplied by the environment. Client booking remains account-free.
- **Sources**: [FastAPI templates](https://fastapi.tiangolo.com/advanced/templates/); [FastAPI form data](https://fastapi.tiangolo.com/tutorial/request-forms/); [HTMX documentation](https://htmx.org/docs/); [Starlette SessionMiddleware](https://www.starlette.io/middleware/#sessionmiddleware); [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html).

### Compose startup and persistence
- **Decision**: One `compose.yaml` defines the web service and PostgreSQL. `docker compose up` is the documented local startup command. Compose waits for PostgreSQL's `pg_isready` healthcheck before starting the web service. A named volume persists the development database.
- **Rationale**: Container start order alone does not mean PostgreSQL is ready. Health-based dependency avoids a startup race. A named volume keeps local data across container recreation.
- **Testing**: Define a separate, opt-in test service and test database so pytest never mutates development data. Run it as a one-off Compose service. The database exclusion rule itself must be exercised on real PostgreSQL, not SQLite.
- **Sources**: [Compose startup order and service_healthy](https://docs.docker.com/compose/how-tos/startup-order); [Compose services and healthcheck](https://docs.docker.com/reference/compose-file/services/); [Compose volumes](https://docs.docker.com/reference/compose-file/volumes/); [Compose run](https://docs.docker.com/reference/cli/docker/compose/run/).

### Test approach
- **Decision**: Use pytest for unit, HTTP-flow, and PostgreSQL integration tests. Use FastAPI's `TestClient` for route and rendered HTML behavior; use a Compose-managed test PostgreSQL instance for database constraints and concurrent booking tests.
- **Rationale**: FastAPI documents direct pytest integration with `TestClient`; the specific range constraint requires the actual PostgreSQL engine to validate.
- **Sources**: [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/).

## Alternatives considered

- **Application-only availability checks**: Rejected because concurrent requests can both pass a read check before either writes.
- **Unique professional/start-time index**: Rejected because it misses overlapping intervals with different start times.
- **SQLite for all tests**: Rejected because it cannot validate PostgreSQL GiST exclusion behavior.
- **Separate JavaScript frontend and JSON API**: Rejected because it adds an unrequested build and client-state layer to a small server-rendered site.
- **Start the web container when PostgreSQL is merely running**: Rejected because PostgreSQL may still be initializing; use `service_healthy`.

## Working assumptions

- Use Python 3.12 for a stable supported baseline and PostgreSQL 18 for the database engine.
- Use synchronous SQLAlchemy 2.x with psycopg 3 for the server-rendered request flow; no requirement needs asynchronous database access.
- Migrations run before the web process starts. The Compose database healthcheck completes before migrations begin.
- Local Compose defaults are explicitly development-only. Production secrets must be supplied through environment configuration and excluded from Git.
- Professional account provisioning is assumed to exist before login; a public account-registration flow is not added without an explicit requirement.