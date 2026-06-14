from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from backend.config import Config
from backend.models import db, User, Department
from backend.routes.auth import auth_bp
from backend.routes.admin import admin_bp
from backend.routes.doctor import doctor_bp
from backend.routes.patient import patient_bp
from backend.routes.test_route import test_bp
from backend.email_utills import mail

import os

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)
    instance_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    from backend.email_utills import mail
    mail.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(test_bp)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def index(path):
        if path.startswith('api/'):
            return jsonify({'error': 'Page not found'}), 404
        return render_template('index.html')
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized'}), 401
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden'}), 403
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return jsonify({'error': 'Invalid token'}), 401
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token expired'}), 401
    @jwt.unauthorized_loader
    def unauthorized_callback(error_string):
        return jsonify({'error': 'Missing token'}), 401
    with app.app_context():
        db.create_all()
        initialize_data()
    return app
def initialize_data():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@hospital.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
    departments_data = [
        {'name': 'Cardiology', 'description': 'Heart Specialist'},
        {'name': 'Neurology', 'description': 'Brain Specialist'},
        {'name': 'Orthopedics', 'description': 'Bone Specialist'},
        {'name': 'Pediatrics', 'description': 'Child Specialist'},
        {'name': 'Dermatology', 'description': 'Skin Specialist'},
        {'name': 'General Medicine', 'description': 'General Health'},
    ]
    for item in departments_data:
        dept = Department.query.filter_by(name=item['name']).first()
        if not dept:
            db.session.add(Department(**item))
    db.session.commit()
from backend.celery_app import celery
from backend.tasks.reminders import send_daily_reminders
from backend.tasks.reports import generate_monthly_reports
from backend.tasks.exports import export_csv_task
jwt = JWTManager()
app = create_app()
daily_reminder_task = send_daily_reminders
monthly_report_task = generate_monthly_reports
export_csv_task = export_csv_task
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
