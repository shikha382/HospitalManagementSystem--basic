from flask import Blueprint, request, jsonify
from backend.models import db, User, Doctor, Patient, Appointment, Treatment, Department, DoctorAvailability
from backend.routes.utils import role_required, patient_required, get_current_user_id
from backend.cache import get_cache, set_cache, get_departments_cache_key
from flask_jwt_extended import jwt_required
from datetime import datetime, date, timedelta
import os
patient_bp = Blueprint('patient', __name__, url_prefix='/api/patient')
@patient_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@patient_required
def get_dashboard():
    user_id = get_current_user_id()
    patient = Patient.query.filter_by(user_id=user_id).first()
    if patient is None:
        return jsonify({'error': 'Patient not found'}), 404
    today = date.today()

    # Auto-expire past booked appointments globally beforehand
    expired_appts = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.date < today,
        Appointment.status == 'booked'
    ).all()
    if expired_appts:
        for a in expired_appts:
            a.status = 'expired'
        db.session.commit()

    upcoming = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.date >= today,
        Appointment.status == 'booked'
    ).order_by(Appointment.date, Appointment.time).all()
    last_appointment = Appointment.query.filter_by(
        patient_id=patient.id,
        status='completed'
    ).order_by(Appointment.date.desc(), Appointment.time.desc()).first()
    last_treatment = None
    if last_appointment and last_appointment.treatment:
        last_treatment = last_appointment.treatment.to_dict()
        last_treatment['doctor_name'] = last_appointment.doctor.name
        last_treatment['date'] = last_appointment.date.isoformat()
    stats = {
        'patient': patient.to_dict(),
        'upcoming_appointments': [apt.to_dict() for apt in upcoming],
        'last_treatment': last_treatment,
        'total_appointments': Appointment.query.filter_by(patient_id=patient.id).count()
    }
    return jsonify(stats), 200
@patient_bp.route('/profile', methods=['GET'])
@jwt_required()
@patient_required
def get_profile():
    user_id = get_current_user_id()
    patient = Patient.query.filter_by(user_id=user_id).first()
    if patient is None:
        return jsonify({'error': 'Patient not found'}), 404
    return jsonify(patient.to_dict()), 200
@patient_bp.route('/profile', methods=['PUT'])
@jwt_required()
@patient_required
def update_profile():
    user_id = get_current_user_id()
    patient = Patient.query.filter_by(user_id=user_id).first()
    if patient is None:
        return jsonify({'error': 'Patient not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    update_fields = ['name', 'age', 'gender', 'contact', 'address', 'medical_history']
    for field in update_fields:
        if field in data:
            setattr(patient, field, data[field])
    db.session.commit()
    return jsonify({'message': 'Profile updated', 'patient': patient.to_dict()}), 200
@patient_bp.route('/departments', methods=['GET'])
@jwt_required()
@role_required('patient', 'admin')
def get_departments():
    cache_key = get_departments_cache_key()
    cached = get_cache(cache_key)
    if cached:
        return jsonify(cached), 200
    departments = Department.query.all()
    data = [d.to_dict() for d in departments]
    set_cache(cache_key, data)
    return jsonify(data), 200
@patient_bp.route('/doctors', methods=['GET'])
@jwt_required()
@patient_required
def get_doctors():
    spec_id = request.args.get('specialization_id')
    query = Doctor.query.join(User).filter(User.active == True)
    if spec_id:
        query = query.filter(Doctor.specialization_id == spec_id)
    doctors = query.all()
    return jsonify([d.to_dict() for d in doctors]), 200
@patient_bp.route('/doctors/<int:doctor_id>/availability', methods=['GET'])
@jwt_required()
@patient_required
def get_doctor_availability(doctor_id):
    today = date.today()
    end_date = today + timedelta(days=7)
    availability = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor_id,
        DoctorAvailability.date >= today,
        DoctorAvailability.date <= end_date,
        DoctorAvailability.is_available == True
    ).order_by(DoctorAvailability.date, DoctorAvailability.start_time).all()
    booked_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date >= today,
        Appointment.date <= end_date,
        Appointment.status != 'cancelled'
    ).all()
    booked_slots = [{'date': a.date.isoformat(), 'time': a.time.strftime('%H:%M')} for a in booked_appointments]
    return jsonify({
        'availability': [a.to_dict() for a in availability],
        'booked_slots': booked_slots
    }), 200
@patient_bp.route('/appointments', methods=['POST'])
@jwt_required()
@patient_required
def book_appointment():
    user_id = get_current_user_id()
    patient = Patient.query.filter_by(user_id=user_id).first()
    if patient is None:
        return jsonify({'error': 'Patient not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    required_fields = ['doctor_id', 'date', 'time']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing: {field}'}), 400
    appointment_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    
    # Prevent booking in the past
    if appointment_date < date.today():
        return jsonify({'error': 'Cannot book an appointment in the past'}), 400

    time_str = data['time']
    if len(time_str) == 8:
        appointment_time = datetime.strptime(time_str, '%H:%M:%S').time()
    else:
        appointment_time = datetime.strptime(time_str, '%H:%M').time()
    existing = Appointment.query.filter_by(
        doctor_id=data['doctor_id'],
        date=appointment_date,
        time=appointment_time
    ).first()
    if existing and existing.status != 'cancelled':
        return jsonify({'error': 'Slot already booked'}), 400
    new_appointment = Appointment(
        patient_id=patient.id,
        doctor_id=data['doctor_id'],
        date=appointment_date,
        time=appointment_time,
        notes=data.get('notes', ''),
        status='booked'
    )
    db.session.add(new_appointment)
    db.session.commit()
    from backend.cache import invalidate_appointment_cache
    invalidate_appointment_cache()
    return jsonify({'message': 'Appointment booked', 'appointment': new_appointment.to_dict()}), 201
@patient_bp.route('/appointments', methods=['GET'])
@jwt_required()
@patient_required
def get_appointments():
    user_id = get_current_user_id()
    patient = Patient.query.filter_by(user_id=user_id).first()
    if patient is None:
        return jsonify({'error': 'Patient not found'}), 404
    appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(
        Appointment.date.desc(),
        Appointment.time.desc()
    ).all()

    # Auto-expire past appointments
    today = date.today()
    changed = False
    for a in appointments:
        if a.status == 'booked' and a.date < today:
            a.status = 'expired'
            changed = True
    
    if changed:
        db.session.commit()

    return jsonify([a.to_dict() for a in appointments]), 200
@patient_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@jwt_required()
@patient_required
def cancel_appointment(appointment_id):
    user_id = get_current_user_id()
    patient = Patient.query.filter_by(user_id=user_id).first()
    if patient is None:
        return jsonify({'error': 'Patient not found'}), 404
    appointment = Appointment.query.get(appointment_id)
    if appointment is None:
        return jsonify({'error': 'Appointment not found'}), 404
    if appointment.patient_id != patient.id:
        return jsonify({'error': 'Access denied'}), 403
    if appointment.status != 'booked':
        return jsonify({'error': 'Cannot cancel this appointment'}), 400
    appointment.status = 'cancelled'
    db.session.commit()
    from backend.cache import invalidate_appointment_cache
    invalidate_appointment_cache()
    return jsonify({'message': 'Appointment cancelled'}), 200
@patient_bp.route('/treatments', methods=['GET'])
@jwt_required()
@patient_required
def get_treatments():
    user_id = get_current_user_id()
    patient = Patient.query.filter_by(user_id=user_id).first()
    if patient is None:
        return jsonify({'error': 'Patient not found'}), 404
    appointments = Appointment.query.filter_by(
        patient_id=patient.id,
        status='completed'
    ).join(Treatment).order_by(Appointment.date.desc()).all()
    history = []
    for apt in appointments:
        if apt.treatment:
            item = apt.treatment.to_dict()
            item['doctor_name'] = apt.doctor.name
            item['date'] = apt.date.isoformat()
            item['specialization'] = apt.doctor.department.name
            history.append(item)
    return jsonify(history), 200
@patient_bp.route('/export', methods=['POST'])
@jwt_required()
@patient_required
def export_history():
    from backend.tasks.exports import export_patient_treatments
    user_id = get_current_user_id()
    patient = Patient.query.filter_by(user_id=user_id).first()
    if patient is None:
        return jsonify({'error': 'Patient not found'}), 404
    try:
        filepath = export_patient_treatments(patient.id, patient.user.email)
        return jsonify({
            'message': 'Export completed', 
            'status': 'completed', 
            'file': os.path.basename(filepath)
        }), 200
    except Exception as e:
        print(f"Export error: {e}")
        return jsonify({'error': str(e)}), 500
@patient_bp.route('/export/<job_id>/status', methods=['GET'])
def get_export_status(job_id):
    # Legacy endpoint kept for compatibility – returns a simple "completed" status.
    return jsonify({'status': 'completed'}), 200
@patient_bp.route('/export/<filename>/download_direct', methods=['GET'])
def download_export_direct(filename):
    from flask_jwt_extended import decode_token
    from flask import request, send_file
    token = request.args.get('token')
    if not token:
        return jsonify({'error': 'Missing token'}), 401
    try:
        decode_token(token)
    except:
        return jsonify({'error': 'Invalid token'}), 401
    export_dir = os.path.join(os.getcwd(), 'exports')
    filepath = os.path.join(export_dir, filename)
    if not os.path.exists(filepath):
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        filepath = os.path.join(downloads_path, filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    return send_file(filepath, as_attachment=True, download_name=filename, mimetype='text/html')