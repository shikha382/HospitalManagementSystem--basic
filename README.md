Hospital Management - Simple
=============================

Project Summary
---------------
A modular hospital management portal with role-based workflows for administrators, doctors, and patients. It delivers appointment booking, treatment history management, reminder emails, monthly reporting, and export capabilities.

Key Capabilities
----------------
- Multi-role access and secure JWT authorization
- Admin management of doctors, patients, departments, appointments, and reports
- Doctor scheduling, treatment recording, and activity reporting
- Patient appointment booking, cancellation, profile updates, and record export
- Redis caching for dashboard performance and department lookup
- Celery-driven asynchronous reminders, reports, and exports

Technology Overview
-------------------
| Layer | Technology |
|-------|------------|
| Backend | Flask 3.0 |
| Database | SQLite |
| Cache | Redis |
| Worker | Celery + Redis |
| Email | Flask-Mail |
| Frontend | VueJS 3 (CDN) |
| Styling | Bootstrap 5 |

System Requirements
-------------------
- Python 3.8 or later
- Redis server
- SMTP email credentials or local mail server
- Writable project directory for `instance` and `exports`

Installation
------------
1. Open the project folder:

```powershell
cd c:\Users\shikha\Pictures\Downloads\lmKFZciHil\24f2007_HMS
```

2. Create and activate a Python virtual environment:

```powershell
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Configure environment variables:
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `REDIS_URL`
- `MAIL_SERVER`
- `MAIL_PORT`
- `MAIL_USE_TLS`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `MAIL_DEFAULT_SENDER`

Create a `.env` file or set values in your terminal session.

5. Start the Redis server.

Application Startup
-------------------
1. Start the Flask backend:

```powershell
venv\Scripts\activate
python -m backend.app
```

2. Start the Celery worker in a second terminal:

```powershell
venv\Scripts\activate
celery -A backend.celery_app worker --loglevel=info --pool=solo
```

3. Start Celery beat in a third terminal:

```powershell
venv\Scripts\activate
celery -A backend.celery_app beat --loglevel=info
```

Default Credentials
-------------------
| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |

API Summary
-----------
| Role | Endpoint | Purpose |
|------|----------|---------|
| Auth | `/api/auth/register` | Register patient account |
| Auth | `/api/auth/login` | Login and receive JWT |
| Admin | `/api/admin/dashboard` | Retrieve admin statistics |
| Admin | `/api/admin/doctors` | Manage doctors |
| Doctor | `/api/doctor/availability` | Manage availability |
| Patient | `/api/patient/appointments` | Book or list appointments |

User Workflows
--------------
- Admin: manage doctor and patient records, monitor appointments, trigger workflows.
- Doctor: update availability, manage consultations, add treatment records, download monthly reports.
- Patient: register, book appointments, view history, export treatment reports.

Key Files
---------
- `backend/app.py` - application factory, blueprint registration, error handling
- `backend/config.py` - environment-driven application configuration
- `backend/routes/` - API blueprints for auth, admin, doctor, and patient workflows
- `backend/tasks/` - Celery tasks for reminders, reports, and exports
- `backend/cache/` - Redis cache utilities and invalidation
- `backend/models/__init__.py` - ORM entities and relationships

Operational Notes
-----------------
- Use `--pool=solo` for Windows Celery workers.
- Verify Redis connection and SMTP settings before running background tasks.
- The SQLite file is created in the `instance` folder at first startup.
- Patient exports generate HTML reports under `exports` and attempt to copy to the system Downloads folder.

Troubleshooting
---------------
- `redis.exceptions.ConnectionError`: confirm Redis is running and environment variables are correct.
- `401 Unauthorized`: ensure JWT token is included in API requests.
- Mail delivery issues: verify mail server settings and credentials.
- Export errors: confirm `exports` directory permissions and available disk space.

Future Improvements
-------------------
- Add frontend form validation and session handling.
- Upgrade storage to PostgreSQL for production use.
- Add automated tests for APIs and Celery tasks.
- Improve dashboard reporting and search performance.

- Triggered by patient from dashboard
- Async job that exports treatment history
- Sends email notification when complete

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register patient
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Admin
- `GET /api/admin/dashboard` - Dashboard stats
- `GET /api/admin/doctors` - List doctors
- `POST /api/admin/doctors` - Add doctor
- `PUT /api/admin/doctors/<id>` - Update doctor
- `DELETE /api/admin/doctors/<id>` - Deactivate doctor
- `GET /api/admin/patients` - List patients
- `DELETE /api/admin/patients/<id>` - Deactivate patient
- `GET /api/admin/appointments` - List all appointments
- `GET /api/admin/search/doctors?q=<query>` - Search doctors
- `GET /api/admin/search/patients?q=<query>` - Search patients

### Doctor
- `GET /api/doctor/dashboard` - Dashboard stats
- `GET /api/doctor/appointments` - List appointments
- `PUT /api/doctor/appointments/<id>` - Update appointment
- `GET /api/doctor/availability` - Get availability
- `POST /api/doctor/availability` - Set availability
- `POST /api/doctor/treatment` - Add treatment
- `PUT /api/doctor/treatment/<id>` - Update treatment
- `GET /api/doctor/patients/<id>/history` - Patient history

### Patient
- `GET /api/patient/dashboard` - Dashboard data
- `GET /api/patient/profile` - Get profile
- `PUT /api/patient/profile` - Update profile
- `GET /api/patient/departments` - List departments
- `GET /api/patient/doctors?specialization_id=<id>` - List doctors
- `GET /api/patient/doctors/<id>/availability` - Doctor availability
- `POST /api/patient/appointments` - Book appointment
- `DELETE /api/patient/appointments/<id>` - Cancel appointment
- `GET /api/patient/appointments` - List appointments
- `GET /api/patient/treatments` - Treatment history
- `POST /api/patient/export` - Export CSV

## Database Schema

- **users**: User authentication (admin, doctor, patient)
- **departments**: Medical specializations
- **doctors**: Doctor profiles
- **patients**: Patient profiles
- **appointments**: Appointment bookings
- **treatments**: Treatment records
- **doctor_availability**: Doctor availability slots

## Troubleshooting

### Redis Connection Error
- Ensure Redis server is running
- Check Redis URL in `.env` file

### Email Not Sending
- Verify SMTP credentials in `.env`
- For Gmail, ensure App Password is used
- Check firewall/antivirus settings

### Celery Not Starting
- On Windows, use `--pool=solo` flag
- Ensure Redis is running
- Check Celery broker URL in `.env`

### Database Errors
- Delete `hospital.db` and restart Flask to recreate
- Check file permissions

## Project Structure

```
hospital-management-system/
├── backend/
│   ├── models/          # Database models
│   ├── routes/          # API routes
│   ├── cache/           # Redis caching
│   ├── tasks/           # Celery tasks
│   ├── app.py           # Flask application
│   ├── config.py        # Configuration
│   └── celery_app.py    # Celery setup
├── static/
│   ├── js/
│   │   ├── components/  # Vue components
│   │   └── app.js       # Main Vue app
│   └── css/
│       └── style.css    # Custom styles
├── templates/
│   └── index.html       # Main HTML template
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # This file
```

## License

This project is for educational purposes.

## Support

For issues or questions, please check the troubleshooting section or review the code comments.
