"""
User Registration Saga - Orchestrates user creation across services
"""
import uuid
import logging
import requests
from app.celery_app import celery

logger = logging.getLogger(__name__)

# Service URLs
USER_SERVICE_URL = 'http://127.0.0.1:5001'
QUIZ_SERVICE_URL = 'http://127.0.0.1:5002'


@celery.task(name='saga.user_registration_orchestrator', bind=True)
def user_registration_saga(self, email, password):
    """
    Orchestrates the user registration saga:
    1. Create user in User Service
    2. Initialize profile in Quiz Service
    
    If any step fails, executes compensation in reverse order.
    
    Returns:
        {
            'status': 'success' | 'failed',
            'saga_id': str,
            'user_id': int (if successful),
            'compensation_log': list (if failed)
        }
    """
    saga_id = str(uuid.uuid4())
    compensation_log = []
    
    logger.info(f"Saga {saga_id} started: User registration for {email}")
    
    try:
        # Step 1: Create user in User Service
        logger.info(f"Saga {saga_id}: Step 1 - Creating user")
        try:
            response = requests.post(
                f'{USER_SERVICE_URL}/saga/register',
                json={'email': email, 'password': password},
                timeout=10
            )
            response.raise_for_status()
            user_result = response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"User creation failed: {str(e)}")
        
        if not user_result or 'user_id' not in user_result:
            raise Exception("User creation failed - invalid response")
        
        user_id = user_result['user_id']
        compensation_log.append(('delete_user', user_id))
        logger.info(f"Saga {saga_id}: Step 1 completed - User {user_id} created")
        
        # Step 2: Initialize profile in Quiz Service
        logger.info(f"Saga {saga_id}: Step 2 - Initializing quiz profile")
        try:
            response = requests.post(
                f'{QUIZ_SERVICE_URL}/saga/init-profile',
                json={'user_id': user_id},
                timeout=10
            )
            response.raise_for_status()
            profile_result = response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Profile initialization failed: {str(e)}")
        
        if not profile_result or 'user_id' not in profile_result:
            raise Exception("Profile initialization failed - invalid response")
        
        compensation_log.append(('delete_profile', user_id))
        logger.info(f"Saga {saga_id}: Step 2 completed - Profile initialized")
        
        # All steps succeeded
        logger.info(f"Saga {saga_id}: Completed successfully")
        return {
            'status': 'success',
            'saga_id': saga_id,
            'user_id': user_id,
            'email': email
        }
        
    except Exception as e:
        logger.error(f"Saga {saga_id}: Failed at step - {str(e)}")
        
        # Compensation phase - execute in reverse order
        logger.info(f"Saga {saga_id}: Starting compensation phase")
        compensation_results = []
        
        for action, params in reversed(compensation_log):
            try:
                if action == 'delete_profile':
                    response = requests.delete(
                        f'{QUIZ_SERVICE_URL}/saga/profile/{params}',
                        timeout=10
                    )
                    result = {'compensated': True, 'user_id': params}
                    compensation_results.append({'action': action, 'result': result})
                    logger.info(f"Saga {saga_id}: Compensated - Deleted profile for user {params}")
                elif action == 'delete_user':
                    response = requests.delete(
                        f'{USER_SERVICE_URL}/saga/users/{params}',
                        timeout=10
                    )
                    result = {'compensated': True, 'user_id': params}
                    compensation_results.append({'action': action, 'result': result})
                    logger.info(f"Saga {saga_id}: Compensated - Deleted user {params}")
            except Exception as comp_error:
                logger.error(f"Saga {saga_id}: Compensation {action} failed: {str(comp_error)}")
                compensation_results.append({'action': action, 'error': str(comp_error)})
        
        logger.warning(f"Saga {saga_id}: Compensation completed")
        
        return {
            'status': 'failed',
            'saga_id': saga_id,
            'error': str(e),
            'compensation_log': compensation_results
        }

