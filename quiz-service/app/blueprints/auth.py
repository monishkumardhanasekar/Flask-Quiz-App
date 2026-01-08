from flask import Blueprint, render_template, request, session, jsonify
import os
import jwt

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login")
def login():
    # Client-side check will redirect if already logged in
    return render_template("login.html")


@auth_bp.route("/register")
def register():
    # Client-side check will redirect if already logged in
    return render_template("register.html")


@auth_bp.route("/set-session", methods=["POST"])
def set_session():
    """
    Endpoint to set/clear user_id in Flask session from JWT token.
    Called by frontend after login to establish server-side session.
    If token is null, clears the session (for logout).
    """
    data = request.get_json(silent=True) or {}
    token = data.get('token')
    
    # Handle logout (clear session)
    if not token or token is None:
        session.pop('user_id', None)
        return jsonify({"success": True, "message": "Session cleared"}), 200
    
    try:
        jwt_secret = os.getenv('JWT_SECRET', 'dev-jwt-secret-change-me')
        payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
        user_id = payload.get('user_id')
        
        if user_id:
            session['user_id'] = user_id
            return jsonify({"success": True, "user_id": user_id}), 200
        else:
            return jsonify({"error": "Invalid token payload"}), 400
    except jwt.ExpiredSignatureError:
        session.pop('user_id', None)
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        session.pop('user_id', None)
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
