Jospital Management - Simple
=============================

Project Requirements Framework (PRF)
===================================

1. Project Overview
-------------------
A web-based Hospital Management System with multi-role support for admins, doctors, and patients. It provides secure access, appointment management, medical history tracking, notifications, and reporting.

2. Stakeholders
---------------
- Admin: manages doctors, patients, departments, and system monitoring.
- Doctor: manages schedules, appointments, treatments, and reports.
- Patient: registers, books appointments, reviews treatment history, and exports health records.
- System Operator: deploys and maintains backend, background jobs, and email services.

3. Objectives
-------------
- Provide a centralized hospital management portal for patient appointments, doctor schedules, and administrative tasks.
- Reduce manual coordination by automating patient reminders and monthly doctor reports.
- Ensure data accuracy with role-based access control and fast lookups via Redis caching.
- Enable secure exports of patient treatment histories and reporting data.

4. Functional Requirements
--------------------------
4.1 Authentication and Authorization
- Register patient accounts.
- Support login for admin, doctor, and patient roles.
- Enforce JWT authorization for protected endpoints.
- Provide role-restricted APIs for admin, doctors, and patients.

4.2 Admin Module
- Admin dashboard with doctor, patient, and appointment statistics.
- Add, update, and deactivate doctors.
- Manage patients and review their records.
- Search doctors and patients by name, specialization, ID, or contact.
- Trigger reminder and monthly report workflows manually.

4.3 Doctor Module
- Doctor dashboard with upcoming appointments and completed counts.
- View and update appointment status.
- Set availability for the next 7 days.
- Add and edit treatment records.
- Download monthly doctor activity reports.
- Review patient medical history.

4.4 Patient Module
- Patient dashboard with upcoming appointments and last treatment summary.
- Browse departments and active doctors.
- Book, view, and cancel appointments.
- Retrieve doctor availability for a 7-day window.
- Export treatment history as HTML or CSV.

4.5 Background Jobs and Notifications
- Daily reminders for booked appointments.
- Monthly reports emailed to doctors.
- Asynchronous export of patient treatment history.

5. Nonfunctional Requirements
-----------------------------
- Deployment: Flask backend, SQLite database, Redis cache, Celery workers.
- Performance: use Redis for cacheable admin and doctor statistics.
- Reliability: standard error handling for API requests and authentication failures.
- Usability: role-specific dashboards and RESTful API design.
- Maintainability: structured blueprint modules and reusable helper utilities.

6. Success Criteria
-------------------
- Admin can manage user roles and monitor appointments.
- Doctors can maintain availability and capture treatment data.
- Patients can book appointments and export their history.
- Reminder and report jobs run successfully with email dispatch.

7. Constraints
-------------
- Uses SQLite for application database.
- Requires Redis for caching and Celery broker/back end.
- Requires configured SMTP to send email notifications.

8. Key Data Entities
--------------------
- User: credentials, role, account status.
- Doctor: specialist profile, schedule, contact.
- Patient: demographic profile, medical history.
- Appointment: doctor-patient booking, status, notes.
- Treatment: diagnosis, prescription, follow-up recommendations.
- Department: medical specialization categories.
