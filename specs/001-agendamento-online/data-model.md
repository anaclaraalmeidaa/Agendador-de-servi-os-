# Data Model: Agendamento Online

## Professional

Represents the single professional served by one account and public link.

- `id`: UUID primary key.
- `email`: required login identifier; unique after normalization.
- `password_hash`: required password hash; never plaintext.
- `display_name`: required public name.
- `slug`: required unique public URL identifier.
- `whatsapp_phone`: required destination number for the confirmation link.
- `timezone`: required IANA time-zone name used to display and interpret local schedules.
- `created_at`: timestamp with time zone.

**Rules**: A professional may manage only their own services, schedule periods, and appointments. Public lookup by slug exposes only active services and public availability, not credentials or appointment contact details.

## Service

Represents one service offered by a professional.

- `id`: UUID primary key.
- `professional_id`: required foreign key to Professional.
- `name`: required, non-empty service name.
- `duration_minutes`: required positive integer.
- `active`: required boolean; inactive services cannot be newly booked.
- `created_at`, `updated_at`: timestamps with time zone.

**Rules**: Service IDs are scoped to their professional. An appointment stores a snapshot of the service name and duration so later edits do not change an existing reservation's display or occupied interval.

## SchedulePeriod

Represents one recurring local-time opening period.

- `id`: UUID primary key.
- `professional_id`: required foreign key to Professional.
- `weekday`: required ISO weekday integer from 1 (Monday) through 7 (Sunday).
- `opens_at`: required local time.
- `closes_at`: required local time later than `opens_at` on the same local day.

**Rules**: A period must be positive in length. Offer service starts from `opens_at` at increments equal to the selected service duration; the complete service interval must fit before `closes_at`. Multiple periods on one weekday represent breaks. Store and interpret recurring hours in the professional's IANA time zone.

## Appointment

Represents a confirmed or canceled client booking.

- `id`: UUID primary key.
- `professional_id`: required foreign key to Professional.
- `service_id`: required foreign key to Service, scoped to the same professional.
- `service_name_snapshot`: required non-empty name at booking time.
- `service_duration_minutes`: required positive integer snapshot.
- `client_name`: required non-empty name.
- `client_phone`: required phone number.
- `starts_at`: required timestamp with time zone.
- `ends_at`: required timestamp with time zone and strictly later than `starts_at`.
- `status`: required enum `confirmed`, `cancelled`, or `completed`.
- `created_at`: required timestamp with time zone.
- `cancelled_at`: nullable timestamp with time zone; set when cancellation succeeds.

**Rules**:
- `ends_at` equals `starts_at` plus the stored service duration.
- Booking start must be in the future and the full interval must fit a schedule period. Validate at request time and again in the booking transaction.
- A professional can cancel only their own confirmed appointment and only when `starts_at - current_time >= 2 hours`. Exactly two hours qualifies. A successful cancel changes status and releases the interval.
- The database MUST enforce no overlap for blocking appointments, independent of application checks. Enable `btree_gist` and add a partial GiST exclusion constraint over `(professional_id WITH =, tstzrange(starts_at, ends_at, '[)') WITH &&)` for `status IN ('confirmed', 'completed')`. The half-open range allows an appointment to start exactly when another ends. Canceled rows do not block.
- Add database checks for positive service duration and `ends_at > starts_at`; use a composite foreign key or equivalent constraint to ensure `service_id` belongs to `professional_id`.
- The exclusion constraint is the final authority for concurrent inserts/updates. The application maps only its named violation to the booking-conflict response.

## Relationships and lifecycle

- Professional 1-to-many Service.
- Professional 1-to-many SchedulePeriod.
- Professional 1-to-many Appointment.
- Service 1-to-many Appointment; appointment snapshots preserve historical service details.
- Appointment state: `confirmed` → `cancelled` (only at least two hours before start), or `confirmed` → `completed` after service time. Canceled appointments release the slot; confirmed and completed records remain blocking in the database constraint.