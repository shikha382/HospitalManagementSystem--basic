from flask import Blueprint, request, jsonify
from backend.models import db, User, Doctor, Patient
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    required_fields = ['username', 'email', 'password', 'name', 'age', 'gender', 'contact']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing: {field}'}), 400
    user = User.query.filter_by(username=data['username']).first()
    if user:
        return jsonify({'error': 'Username exists'}), 400
    email = User.query.filter_by(email=data['email']).first()
    if email:
        return jsonify({'error': 'Email exists'}), 400
    new_user = User(
        username=data['username'],
        email=data['email'],
        role='patient'
    )
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.flush()
    new_patient = Patient(
        user_id=new_user.id,
        name=data['name'],
        age=data['age'],
        gender=data['gender'],
        contact=data['contact'],
        address=data.get('address', ''),
        medical_history=data.get('medical_history', '')
    )
    db.session.add(new_patient)
    db.session.commit()
    return jsonify({'message': 'Registration successful', 'user': new_user.to_dict()}), 201
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    user = User.query.filter_by(username=data['username']).first()
    if user is None:
        return jsonify({'error': 'Invalid credentials'}), 401
    if not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    if not user.active:
        return jsonify({'error': 'Account deactivated'}), 403
    token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role}
    )
    profile_data = {}
    if user.role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=user.id).first()
        if doctor:
            profile_data = doctor.to_dict()
    elif user.role == 'patient':
        patient = Patient.query.filter_by(user_id=user.id).first()
        if patient:
            profile_data = patient.to_dict()
    return jsonify({
        'token': token,
        'user': user.to_dict(),
        'profile': profile_data
    }), 200
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    profile_data = {}
    if user.role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=user.id).first()
        if doctor:
            profile_data = doctor.to_dict()
    elif user.role == 'patient':
        patient = Patient.query.filter_by(user_id=user.id).first()
        if patient:
            profile_data = patient.to_dict()
    return jsonify({
        'user': user.to_dict(),
        'profile': profile_data
    }), 200
