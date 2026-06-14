from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from backend.models import User, db
def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role')
            if user_role not in roles: return jsonify({'error': 'Forbidden'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
def admin_required(fn): return role_required('admin')(fn)
def doctor_required(fn): return role_required('doctor')(fn)
def patient_required(fn): return role_required('patient')(fn)
def get_current_user_id():
    from flask_jwt_extended import get_jwt_identity
    return int(get_jwt_identity())
def get_current_user():
    user_id = get_current_user_id()
    return User.query.get(user_id)
