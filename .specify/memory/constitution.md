<!--
Sync Impact Report
- Version change: unversioned scaffold → 1.0.0 (initial constitution)
- Modified principles: none; established five principles from the Agendador requirements
- Added sections: Product Constraints; Development Workflow
- Removed sections: none
- Follow-up TODOs: confirm original ratification date
-->
# Agendador Constitution

## Core Principles

### I. Exclusive Scheduling
Each appointment MUST reserve one time slot for one client for the selected
professional. The system MUST reject any attempt to create a second appointment
for that professional at the same time. Availability checks and reservation MUST
preserve this rule even when requests arrive concurrently. This protects the
professional's schedule from conflicts.

### II. Website-Based Booking Without Accounts
All appointments MUST be created through the website. Clients MUST be able to
book without creating an account and MUST only need to provide their name and
telephone number. This keeps booking direct and accessible to occasional clients.

### III. Automated Quality Checks
The project MUST include automated tests for its behavior. Tests MUST cover the
exclusive scheduling rule, including rejection of duplicate appointments for
the same professional and time. Changes to booking behavior MUST be covered by
tests before they are considered complete.

### IV. Mobile Usability and Clear Portuguese
The website MUST be usable on mobile screens. Booking controls, availability,
confirmation, and error messages MUST be understandable in Portuguese. The
interface MUST provide clear feedback when a slot is unavailable or a booking
cannot be completed.

### V. Simplicity and Focus
The project MUST implement only functionality requested for Agendador. New
features and added complexity MUST have a clear connection to the stated
requirements and MUST NOT be introduced speculatively. This keeps the service
straightforward for autonomous professionals and small businesses.

## Product Constraints

- The booking flow MUST collect only the client name and telephone number; an
  account MUST NOT be required.
- Appointment records MUST associate the reserved time with its professional so
  that uniqueness is enforced per professional.
- Credentials, passwords, API keys, and other secret values MUST NOT be committed
  or pushed to GitHub. Secrets MUST be supplied through an appropriate local or
  deployment configuration mechanism.

## Development Workflow

- The repository MUST include a README explaining how to install, configure,
  and use the project.
- Automated tests MUST be run when changes affect application behavior, with
  particular attention to scheduling conflicts.
- Reviews MUST check that changes follow these principles and that no secrets
  are included in tracked files.

## Governance
This constitution governs product and engineering decisions for Agendador.
Amendments MUST be made by editing this document, stating the reason for the
change, and updating the version and last-amended date. Changes to existing
principles or removal of a principle require a MAJOR version increment; new
principles or materially expanded requirements require a MINOR increment;
clarifications and non-semantic edits require a PATCH increment. Contributors
and reviewers MUST check proposed changes against this constitution. Any
exception MUST be documented with its rationale in the relevant change review.

**Version**: 1.0.0 | **Ratified**: 2026-10-19 | **Last Amended**: 2026-10-19

