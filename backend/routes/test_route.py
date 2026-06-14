from flask import Blueprint, jsonify, request, send_from_directory
from backend.tasks.math_tasks import add_numbers
from backend.tasks.exports import export_appointments_csv, EXPORTS_DIR
from backend.celery_app import celery
import os

test_bp = Blueprint('test', __name__, url_prefix='/api/test')

@test_bp.route('/add', methods=['GET'])
def trigger_add():
    x = request.args.get('x', type=float)
    y = request.args.get('y', type=float)
    task = add_numbers.delay(x, y)
    return jsonify({'task_id': task.id}), 200

@test_bp.route('/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    result = celery.AsyncResult(task_id)
    return jsonify({
        'status': result.status,
        'result': result.result if result.ready() else None
    }), 200

@test_bp.route('/export_appointments', methods=['GET'])
def trigger_export():
    task = export_appointments_csv.delay()
    return jsonify({'task_id': task.id}), 200

@test_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(EXPORTS_DIR, filename, as_attachment=True)

@celery.task(name="tasks.dynamic_test_task")
def dynamic_test_task(x, y):
    return x + y

@test_bp.route('/dynamic_test', methods=['POST'])
def run_dynamic_test():
    data = request.get_json()
    x = data.get('x', 0)
    y = data.get('y', 0)
    task = dynamic_test_task.delay(x, y)
    return jsonify({"task_id": task.id, "message": "task started"})