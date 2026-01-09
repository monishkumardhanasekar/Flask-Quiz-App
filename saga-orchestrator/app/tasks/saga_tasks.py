"""
Saga Tasks - Individual steps and compensation actions
"""
import requests
import logging
from app.celery_app import celery

logger = logging.getLogger(__name__)

# Service URLs
USER_SERVICE_URL = 'http://127.0.0.1:5001'
QUIZ_SERVICE_URL = 'http://127.0.0.1:5002'


@celery.task(name='saga.create_user')
def create_user_task(email, password):
    """
    Saga Step 1: Create user in User Service
    Returns: {'user_id': int, 'email': str}
    """
    try:
        response = requests.post(
            f'{USER_SERVICE_URL}/saga/register',
            json={'email': email, 'password': password},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        logger.info(f"User created: {result['user_id']}")
        return result
    except Exception as e:
        logger.error(f"Failed to create user: {str(e)}")
        raise


@celery.task(name='saga.init_quiz_profile')
def init_quiz_profile_task(user_id):
    """
    Saga Step 2: Initialize user profile/stats in Quiz Service
    Returns: {'user_id': int, 'stats_id': int}
    """
    try:
        response = requests.post(
            f'{QUIZ_SERVICE_URL}/saga/init-profile',
            json={'user_id': user_id},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        logger.info(f"Quiz profile initialized for user: {user_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to initialize quiz profile: {str(e)}")
        raise


@celery.task(name='saga.compensate_delete_user')
def compensate_delete_user_task(user_id):
    """
    Compensation: Delete user from User Service
    Used when saga fails after user creation
    """
    try:
        response = requests.delete(
            f'{USER_SERVICE_URL}/saga/users/{user_id}',
            timeout=10
        )
        logger.info(f"Compensated: Deleted user {user_id}")
        return {'compensated': True, 'user_id': user_id}
    except Exception as e:
        logger.error(f"Compensation failed for user {user_id}: {str(e)}")
        # Log but don't raise - compensation failures should be logged for manual intervention
        return {'compensated': False, 'error': str(e)}


@celery.task(name='saga.compensate_delete_profile')
def compensate_delete_profile_task(user_id):
    """
    Compensation: Delete user profile from Quiz Service
    Used when saga fails after profile initialization
    """
    try:
        response = requests.delete(
            f'{QUIZ_SERVICE_URL}/saga/profile/{user_id}',
            timeout=10
        )
        logger.info(f"Compensated: Deleted quiz profile for user {user_id}")
        return {'compensated': True, 'user_id': user_id}
    except Exception as e:
        logger.error(f"Compensation failed for profile {user_id}: {str(e)}")
        return {'compensated': False, 'error': str(e)}

