"""
Saga endpoints for User Service
These endpoints are called by the Saga Orchestrator
"""
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from app.db import db
from app.models import User

saga_bp = Blueprint("saga", __name__, url_prefix="/saga")


@saga_bp.route("/register", methods=["POST"])
def saga_register():
    """
    Create user for saga (called by orchestrator)
    Returns user_id for saga compensation tracking
    """
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    # Check if user already exists
    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "email already registered"}), 409

    password_hash = generate_password_hash(password)
    user = User(email=email, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({"user_id": user.id, "email": user.email}), 201


@saga_bp.route("/users/<int:user_id>", methods=["DELETE"])
def saga_delete_user(user_id):
    """
    Compensation endpoint: Delete user
    Called by saga orchestrator during rollback
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "user deleted", "user_id": user_id}), 200


@saga_bp.route("/users/<int:user_id>", methods=["GET"])
def saga_get_user(user_id):
    """
    Check if user exists (for testing)
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404

    return jsonify({"user_id": user.id, "email": user.email}), 200
