from datetime import datetime
from app.db import db

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    questions = db.relationship("Question", backref="category", lazy=True)


class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)

    prompt = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)

    correct_option = db.Column(db.String(1), nullable=False)  # "A", "B", "C", "D"


class UserStats(db.Model):
    """
    User statistics - initialized when user registers via saga
    """
    __tablename__ = "user_stats"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    total_quizzes = db.Column(db.Integer, default=0, nullable=False)
    total_correct = db.Column(db.Integer, default=0, nullable=False)
    total_questions = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempts"
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=True)  # User ID from gateway (nullable for existing data)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    submitted_at = db.Column(db.DateTime, nullable=True)

    # store picked question order as a simple comma string: "12,4,9,1,8"
    question_ids_csv = db.Column(db.String(255), nullable=False)

    category = db.relationship("Category", backref="attempts")

    answers = db.relationship("AttemptAnswer", backref="attempt", lazy=True)

    @property
    def is_submitted(self) -> bool:
        return self.submitted_at is not None


class AttemptAnswer(db.Model):
    __tablename__ = "attempt_answers"
    id = db.Column(db.Integer, primary_key=True)

    attempt_id = db.Column(db.Integer, db.ForeignKey("quiz_attempts.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)

    chosen_option = db.Column(db.String(1), nullable=True)  # "A"/"B"/"C"/"D"

    question = db.relationship("Question")
