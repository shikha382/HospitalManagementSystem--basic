from datetime import datetime, date
from calendar import monthrange
from backend.celery_app import celery
from backend.models import Appointment, Treatment

@celery.task(name="tasks.generate_monthly_reports")
def generate_monthly_reports(year=None, month=None):
    from backend.app import create_app
    from backend.email_utills import send_email
    app = create_app()
    with app.app_context():
        now = datetime.now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month
        # Build start and end dates for the target month
        start_date = date(year, month, 1)
        last_day = monthrange(year, month)[1]
        end_date = date(year, month, last_day)
        month_str = start_date.strftime("%B %Y")

        from backend.models import Doctor
        doctors = Doctor.query.all()
        sent_count = 0
        for doctor in doctors:
            # Filter appointments for the specific month only
            appts = Appointment.query.filter(
                Appointment.doctor_id == doctor.id,
                Appointment.date >= start_date,
                Appointment.date <= end_date
            ).all()
            completed = [a for a in appts if a.status.lower() == 'completed']
            cancelled = [a for a in appts if a.status.lower() == 'cancelled']
            # Build detail rows for all appointments
            appt_list = []
            from collections import Counter
            diagnoses = []
            for a in appts:
                t = Treatment.query.filter_by(appointment_id=a.id).first()
                if t and t.diagnosis:
                    diagnoses.append(t.diagnosis)
                appt_list.append({
                    'date': a.date.strftime('%Y-%m-%d') if a.date else "N/A",
                    'time': a.time.strftime('%H:%M') if a.time else "N/A",
                    'patient_name': a.patient.name if a.patient else "Unknown",
                    'status': a.status.capitalize() if a.status else "N/A",
                    'diagnosis': t.diagnosis if t else "N/A",
                    'prescription': t.prescription if t else "N/A"
                })
            
            top_diagnoses = Counter(diagnoses).most_common(5)
            if doctor.user and doctor.user.email:
                send_email(
                    to_email=doctor.user.email,
                    subject=f"Monthly Activity Report - {month_str}",
                    template_name="report",
                    month=month_str,
                    doctor_name=doctor.name,
                    total_appointments=len(appts),
                    completed_count=len(completed),
                    cancelled_count=len(cancelled),
                    top_diagnoses=top_diagnoses,
                    appointments=appt_list,
                    generated_date=now.strftime("%d %b %Y, %I:%M %p")
                )
                sent_count += 1
        return f"Monthly reports sent to {sent_count}/{len(doctors)} doctors for {month_str}"
