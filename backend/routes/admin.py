from flask import Blueprint, request, jsonify
from backend.models import db, User, Doctor, Patient, Appointment, Department
from backend.routes.utils import admin_required
from backend.cache import (
    get_cache, set_cache, get_admin_stats_key,
    invalidate_doctor_cache, invalidate_appointment_cache
)
from flask_jwt_extended import jwt_required
from sqlalchemy import or_, func
from datetime import datetime
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@admin_required
def get_dashboard():
    cache_key = get_admin_stats_key()
    cached = get_cache(cache_key)
    if cached:
        return jsonify(cached), 200
    stats = {
        'total_doctors': Doctor.query.join(User).filter(User.active == True).count(),
        'total_patients': Patient.query.join(User).filter(User.active == True).count(),
        'total_appointments': Appointment.query.count(),
        'upcoming_appointments': Appointment.query.filter(Appointment.date >= datetime.now().date(), Appointment.status == 'booked').count(),
        'completed_appointments': Appointment.query.filter_by(status='completed').count()
    }
    set_cache(cache_key, stats)
    return jsonify(stats), 200
@admin_bp.route('/doctors', methods=['GET'])
@jwt_required()
@admin_required
def get_doctors():
    doctors = Doctor.query.join(User).all()
    return jsonify([d.to_dict() for d in doctors]), 200
@admin_bp.route('/doctors', methods=['POST'])
@jwt_required()
@admin_required
def add_doctor():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    required_fields = ['username', 'email', 'password', 'name', 'specialization_id', 'experience', 'contact']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing: {field}'}), 400
    user = User.query.filter_by(username=data['username']).first()
    if user:
        return jsonify({'error': 'Username already exists'}), 400
    new_user = User(username=data['username'], email=data['email'], role='doctor')
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.flush()
    new_doctor = Doctor(user_id=new_user.id, name=data['name'], specialization_id=data['specialization_id'], experience=data['experience'], qualification=data.get('qualification'), contact=data['contact']
    )
    db.session.add(new_doctor)
    db.session.commit()
    invalidate_doctor_cache()
    invalidate_appointment_cache()
    return jsonify({'message': 'Doctor added successfully', 'doctor': new_doctor.to_dict()}), 201
@admin_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if doctor is None:
        return jsonify({'error': 'Doctor not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    fields = ['name', 'specialization_id', 'experience', 'qualification', 'contact']
    for field in fields:
        if field in data:
            setattr(doctor, field, data[field])
    if "name" in data:
        doctor.name = data["name"]
    if "email" in data and data['email'] != doctor.user.email:
        existing_email = User.query.filter_by(email=data['email']).first()
        if existing_email:
            return jsonify({'error': 'Email already exists'}), 400
        doctor.user.email = data['email']
    if "username" in data and data['username'] != doctor.user.username:
        old_username = User.query.filter_by(username=data['username']).first()
        if old_username:
            return jsonify({'error': 'Username already exists'}), 400
        doctor.user.username = data['username']
    db.session.commit()
    invalidate_doctor_cache(doctor_id)
    return jsonify({'message': 'Doctor updated successfully', 'doctor': doctor.to_dict()}), 200
@admin_bp.route('/doctors/<int:doctor_id>/toggle', methods=['PUT'])
@jwt_required()
@admin_required
def toggle_doctor_status(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if doctor is None:
        return jsonify({'error': 'Doctor not found'}), 404
    doctor.user.active = not doctor.user.active
    db.session.commit()
    invalidate_doctor_cache(doctor_id)
    invalidate_appointment_cache()
    return jsonify({'message': 'Doctor status updated'}), 200
@admin_bp.route('/patients', methods=['GET'])
@jwt_required()
@admin_required
def get_patients():
    patients = Patient.query.join(User).all()
    return jsonify([p.to_dict() for p in patients]), 200
@admin_bp.route('/patients/<int:patient_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_patient(patient_id):
    patient = Patient.query.get(patient_id)
    if patient is None:
        return jsonify({'error': 'Patient not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    update_fields = ['age', 'gender', 'contact', 'address', 'medical_history']
    for field in update_fields:
        if field in data:
            setattr(patient, field, data[field])
    if 'email' in data and data['email'] != patient.user.email:
        existing_email = User.query.filter_by(email=data['email']).first()
        if existing_email:
            return jsonify({'error': 'Email already exists'}), 400
        patient.user.email = data['email']
    if "username" in data and data['username'] != patient.user.username:
        username = User.query.filter_by(username=data['username']).first()
        if username:
            return jsonify({'error': 'Username already exists'}), 400
        patient.user.username = data['username']
    db.session.commit()
    return jsonify({'message': 'Patient updated successfully', 'patient': patient.to_dict()}), 200
@admin_bp.route('/patients/<int:patient_id>/toggle', methods=['PUT'])
@jwt_required()
@admin_required
def toggle_patient_status(patient_id):
    patient = Patient.query.get(patient_id)
    if patient is None:
        return jsonify({'error': 'Patient not found'}), 404
    patient.user.active = not patient.user.active
    db.session.commit()
    invalidate_appointment_cache()
    return jsonify({'message': 'Patient status updated'}), 200
@admin_bp.route('/appointments', methods=['GET'])
@jwt_required()
@admin_required
def get_appointments():
    appointments = Appointment.query.order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    return jsonify([a.to_dict() for a in appointments]), 200
@admin_bp.route('/search/doctors', methods=['GET'])
@jwt_required()
@admin_required
def search_doctors():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([]), 200
    doctors = Doctor.query.join(Department).join(User).filter(
        or_(Doctor.name.ilike(f'%{query}%'), Department.name.ilike(f'%{query}%'))
    ).all()
    return jsonify([d.to_dict() for d in doctors]), 200
@admin_bp.route('/search/patients', methods=['GET'])
@jwt_required()
@admin_required
def search_patients():
    query= request.args.get('q', '').strip()
    if not query:
        return jsonify([]), 200
    patients = Patient.query.filter(or_(Patient.name.ilike(f'%{query}%'),Patient.contact.ilike(f'%{query}%'),Patient.id ==int(query) if query.isdigit() else False)).all()
    return jsonify([p.to_dict() for p in patients]), 200
@admin_bp.route('/departments', methods=['GET'])
@jwt_required()
@admin_required
def get_departments():
    depts = Department.query.all()
    return jsonify([d.to_dict() for d in depts]), 200
@admin_bp.route('/reminders/trigger', methods=['POST'])
@jwt_required()
@admin_required
def trigger_reminders():
    from backend.tasks.reminders import send_daily_reminders
    try:
        count = send_daily_reminders()
        return jsonify({'message': f'Successfully sent {count} reminders!', 'count': count}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/reports/monthly', methods=['POST'])
@jwt_required()
@admin_required
def trigger_monthly_reports():
    from backend.tasks.reports import generate_monthly_reports
    try:
        data = request.get_json() or {}
        year = data.get('year')
        month = data.get('month')
        # Run synchronously (direct call, not .delay()) so we get the result immediately
        result = generate_monthly_reports(year=year, month=month)
        return jsonify({'message': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500