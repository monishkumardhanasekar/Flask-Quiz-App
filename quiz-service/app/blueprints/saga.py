"""
Saga endpoints for Quiz Service
These endpoints are called by the Saga Orchestrator
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from app.db import db
from app.models import UserStats

saga_bp = Blueprint("saga", __name__, url_prefix="/saga")


@saga_bp.route("/init-profile", methods=["POST"])
def init_profile():
    """
    Initialize user profile/stats for saga (called by orchestrator)
    Creates UserStats record for the user
    """
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    # Check if stats already exist
    existing = UserStats.query.filter_by(user_id=user_id).first()
    if existing:
        return jsonify({"error": "profile already exists"}), 409

    # Create user stats
    stats = UserStats(
        user_id=user_id,
        total_quizzes=0,
        total_correct=0,
        total_questions=0
    )
    db.session.add(stats)
    db.session.commit()

    return jsonify({
        "user_id": user_id,
        "stats_id": stats.id,
        "message": "profile initialized"
    }), 201


@saga_bp.route("/profile/<int:user_id>", methods=["DELETE"])
def delete_profile(user_id):
    """
    Compensation endpoint: Delete user profile/stats
    Called by saga orchestrator during rollback
    """
    stats = UserStats.query.filter_by(user_id=user_id).first()
    if not stats:
        return jsonify({"error": "profile not found"}), 404

    db.session.delete(stats)
    db.session.commit()

    return jsonify({"message": "profile deleted", "user_id": user_id}), 200


@saga_bp.route("/profile/<int:user_id>", methods=["GET"])
def get_profile(user_id):
    """
    Check if profile exists (for testing)
    """
    stats = UserStats.query.filter_by(user_id=user_id).first()
    if not stats:
        return jsonify({"error": "profile not found"}), 404

    return jsonify({
        "user_id": stats.user_id,
        "stats_id": stats.id,
        "total_quizzes": stats.total_quizzes
    }), 200
