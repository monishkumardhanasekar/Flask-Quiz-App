import os
import jwt
from flask import request, session


def get_user_id():
    """
    Get user_id from:
    1. X-User-Id header (set by gateway after JWT validation) - highest priority
    2. Flask session (stored when user logs in)
    3. JWT token from Authorization header (for direct access)
    
    Returns None if user_id cannot be determined.
    """
    # First check: X-User-Id header from gateway
    user_id_header = request.headers.get('X-User-Id') or request.headers.get('x-user-id')
    if user_id_header:
        try:
            return int(user_id_header)
        except (ValueError, TypeError):
            pass
    
    # Second check: Flask session
    if 'user_id' in session:
        return session.get('user_id')
    
    # Third check: Extract from JWT token in Authorization header
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ', 1)[1].strip()
        try:
            jwt_secret = os.getenv('JWT_SECRET', 'dev-jwt-secret-change-me')
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            user_id = payload.get('user_id')
            if user_id:
                # Store in session for future requests
                session['user_id'] = user_id
                return user_id
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Exception):
            pass
    
    return None

