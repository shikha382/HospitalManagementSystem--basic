Jospital Management - Simple
=============================

Technical Requirements Document (TRD)
=====================================

1. System Architecture
----------------------
The system is implemented as a Flask-based backend with the following components:
- Flask API layer with blueprint modules for authentication, admin, doctor, and patient operations.
- SQLite database for persistent storage.
- Redis for caching dashboards and lookup results.
- Celery with Redis broker for asynchronous tasks.
- Email service integration using Flask-Mail for reminders and reports.
- HTML export support for patient treatment histories.

2. Key Services and Components
------------------------------
- backend.app: application factory, blueprint registration, error handling, initialization.
- backend.config: environment-driven settings for database, JWT, Redis, Celery, and email.
- backend.routes.auth: registration, login, current user retrieval.
- backend.routes.admin: doctor/patient management, dashboard, search, manual triggers.
- backend.routes.doctor: appointment management, availability, treatment records, reports.
- backend.routes.patient: profile, booking, appointment lifecycle, history export.
- backend.tasks.reminders: daily appointment reminder emails.
- backend.tasks.reports: monthly doctor activity reports.
- backend.tasks.exports: async patient export and CSV generation.
- backend.cache: cache getters/setters and invalidation utilities.
- backend.models: database ORM entities and relations.

3. Data Flow
------------
- User requests are routed through role-validated REST endpoints.
- JWT tokens supply role-based authorization for protected APIs.
- Caching is applied to admin statistics, doctor statistics, and department listings.
- Updates to doctors, appointments, or patients trigger cache invalidation.
- Celery tasks run outside request flow to send emails and generate exports.

4. API Endpoints
----------------
Category  Endpoint                         Method
--------  --------------------------------  ------
Auth      /api/auth/register               POST
Auth      /api/auth/login                  POST
Auth      /api/auth/me                     GET
Admin     /api/admin/dashboard             GET
Admin     /api/admin/doctors               GET
Admin     /api/admin/doctors               POST
Admin     /api/admin/doctors/<id>          PUT
Admin     /api/admin/doctors/<id>/toggle   PUT
Admin     /api/admin/patients              GET
Admin     /api/admin/patients/<id>         PUT
Admin     /api/admin/patients/<id>/toggle  PUT
Admin     /api/admin/appointments           GET
Admin     /api/admin/search/doctors        GET
Admin     /api/admin/search/patients       GET
Admin     /api/admin/departments           GET
Admin     /api/admin/reminders/trigger     POST
Admin     /api/admin/reports/monthly       POST
Doctor    /api/doctor/dashboard            GET
Doctor    /api/doctor/appointments         GET
Doctor    /api/doctor/appointments/<id>    PUT
Doctor    /api/doctor/availability         GET
Doctor    /api/doctor/availability         POST
Doctor    /api/doctor/treatment            POST
Doctor    /api/doctor/treatment/<id>       PUT
Doctor    /api/doctor/patients/<id>/history GET
Doctor    /api/doctor/report/monthly       GET
Patient   /api/patient/dashboard           GET
Patient   /api/patient/profile             GET
Patient   /api/patient/profile             PUT
Patient   /api/patient/departments         GET
Patient   /api/patient/doctors             GET
Patient   /api/patient/doctors/<id>/availability GET
Patient   /api/patient/appointments        POST
Patient   /api/patient/appointments        GET
Patient   /api/patient/appointments/<id>   DELETE
Patient   /api/patient/treatments          GET
Patient   /api/patient/export              POST
Patient   /api/patient/export/<job_id>/status GET
Patient   /api/patient/export/<filename>/download_direct GET

5. Security Requirements
------------------------
- JWT-based authentication for protected APIs.
- Role-specific decorators ensure access control.
- Input validation on required JSON fields.
- Username and email uniqueness checks.
- Standard error responses for invalid requests.

6. Infrastructure Requirements
------------------------------
- Python 3.8 or newer.
- Flask 3.0.
- SQLite database file stored under /instance.
- Redis server available at redis://localhost:6379/0.
- Celery configured with Redis broker and backend.
- SMTP mail server or local email testing server.

7. Deployment and Runtime
-------------------------
- Start Redis server first.
- Run Flask app through `python -m backend.app`.
- Run Celery worker with `celery -A backend.celery_app worker --loglevel=info --pool=solo`.
- Run Celery beat with `celery -A backend.celery_app beat --loglevel=info`.
- Configure mail credentials through environment variables.

8. Error Handling
-----------------
- 400: Bad request for missing or invalid payload.
- 401: Unauthorized for missing or invalid token.
- 403: Forbidden for role violations.
- 404: Not found for missing resources.
- 500: Internal server error for unexpected failures.

9. Quality and Validation
-------------------------
- Use modular blueprints for separation of concerns.
- Apply cache invalidation after updates to keep dashboard data fresh.
- Keep export generation asynchronous to avoid blocking user requests.
- Maintain patient privacy by enforcing role restrictions on clinical data access.
