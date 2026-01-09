"""
Saga Orchestrator API endpoints
"""
from flask import Blueprint, request, jsonify
from app.sagas.user_registration_saga import user_registration_saga
import logging

logger = logging.getLogger(__name__)

saga_bp = Blueprint('saga', __name__, url_prefix='/saga')


@saga_bp.route('/register', methods=['POST'])
def register_user():
    """
    Start user registration saga
    This endpoint triggers the saga orchestrator
    """
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'email and password are required'}), 400
    
    try:
        # Trigger the saga asynchronously
        task = user_registration_saga.delay(email, password)
        
        return jsonify({
            'message': 'User registration saga started',
            'task_id': task.id,
            'status': 'processing'
        }), 202  # Accepted - async processing
    
    except Exception as e:
        logger.error(f"Failed to start saga: {str(e)}")
        return jsonify({'error': 'Failed to start registration saga'}), 500


@saga_bp.route('/status/<task_id>', methods=['GET'])
def get_saga_status(task_id):
    """
    Get the status of a running saga
    """
    from app.celery_app import celery
    
    task = celery.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Saga is waiting to start'
        }
    elif task.state == 'PROGRESS':
        response = {
            'state': task.state,
            'status': 'Saga is in progress',
            'info': task.info
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'status': 'Saga completed successfully',
            'result': task.result
        }
    else:  # FAILURE or other states
        response = {
            'state': task.state,
            'status': 'Saga failed',
            'error': str(task.info) if task.info else 'Unknown error',
            'result': task.result if task.result else None
        }
    
    return jsonify(response), 200


@saga_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'saga-orchestrator'}), 200
