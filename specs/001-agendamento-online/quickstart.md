# Quickstart: Agendamento Online

## Prerequisites

- Docker Engine or Docker Desktop with the Compose plugin.
- A browser.

## Start the site

From the repository root, run:

```sh
docker compose up
```

Compose builds and starts the FastAPI website and PostgreSQL. The website waits for PostgreSQL's healthcheck, applies database migrations, then becomes available at `http://localhost:8000`. Local development values are defaults only; production secrets must be supplied outside Git.

## Validate the main flows

1. Sign in as a provisioned professional.
2. Create a service with a name and positive duration.
3. Define a weekly schedule period in the professional's local time zone.
4. Copy the public link and open it in a private browser window.
5. Choose a service and confirm that offered starts advance by that service's duration and that the entire service fits before closing time.
6. Book a future slot with only a name and telephone number. Confirm the success page and the WhatsApp link with a prefilled message.
7. Open the professional's daily agenda. Cancel a booking with at least two hours remaining and confirm that the slot is released. Verify a booking with less than two hours remaining cannot be canceled; exactly two hours remains eligible.
8. Open a second browser session and attempt a conflicting booking. The database must reject overlap even if both clients observed the slot as free earlier.

## Run automated tests

Run tests in the isolated Compose test service and test database:

```sh
docker compose run --rm tests
```

The test suite uses pytest. It includes direct PostgreSQL integration cases for overlapping ranges, adjacent ranges, different professionals, canceled bookings, and concurrent attempts. It also exercises form validation, past/out-of-hours rejection, the two-hour cancellation boundary, access ownership, and Portuguese messages.

## Stop the site

Press `Ctrl+C` in the Compose terminal. To stop and remove containers while keeping local database data:

```sh
docker compose down
```

The named development database volume persists until explicitly removed. Test database storage is separate and disposable.