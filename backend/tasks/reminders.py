from datetime import date
from backend.celery_app import celery
from backend.models import Appointment
@celery.task(name="tasks.send_daily_reminders")
def send_daily_reminders():
    from backend.app import create_app
    from backend.email_utills import send_email
    app = create_app()
    with app.app_context():
        today = date.today()
        booked = Appointment.query.filter_by(date=today, status="booked").all()
        for a in booked:
            if a.patient and a.patient.user:
                send_email(
                    to_email=a.patient.user.email,
                    subject="Appointment Reminder",
                    template_name="reminder",
                    name=a.patient.name,
                    doctor_name=a.doctor.name if a.doctor else "N/A",
                    date=a.date.strftime('%B %d, %Y'),
                    time=a.time.strftime('%I:%M %p')
                )
        return len(booked)
