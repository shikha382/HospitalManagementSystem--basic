from flask import Blueprint, request, jsonify
from backend.models import db, Doctor, Appointment, Treatment, DoctorAvailability, Patient
from backend.routes.utils import doctor_required, get_current_user_id
from backend.cache import get_cache, set_cache, get_doctor_stats_key, invalidate_appointment_cache
from flask_jwt_extended import jwt_required
from datetime import datetime, date, time, timedelta
doctor_bp = Blueprint('doctor', __name__, url_prefix='/api/doctor')
@doctor_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@doctor_required
def get_dashboard():
    user_id = get_current_user_id()
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    if doctor is None:
        return jsonify({'error': 'Doctor not found'}), 404
    cache_key = get_doctor_stats_key(doctor.id)
    cached = get_cache(cache_key)
    if cached:
        return jsonify(cached), 200
    today = date.today()
    week_later = today + timedelta(days=7)
    upcoming = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.date >= today,
        Appointment.date <= week_later,
        Appointment.status == 'booked'
    ).order_by(Appointment.date, Appointment.time).all()
    total_patients = db.session.query(Appointment.patient_id).filter(
        Appointment.doctor_id == doctor.id
    ).distinct().count()
    completed_today = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.date == today,
        Appointment.status == 'completed'
    ).count()
    stats = {
        'doctor': doctor.to_dict(),
        'upcoming_appointments': [a.to_dict() for a in upcoming],
        'total_patients': total_patients,
        'completed_today': completed_today
    }
    set_cache(cache_key, stats, expiry=60)
    return jsonify(stats), 200
@doctor_bp.route('/appointments', methods=['GET'])
@jwt_required()
@doctor_required
def get_appointments():
    user_id = get_current_user_id()
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    if doctor is None:
        return jsonify({'error': 'Doctor not found'}), 404
    status = request.args.get('status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    query = Appointment.query.filter_by(doctor_id=doctor.id)
    if status:
        query = query.filter_by(status=status)
    if date_from:
        query = query.filter(Appointment.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
    if date_to:
        query = query.filter(Appointment.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
    appointments = query.order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    return jsonify([a.to_dict() for a in appointments]), 200
@doctor_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@jwt_required()
@doctor_required
def update_appointment(appointment_id):
    user_id = get_current_user_id()
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    if doctor is None:
        return jsonify({'error': 'Doctor not found'}), 404
    appointment = Appointment.query.get(appointment_id)
    if appointment is None:
        return jsonify({'error': 'Appointment not found'}), 404
    if appointment.doctor_id != doctor.id:
        return jsonify({'error': 'Access denied'}), 403
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    if 'status' in data:
        if data['status'] not in ['completed', 'cancelled']:
            return jsonify({'error': 'Invalid status'}), 400
        appointment.status = data['status']
    if 'notes' in data:
        appointment.notes = data['notes']
    db.session.commit()
    invalidate_appointment_cache()
    return jsonify({'message': 'Appointment updated', 'appointment': appointment.to_dict()}), 200
@doctor_bp.route('/availability', methods=['GET'])
@jwt_required()
@doctor_required
def get_availability():
    user_id = get_current_user_id()
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    if doctor is None:
        return jsonify({'error': 'Doctor not found'}), 404
    today = date.today()
    week_later = today + timedelta(days=7)
    availability = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.date >= today,
        DoctorAvailability.date <= week_later
    ).order_by(DoctorAvailability.date).all()
    return jsonify([a.to_dict() for a in availability]), 200
@doctor_bp.route('/availability', methods=['POST'])
@jwt_required()
@doctor_required
def set_availability():
    user_id = get_current_user_id()
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    if doctor is None:
        return jsonify({'error': 'Doctor not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    if 'availability' not in data:
        return jsonify({'error': 'Missing availability data'}), 400
    if not isinstance(data['availability'], list):
        return jsonify({'error': 'Invalid format'}), 400
    today = date.today()
    week_later = today + timedelta(days=7)
    DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.date >= today,
        DoctorAvailability.date <= week_later
    ).delete()
    for item in data['availability']:
        if 'date' not in item or 'start_time' not in item or 'end_time' not in item:
            continue
        new_availability = DoctorAvailability(
            doctor_id=doctor.id,
            date=datetime.strptime(item['date'], '%Y-%m-%d').date(),
            start_time=datetime.strptime(item['start_time'], '%H:%M').time(),
            end_time=datetime.strptime(item['end_time'], '%H:%M').time(),
            is_available=item.get('is_available', True)
        )
        db.session.add(new_availability)
    db.session.commit()
    return jsonify({'message': 'Availability updated'}), 200
@doctor_bp.route('/treatment', methods=['POST'])
@jwt_required()
@doctor_required
def add_treatment():
    user_id = get_current_user_id()
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    if doctor is None:
        return jsonify({'error': 'Doctor not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    if 'appointment_id' not in data:
        return jsonify({'error': 'Missing appointment_id'}), 400
    if 'diagnosis' not in data:
        return jsonify({'error': 'Missing diagnosis'}), 400
    appointment = Appointment.query.get(data['appointment_id'])
    if appointment is None:
        return jsonify({'error': 'Appointment not found'}), 404
    if appointment.doctor_id != doctor.id:
        return jsonify({'error': 'Access denied'}), 403
    if appointment.treatment:
        return jsonify({'error': 'Treatment already exists'}), 400
    next_visit = None
    if data.get('next_visit_date'):
        next_visit = datetime.strptime(data['next_visit_date'], '%Y-%m-%d').date()
    new_treatment = Treatment(
        appointment_id=data['appointment_id'],
        diagnosis=data['diagnosis'],
        prescription=data.get('prescription', ''),
        notes=data.get('notes', ''),
        next_visit_date=next_visit
    )
    db.session.add(new_treatment)
    appointment.status = 'completed'
    db.session.commit()
    invalidate_appointment_cache()
    return jsonify({'message': 'Treatment added', 'treatment': new_treatment.to_dict()}), 201
@doctor_bp.route('/treatment/<int:treatment_id>', methods=['PUT'])
@jwt_required()
@doctor_required
def update_treatment(treatment_id):
    user_id = get_current_user_id()
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    if doctor is None:
        return jsonify({'error': 'Doctor not found'}), 404
    treatment = Treatment.query.get(treatment_id)
    if treatment is None:
        return jsonify({'error': 'Treatment not found'}), 404
    if treatment.appointment.doctor_id != doctor.id:
        return jsonify({'error': 'Access denied'}), 403
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    if 'diagnosis' in data:
        treatment.diagnosis = data['diagnosis']
    if 'prescription' in data:
        treatment.prescription = data['prescription']
    if 'notes' in data:
        treatment.notes = data['notes']
    if 'next_visit_date' in data:
        if data['next_visit_date']:
            treatment.next_visit_date = datetime.strptime(data['next_visit_date'], '%Y-%m-%d').date()
        else:
            treatment.next_visit_date = None
    db.session.commit()
    return jsonify({'message': 'Treatment updated', 'treatment': treatment.to_dict()}), 200
@doctor_bp.route('/patients/<int:patient_id>/history', methods=['GET'])
@jwt_required()
@doctor_required
def get_patient_history(patient_id):
    user_id = get_current_user_id()
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    if doctor is None:
        return jsonify({'error': 'Doctor not found'}), 404
    patient = Patient.query.get(patient_id)
    if patient is None:
        return jsonify({'error': 'Patient not found'}), 404
    appointments = Appointment.query.filter_by(
        patient_id=patient_id,
        status='completed'
    ).order_by(Appointment.date.desc()).all()
    history = []
    for a in appointments:
        record = a.to_dict()
        if a.treatment:
            record['treatment'] = a.treatment.to_dict()
        history.append(record)
    return jsonify(history), 200
@doctor_bp.route('/report/monthly', methods=['GET'])
@jwt_required()
@doctor_required
def download_monthly_report():
    import io
    from flask import send_file
    user_id = get_current_user_id()
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    if doctor is None:
        return jsonify({'error': 'Doctor not found'}), 404
    today = date.today()
    month = today.month
    year = today.year
    month_name = today.strftime('%B')
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.date >= start_date,
        Appointment.date < end_date
    ).all()
    total_appointments = len(appointments)
    completed = sum(1 for a in appointments if a.status == 'completed')
    cancelled = sum(1 for a in appointments if a.status == 'cancelled')
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Monthly Report - {month_name} {year}</title></head>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Monthly Activity Report - {doctor.name}</h2>
        <p><strong>Month:</strong> {month_name} {year}</p>
        <p><strong>Total Appointments:</strong> {total_appointments}</p>
        <p><strong>Completed:</strong> {completed}</p>
        <p><strong>Cancelled:</strong> {cancelled}</p>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color:
                <th>Date</th>
                <th>Patient Name</th>
                <th>Status</th>
                <th>Diagnosis</th>
                <th>Prescription</th>
            </tr>
    """
    for apt in appointments:
        pname = apt.patient.name if apt.patient else 'Unknown'
        t = apt.treatment
        diagnosis = t.diagnosis if t else "N/A"
        prescription = t.prescription if t else "N/A"
        
        html += f"""
            <tr>
                <td>{apt.date.strftime('%Y-%m-%d')}</td>
                <td>{pname}</td>
                <td>{apt.status.capitalize()}</td>
                <td>{diagnosis}</td>
                <td>{prescription}</td>
            </tr>
        """
    html += """
        </table>
    </body>
    </html>
    """
    mem = io.BytesIO()
    mem.write(html.encode('utf-8'))
    mem.seek(0)
    filename = f"Report_{doctor.name.replace(' ', '_')}_{month_name}_{year}.html"
    return send_file(
        mem,
        mimetype='text/html',
        as_attachment=True,
        download_name=filename
    )
