# Technical Requirements Document

## Technical Overview

Hospital Management - Simple is a Flask application serving JSON APIs and a Vue 3 browser interface. SQLite stores application data, Redis supports caching and Celery task brokering, and SMTP is used for reminder and report emails.

| Category | Technology |
| --- | --- |
| Language | Python |
| Backend framework | Flask |
| ORM | Flask-SQLAlchemy |
| Auth | Flask-JWT-Extended |
| Frontend | Vue 3, Bootstrap 5 |
| Database | SQLite |
| Cache | Redis |
| Background jobs | Celery |
| Email | Flask-Mail |

## Architecture

```text
Browser
  |
  | HTTP
  v
Flask app
  |-- Auth routes
  |-- Admin routes
  |-- Doctor routes
  |-- Patient routes
  |
  | SQLAlchemy
  v
SQLite database

Flask app
  |
  | cache and broker
  v
Redis
  |
  v
Celery worker and Celery Beat
  |
  v
SMTP email service and export files
```

## Runtime Components

| Component | Responsibility | Main Files |
| --- | --- | --- |
| App factory | Initializes Flask, CORS, JWT, Mail, database, and blueprints | `backend/app.py` |
| Configuration | Reads environment variables and sets defaults | `backend/config.py` |
| Models | Defines SQLAlchemy tables and serialization helpers | `backend/models/__init__.py` |
| Auth API | Handles registration, login, and current user lookup | `backend/routes/auth.py` |
| Admin API | Handles doctor, patient, department, search, dashboard, and report admin flows | `backend/routes/admin.py` |
| Doctor API | Handles appointments, availability, treatment, and monthly report download | `backend/routes/doctor.py` |
| Patient API | Handles dashboards, profiles, booking, treatment history, and exports | `backend/routes/patient.py` |
| Cache helpers | Wraps Redis reads, writes, and invalidation | `backend/cache/` |
| Tasks | Handles reminders, reports, and exports | `backend/tasks/` |

## Environment Variables

| Variable | Required | Default | Notes |
| --- | --- | --- | --- |
| `SECRET_KEY` | Yes for production | `dev-secret-key` | Flask secret |
| `JWT_SECRET_KEY` | Yes for production | `jwt-secret-key` | JWT signing key |
| `DATABASE_URL` | No | SQLite in `instance/hospital.db` | SQLAlchemy URL |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Cache, broker, and result backend |
| `CACHE_EXPIRY` | No | `300` | Cache TTL in seconds |
| `MAIL_SERVER` | No | `localhost` | SMTP host |
| `MAIL_PORT` | No | `1025` | SMTP port |
| `MAIL_USE_TLS` | No | `False` | Set to `True` for TLS |
| `MAIL_USERNAME` | Depends on SMTP | Empty | SMTP username |
| `MAIL_PASSWORD` | Depends on SMTP | Empty | SMTP password |
| `MAIL_DEFAULT_SENDER` | No | `noreply@hospital.com` | Sender address |

## Database Design

| Table | Key Columns | Relationships |
| --- | --- | --- |
| `users` | `id`, `username`, `email`, `password_hash`, `role`, `active` | One-to-one with doctor or patient |
| `departments` | `id`, `name`, `description` | One-to-many with doctors |
| `doctors` | `id`, `user_id`, `name`, `specialization_id`, `experience`, `qualification`, `contact` | Belongs to user and department |
| `patients` | `id`, `user_id`, `name`, `age`, `gender`, `contact`, `address`, `medical_history` | Belongs to user |
| `appointments` | `id`, `patient_id`, `doctor_id`, `date`, `time`, `status`, `notes` | Links patient and doctor |
| `treatments` | `id`, `appointment_id`, `diagnosis`, `prescription`, `notes`, `next_visit_date` | One-to-one with appointment |
| `doctor_availability` | `id`, `doctor_id`, `date`, `start_time`, `end_time`, `is_available` | Belongs to doctor |

## Data Rules

| Rule | Implementation |
| --- | --- |
| Usernames are unique | `users.username` unique constraint |
| Emails are unique | `users.email` unique constraint |
| One doctor slot cannot be double booked | Unique appointment constraint on doctor, date, and time |
| Appointment status is controlled | App uses `booked`, `completed`, `cancelled`, and `expired` states |
| Patient cannot book past dates | Checked in patient booking route |
| Doctor treatment belongs to own appointment | Checked in doctor treatment routes |

## API Security

| Control | Details |
| --- | --- |
| Authentication | JWT access tokens returned from `/api/auth/login` |
| Authorization | Route decorators enforce admin, doctor, and patient roles |
| Password storage | Werkzeug password hashing |
| Cross-origin access | Flask-CORS enabled for browser access |
| Secrets | Read from environment variables |

## API Groups

| Group | Prefix | Access |
| --- | --- | --- |
| Authentication | `/api/auth` | Public for register/login, protected for profile |
| Admin | `/api/admin` | Admin only |
| Doctor | `/api/doctor` | Doctor only |
| Patient | `/api/patient` | Patient only, with limited admin department access |

## Background Jobs

| Job | Trigger | Purpose |
| --- | --- | --- |
| Daily reminders | Celery Beat or admin trigger | Email patients with upcoming appointments |
| Monthly reports | Celery Beat or admin trigger | Generate doctor activity reports |
| Patient export | Patient request | Export treatment history and notify patient |

## Local Development Commands

| Task | Command |
| --- | --- |
| Install dependencies | `pip install -r requirements.txt` |
| Run app | `python -m backend.app` |
| Run worker on Windows | `celery -A backend.celery_app worker --loglevel=info --pool=solo` |
| Run beat | `celery -A backend.celery_app beat --loglevel=info` |

## Repository Hygiene

| File or Folder | Commit Status | Reason |
| --- | --- | --- |
| `backend/` | Commit | Application source |
| `static/` | Commit | Frontend scripts and images |
| `templates/` | Commit | HTML templates |
| `docs/` | Commit | PRD and TRD |
| `.env.example` | Commit | Safe configuration template |
| `.env` | Ignore | Contains secrets |
| `instance/` | Ignore | Runtime database |
| `exports/` | Ignore | Generated patient/report files |
| `__pycache__/` | Ignore | Python bytecode |
| `redis_win/` | Ignore | Local third-party binary bundle |

## Deployment Notes

| Concern | Recommendation |
| --- | --- |
| Database | Use SQLite for local/demo use and PostgreSQL for production |
| Secrets | Set strong `SECRET_KEY` and `JWT_SECRET_KEY` in environment variables |
| Redis | Run managed Redis or a supervised Redis service |
| Email | Use an SMTP provider with app-specific credentials |
| Workers | Run Flask, Celery worker, Celery Beat, Redis, and database as separate services |
| Admin password | Change the default admin password before any public or shared deployment |

## Known Technical Debt

| Item | Suggested Improvement |
| --- | --- |
| No formal migrations | Add Flask-Migrate or Alembic before schema changes become frequent |
| SQLite default | Add production database instructions for PostgreSQL |
| Synchronous export path exists | Use Celery result tracking consistently for large exports |
| Limited automated tests | Add route tests for auth, booking, treatment, and role access |
