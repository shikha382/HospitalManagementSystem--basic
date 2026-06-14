# Hospital Management - Simple

A role-based hospital management system for admins, doctors, and patients. The application handles patient registration, doctor management, appointment booking, treatment records, reminders, reports, exports, and dashboard views through a Flask API and a Vue 3 frontend.

## Project Snapshot

| Area | Details |
| --- | --- |
| Application type | Full-stack hospital management web app |
| Backend | Flask, Flask-SQLAlchemy, Flask-JWT-Extended |
| Frontend | Vue 3 from CDN, Bootstrap 5 |
| Database | SQLite by default |
| Background work | Celery with Redis broker |
| Cache | Redis |
| Authentication | JWT-based role access |
| Roles | Admin, Doctor, Patient |

## Key Features

| Role | Capabilities |
| --- | --- |
| Admin | View dashboard stats, manage doctors, manage patients, view appointments, search users, trigger reminders, generate reports |
| Doctor | View dashboard, manage appointments, set availability, add and update treatment records, view patient history, download monthly reports |
| Patient | Register, log in, browse departments, view doctors, book appointments, cancel appointments, view treatments, export medical history |

## System Modules

| Module | Purpose |
| --- | --- |
| Authentication | Registers patients, logs users in, returns JWT tokens, exposes current profile |
| Admin API | Controls hospital master data and account activation states |
| Doctor API | Supports availability, appointment handling, and treatment records |
| Patient API | Supports booking, profile updates, treatment history, and exports |
| Cache Layer | Stores repeated department, doctor, and dashboard data in Redis |
| Tasks | Sends reminders, creates reports, and exports patient treatment history |

## Documentation

| Document | Description |
| --- | --- |
| [Product Requirements Document](docs/PRD.md) | Product scope, users, requirements, workflows, and acceptance criteria |
| [Technical Requirements Document](docs/TRD.md) | Architecture, stack, schema, APIs, environment, and deployment notes |

## Folder Structure

```text
.
|-- backend/
|   |-- app.py
|   |-- celery_app.py
|   |-- config.py
|   |-- cache/
|   |-- models/
|   |-- routes/
|   `-- tasks/
|-- docs/
|   |-- PRD.md
|   `-- TRD.md
|-- static/
|   |-- images/
|   |-- js/
|   `-- hms1.jpg
|-- templates/
|   |-- email/
|   |-- index.html
|   `-- patient_records.html
|-- .env.example
|-- .gitignore
|-- requirements.txt
|-- trigger_tasks.py
`-- README.md
```

## Prerequisites

| Requirement | Recommended Version |
| --- | --- |
| Python | 3.10 or newer |
| Redis | 6 or newer |
| pip | Latest available |
| SMTP account | Needed for reminder and report emails |

## Setup

1. Create and activate a virtual environment.

```bash
python -m venv venv
venv\Scripts\activate
```

For macOS or Linux:

```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Copy the environment template.

```bash
copy .env.example .env
```

For macOS or Linux:

```bash
cp .env.example .env
```

4. Update `.env` with local values.

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Flask session secret |
| `JWT_SECRET_KEY` | JWT signing secret |
| `DATABASE_URL` | SQLAlchemy database URL |
| `REDIS_URL` | Redis broker and cache URL |
| `MAIL_SERVER` | SMTP host |
| `MAIL_PORT` | SMTP port |
| `MAIL_USERNAME` | SMTP username |
| `MAIL_PASSWORD` | SMTP password or app password |
| `MAIL_DEFAULT_SENDER` | Sender address for email jobs |

5. Start Redis.

```bash
redis-server
```

6. Start the Flask app.

```bash
python -m backend.app
```

The app runs at:

```text
http://localhost:5000
```

## Background Workers

Start the Celery worker in a second terminal:

```bash
celery -A backend.celery_app worker --loglevel=info --pool=solo
```

Start Celery Beat in a third terminal:

```bash
celery -A backend.celery_app beat --loglevel=info
```

The `--pool=solo` option is recommended on Windows.

## Default Login

| Role | Username | Password |
| --- | --- | --- |
| Admin | `admin` | `admin123` |

Change this password before using the application outside a local development environment.

## API Overview

| Area | Endpoint | Method | Purpose |
| --- | --- | --- | --- |
| Auth | `/api/auth/register` | POST | Register a patient |
| Auth | `/api/auth/login` | POST | Login and receive a token |
| Auth | `/api/auth/me` | GET | Get current user profile |
| Admin | `/api/admin/dashboard` | GET | View system stats |
| Admin | `/api/admin/doctors` | GET, POST | List or create doctors |
| Admin | `/api/admin/doctors/<id>` | PUT | Update doctor details |
| Admin | `/api/admin/doctors/<id>/toggle` | PUT | Activate or deactivate doctor |
| Admin | `/api/admin/patients` | GET | List patients |
| Admin | `/api/admin/patients/<id>` | PUT | Update patient details |
| Admin | `/api/admin/patients/<id>/toggle` | PUT | Activate or deactivate patient |
| Admin | `/api/admin/appointments` | GET | View all appointments |
| Admin | `/api/admin/search/doctors` | GET | Search doctors |
| Admin | `/api/admin/search/patients` | GET | Search patients |
| Doctor | `/api/doctor/dashboard` | GET | View doctor dashboard |
| Doctor | `/api/doctor/appointments` | GET | List doctor appointments |
| Doctor | `/api/doctor/appointments/<id>` | PUT | Update appointment status |
| Doctor | `/api/doctor/availability` | GET, POST | View or set availability |
| Doctor | `/api/doctor/treatment` | POST | Add treatment record |
| Doctor | `/api/doctor/treatment/<id>` | PUT | Update treatment record |
| Patient | `/api/patient/dashboard` | GET | View patient dashboard |
| Patient | `/api/patient/profile` | GET, PUT | View or update profile |
| Patient | `/api/patient/departments` | GET | List departments |
| Patient | `/api/patient/doctors` | GET | List doctors |
| Patient | `/api/patient/appointments` | GET, POST | List or book appointments |
| Patient | `/api/patient/appointments/<id>` | DELETE | Cancel appointment |
| Patient | `/api/patient/treatments` | GET | View treatment history |
| Patient | `/api/patient/export` | POST | Export treatment history |

## Database Tables

| Table | Description |
| --- | --- |
| `users` | Login accounts and role metadata |
| `departments` | Medical departments and specializations |
| `doctors` | Doctor profile records |
| `patients` | Patient profile records |
| `appointments` | Appointment bookings and statuses |
| `treatments` | Diagnosis, prescription, notes, and follow-up data |
| `doctor_availability` | Doctor date and time availability |

## Development Notes

| Topic | Note |
| --- | --- |
| Local database | Created automatically in `instance/hospital.db` |
| Runtime exports | Written to `exports/` or local downloads |
| Redis bundle | Do not commit local Redis binaries |
| Secrets | Keep real secrets in `.env` only |
| Public repo | Commit source, docs, templates, static assets, and dependency files only |

## License

This project is intended for educational use.
