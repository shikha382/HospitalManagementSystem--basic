Product Requirements Document (PRD)
===================================

Project purpose
---------------
Build a lightweight hospital management application that enables administrators, doctors, and patients to coordinate appointments, manage treatment history, and automate email-based reminders and reports.

Target users
------------
- Admin: oversee doctor and patient records, control access, and monitor system activity.
- Doctor: manage schedules, record treatment details, and receive monthly performance summaries.
- Patient: book appointments, view medical history, and export treatment reports.

Key outcomes
------------
- Provide a simple workflow for appointment booking and scheduling.
- Reduce manual follow-up with automated appointment reminders.
- Centralize clinical history and export options for patient records.
- Keep the application minimal and easy to deploy using Flask, SQLite, Redis, and Celery.

Critical features
-----------------
- Role-based login for admin, doctor, and patient users.
- Secure JWT-protected APIs with role-specific access.
- Doctor availability scheduling for the next 7 days.
- Patient appointment booking, cancellation, and history retrieval.
- Treatment recording and patient history exports.
- Daily reminder emails for appointments and monthly activity reports for doctors.

Success metrics
---------------
- Admin can add, update, and deactivate doctors and patients.
- Doctors can manage appointment status and treatment records.
- Patients can successfully book, cancel, and export appointments and history.
- Email reminders and reports generate reliably through background jobs.

Scope and constraints
---------------------
- Use SQLite for local storage and Redis for caching and task queuing.
- No external frontend build process required; the interface uses VueJS CDN components.
- The product should remain simple and maintainable for a small deployment.

Out of scope
------------
- Advanced analytics or multi-tenant hospital support.
- Production-grade database clustering or horizontal scaling.
- Native mobile applications.
