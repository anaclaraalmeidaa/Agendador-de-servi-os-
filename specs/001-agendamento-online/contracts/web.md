# Web Contracts: Agendamento Online

The product is a server-rendered website. FastAPI returns complete Jinja pages for ordinary navigation and may return HTML fragments for HTMX requests. HTMX is a progressive enhancement; it does not own validation or business rules. All user-facing text is in Portuguese.

## Public client flow

| Method and path | Input | Success | Failure |
|---|---|---|---|
| `GET /p/{slug}` | Public professional slug | Booking page with active services and date selection | Friendly not-found/empty page without private data |
| `GET /p/{slug}/availability?service_id={id}&date={YYYY-MM-DD}` | Service, local date | Only future starts fitting the service duration and opening periods; full page or HTMX fragment | Clear unavailable/invalid-date response |
| `POST /p/{slug}/appointments` | Form: service, start, client name, phone, CSRF token | Revalidate; persist confirmed booking; redirect to a confirmation page | Invalid form or conflict returns clear Portuguese error and refreshed availability; no duplicate persists |
| `GET /confirmation/{token}` | Opaque, unguessable confirmation token | Confirmation and user-clicked WhatsApp link with prefilled service/date/time message | Safe not-found response; do not reveal client details for invalid tokens |

The WhatsApp action is a normal external click-to-chat link to the professional's supplied number. The app does not send a message or call a WhatsApp API.

## Professional flow

| Method and path | Input | Success | Failure |
|---|---|---|---|
| `GET /professional/login` | None | Login form | — |
| `POST /professional/login` | Login identifier, password, CSRF token | Signed secure session and redirect to agenda | Generic Portuguese authentication error |
| `POST /professional/logout` | CSRF token | Clear session and redirect to login | — |
| `GET/POST /professional/services` | Service name, positive duration, active state; CSRF for mutation | Own service list/create/edit | Validation errors; ownership checks |
| `GET/POST /professional/schedule` | Weekday and one or more opening/closing periods; CSRF for mutation | Own recurring schedule | Validation errors; no invalid or non-positive period |
| `GET /professional/appointments?date={YYYY-MM-DD}` | Local date | Own daily agenda in professional time zone | Invalid date message |
| `POST /professional/appointments/{id}/cancel` | CSRF token | Cancel own appointment with at least two hours remaining; release interval | Refuse if not owned, not confirmed, or less than two hours remain; message in Portuguese |

## HTTP and security behavior

- Mutations use POST; GET requests never change state.
- HTML forms include CSRF tokens. HTMX mutations submit the same token.
- Professional-only routes require a valid session and enforce ownership on every record lookup.
- Session cookies are signed, `HttpOnly`, `SameSite=Lax`, and `Secure` in HTTPS deployments. The cookie contains only a minimal professional identifier; its signing secret comes from environment configuration.
- Successful form mutations use Post/Redirect/Get where appropriate. The database exclusion violation returns an availability conflict, not a generic success.
- Public routes expose no appointment list, client phone, password hash, or professional management data.