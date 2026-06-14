# Product Requirements Document

## Product Overview

Hospital Management - Simple is a lightweight hospital management system that helps a small clinic or academic demo environment manage doctors, patients, appointments, treatment records, reminders, and reports from one web interface.

| Item | Details |
| --- | --- |
| Product name | Hospital Management - Simple |
| Product type | Role-based hospital management web app |
| Primary users | Admins, doctors, patients |
| Platform | Browser-based |
| Primary goal | Reduce manual coordination for appointments, patient records, and reporting |

## Goals

| Goal | Description | Success Measure |
| --- | --- | --- |
| Centralize workflows | Keep doctor, patient, appointment, and treatment data in one app | Users can complete core flows without external spreadsheets |
| Support role clarity | Show each user only the tools relevant to their role | Admin, doctor, and patient dashboards have separate access rules |
| Improve appointment handling | Let patients book available slots and doctors manage outcomes | Booked, completed, cancelled, and expired states are tracked |
| Make reporting easier | Provide reminders, monthly reports, and patient exports | Reports and exports can be generated from system data |
| Keep setup simple | Use SQLite, Redis, Flask, and Vue from CDN for straightforward local deployment | A developer can run the app locally with documented steps |

## User Personas

| Persona | Needs | Main Actions |
| --- | --- | --- |
| Hospital Admin | Manage staff, patients, departments, and hospital-level appointment visibility | Add doctors, update users, view stats, trigger reports |
| Doctor | Know upcoming appointments and record treatment outcomes | Set availability, complete visits, add diagnosis and prescriptions |
| Patient | Find doctors and manage appointments | Register, book slots, cancel bookings, view history, export records |

## User Stories

| ID | User Story | Priority |
| --- | --- | --- |
| PRD-001 | As a patient, I want to register and log in so I can book appointments. | High |
| PRD-002 | As a patient, I want to browse departments and doctors so I can choose the right specialist. | High |
| PRD-003 | As a patient, I want to book only available slots so double booking is avoided. | High |
| PRD-004 | As a patient, I want to cancel an upcoming appointment if I cannot attend. | Medium |
| PRD-005 | As a patient, I want to view treatment history so I can remember previous diagnoses and prescriptions. | High |
| PRD-006 | As a doctor, I want to set availability so patients can book valid slots. | High |
| PRD-007 | As a doctor, I want to mark appointments completed or cancelled so schedules stay accurate. | High |
| PRD-008 | As a doctor, I want to add treatment details so patient records are complete. | High |
| PRD-009 | As an admin, I want to add and update doctors so staffing data stays current. | High |
| PRD-010 | As an admin, I want to activate or deactivate accounts so access can be controlled. | High |
| PRD-011 | As an admin, I want dashboard statistics so I can monitor hospital activity. | Medium |
| PRD-012 | As a user, I want reminders and reports so important hospital updates are not missed. | Medium |

## Functional Requirements

| ID | Requirement | Priority | Current Status |
| --- | --- | --- | --- |
| FR-001 | Patient registration with username, email, password, and profile details | High | Implemented |
| FR-002 | JWT login for admin, doctor, and patient roles | High | Implemented |
| FR-003 | Role-protected API routes | High | Implemented |
| FR-004 | Admin dashboard statistics | Medium | Implemented |
| FR-005 | Doctor creation and updates by admin | High | Implemented |
| FR-006 | Patient listing and updates by admin | Medium | Implemented |
| FR-007 | Department listing | High | Implemented |
| FR-008 | Doctor availability management | High | Implemented |
| FR-009 | Patient appointment booking | High | Implemented |
| FR-010 | Appointment status updates | High | Implemented |
| FR-011 | Treatment record creation and updates | High | Implemented |
| FR-012 | Patient treatment history | High | Implemented |
| FR-013 | Patient export workflow | Medium | Implemented |
| FR-014 | Daily reminder workflow | Medium | Implemented |
| FR-015 | Monthly doctor report workflow | Medium | Implemented |

## Non-Functional Requirements

| Category | Requirement |
| --- | --- |
| Security | JWT-protected APIs, role checks, password hashing, secrets stored in environment variables |
| Performance | Redis caching for repeated dashboard and lookup data |
| Reliability | SQLite auto-creation for local development and defensive API error responses |
| Maintainability | Separate modules for routes, models, cache, tasks, templates, and static assets |
| Portability | Runs locally on Windows, macOS, or Linux with Python and Redis |
| Privacy | Runtime database, exports, logs, and secrets must not be committed to the public repository |

## Core Workflows

| Workflow | Steps | Outcome |
| --- | --- | --- |
| Patient books appointment | Register or login, browse department, choose doctor, view availability, book slot | Appointment is saved as `booked` |
| Doctor completes visit | Login, view appointments, add treatment, mark complete | Treatment record is linked to appointment |
| Admin adds doctor | Login, create doctor account and profile, assign department | Doctor can log in and set availability |
| Patient exports history | Login, request export, download generated file | Treatment history is available outside the app |
| Scheduled communication | Celery Beat triggers reminder or report task | Email content is generated and sent through SMTP |

## Acceptance Criteria

| ID | Criteria |
| --- | --- |
| AC-001 | A patient can register, log in, and see a patient dashboard. |
| AC-002 | An admin can create a doctor and assign the doctor to a department. |
| AC-003 | A doctor can set availability for upcoming dates. |
| AC-004 | A patient cannot book a past appointment. |
| AC-005 | A patient cannot book an already reserved active slot. |
| AC-006 | A doctor can create one treatment record per appointment. |
| AC-007 | A patient can view completed treatment history. |
| AC-008 | Runtime files such as `instance/`, `exports/`, `.env`, and `__pycache__/` are excluded from git. |

## Out of Scope

| Item | Reason |
| --- | --- |
| Payment billing | Not required for the simple management scope |
| Insurance claim processing | Requires external integrations and compliance scope |
| Multi-branch hospital support | Current schema targets one clinic or hospital instance |
| Real-time chat | Not part of appointment and records flow |
| Production-grade audit logs | Useful later, but outside the current simple implementation |

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Default admin password used outside development | Unauthorized access | Document that it must be changed before real use |
| SQLite limitations under high traffic | Concurrency issues | Use SQLite locally, migrate to PostgreSQL for production |
| Redis unavailable | Cache and background jobs fail | Keep Redis setup documented and fail gracefully where possible |
| Email credentials misconfigured | Reminders and reports fail | Use `.env.example` and setup notes |
| Sensitive generated files committed | Privacy issue | Maintain `.gitignore` and commit only source/docs/assets |
