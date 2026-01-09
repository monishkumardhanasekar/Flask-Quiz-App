import os
from datetime import datetime, timedelta

import jwt
from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import db
from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="")


def _jwt_secret() -> str:
    return os.getenv("JWT_SECRET", "dev-jwt-secret-change-me")


def _generate_token(user: User) -> str:
    payload = {
        "user_id": user.id,
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(hours=12),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, _jwt_secret(), algorithm="HS256")


def _decode_token(token: str):
    return jwt.decode(token, _jwt_secret(), algorithms=["HS256"])


@auth_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "user"}), 200


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "email already registered"}), 409

    password_hash = generate_password_hash(password)
    user = User(email=email, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    return (
        jsonify(
            {
                "message": "registered",
                "user": {"id": user.id, "email": user.email},
            }
        ),
        201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid credentials"}), 401

    token = _generate_token(user)
    return jsonify({"token": token, "user": {"id": user.id, "email": user.email}}), 200


def _get_token_from_header():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1].strip()
    return None


@auth_bp.route("/profile", methods=["GET"])
def profile():
    token = _get_token_from_header()
    if not token:
        return jsonify({"error": "missing token"}), 401
    try:
        payload = _decode_token(token)
        user = User.query.get(payload.get("user_id"))
        if not user:
            return jsonify({"error": "user not found"}), 404
        return jsonify({"id": user.id, "email": user.email}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "invalid token"}), 401



