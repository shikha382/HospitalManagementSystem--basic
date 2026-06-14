import csv
import os
from datetime import datetime
from backend.celery_app import celery
from backend.models import db, Appointment, Treatment, Patient, Doctor
EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'exports')
@celery.task(name="tasks.export_csv")
def export_csv_task(patient_id):
    if not os.path.exists(EXPORTS_DIR):
        os.makedirs(EXPORTS_DIR)
    treatments = Treatment.query.join(Appointment).filter(
        Appointment.patient_id == patient_id
    ).all()
    filepath = os.path.join(EXPORTS_DIR, f"patient_{patient_id}.csv")
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Diagnosis', 'Prescription', 'Next Visit'])
        for t in treatments:
            writer.writerow([
                t.appointment.date.isoformat() if t.appointment.date else '',
                t.diagnosis,
                t.prescription,
                t.next_visit_date.isoformat() if t.next_visit_date else ''
            ])
    print(f"CSV export completed: {filepath}")
    return filepath
@celery.task(name="tasks.export_patient_treatments")
def export_patient_treatments(patient_id, email):
    if not os.path.exists(EXPORTS_DIR):
        os.makedirs(EXPORTS_DIR)
    patient = Patient.query.get(patient_id)
    if patient is None:
        print(f"Patient {patient_id} not found")
        return None
    appointments = Appointment.query.filter_by(
        patient_id=patient_id,
        status='completed'
    ).join(Treatment).all()
    from flask import render_template
    from backend.app import create_app
    app = create_app()
    
    # Prepare history list for template
    history = []
    for apt in appointments:
        if apt.treatment:
            doctor = Doctor.query.get(apt.doctor_id)
            history.append({
                'date': apt.date.strftime('%Y-%m-%d') if apt.date else 'N/A',
                'doctor_name': doctor.name if doctor else 'Unknown',
                'specialization': doctor.department.name if doctor and doctor.department else 'N/A',
                'diagnosis': apt.treatment.diagnosis,
                'prescription': apt.treatment.prescription or ''
            })

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = os.path.join(EXPORTS_DIR, f"medical_report_{patient_id}_{timestamp}.html")
    
    with app.app_context():
        html_content = render_template(
            'patient_records.html', 
            history=history, 
            patient_name=patient.name,
            age=patient.age,
            date=datetime.now().strftime('%d %B %Y'),
            year=datetime.now().year
        )
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
    try:
        import shutil
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        if os.path.exists(downloads_path):
            dest_name = os.path.basename(filepath)
            dest_path = os.path.join(downloads_path, dest_name)
            shutil.copy2(filepath, dest_path)
            print(f"✅ Patient history saved to Downloads: {dest_path}")
    except Exception as e:
        print(f"⚠️ Could not copy to Downloads: {e}")
    return filepath

@celery.task(name="tasks.export_appointments_csv")
def export_appointments_csv():
    if not os.path.exists(EXPORTS_DIR):
        os.makedirs(EXPORTS_DIR)
    
    # Use app context to query DB
    from backend.app import create_app
    app = create_app()
    
    with app.app_context():
        appointments = Appointment.query.all()
        filename = f"appointments_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(EXPORTS_DIR, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Patient', 'Doctor', 'Date', 'Time', 'Status'])
            for a in appointments:
                writer.writerow([
                    a.id,
                    a.patient.name if a.patient else 'N/A',
                    a.doctor.name if a.doctor else 'N/A',
                    a.date.strftime('%Y-%m-%d') if a.date else '',
                    a.time.strftime('%H:%M') if a.time else '',
                    a.status
                ])
    
    print(f"CSV export completed: {filepath}")
    return filename
