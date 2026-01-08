import random
import uuid
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, session
from app.db import db
from app.models import Category, Question, QuizAttempt
from app.helpers import get_user_id

main_bp = Blueprint("main", __name__)

@main_bp.route("/home")
def home():
    # Client-side auth check will handle redirect if not logged in
    # This route just renders the template
    categories = Category.query.all()
    
    # fetch all unfinished attempts from session (not DB)
    unfinished_list = get_unfinished_attempts()
    
    return render_template(
        "home.html",
        categories=categories,
        unfinished_list=unfinished_list
    )


@main_bp.route("/start/<int:category_id>", methods=["POST"])
def start_quiz(category_id):


    questions = Question.query.filter_by(category_id=category_id).all()
    # pick 5 random from 10
    chosen = random.sample(questions, 5)
    chosen_ids = [q.id for q in chosen]
    
    # Generate a temporary ID for this unfinished quiz.
    temp_id = f"temp_{uuid.uuid4().hex[:12]}"
    
    # Store ALL quiz data in session only for unfinished quizzes.
    # Initialize session structure if it doesn't exist
    if 'unfinished_quizzes' not in session:
        session['unfinished_quizzes'] = {}
    
    # Get user_id from gateway header (if available)
    user_id = get_user_id()
    
    # Store complete quiz data in session
    session['unfinished_quizzes'][temp_id] = {
        'category_id': category_id,
        'started_at': datetime.utcnow().isoformat(),
        'question_ids': [str(qid) for qid in chosen_ids],
        'answers': {str(qid): None for qid in chosen_ids},
        'user_id': user_id  # Store user_id in session for later use
    }
    session.modified = True  # Mark session as modified

    return redirect(url_for("quiz.question", attempt_id=temp_id, index=0))



def get_unfinished_attempts():
    """Return all unfinished quiz attempts from session, ordered by most recent."""
    if 'unfinished_quizzes' not in session:
        return []
    
    unfinished_list = []
    for temp_id, quiz_data in session['unfinished_quizzes'].items():
        # Convert session data to a simple object-like structure for template
        question_ids = quiz_data.get('question_ids', [])
        answers = quiz_data.get('answers', {})
        
        # Count answered questions
        answered = len([v for v in answers.values() if v is not None])
        total = len(question_ids)
        
        # Create a simple object to mimic QuizAttempt for template compatibility
        started_at_str = quiz_data.get('started_at', datetime.utcnow().isoformat())
        try:
            started_at_dt = datetime.fromisoformat(started_at_str)
        except (ValueError, TypeError):
            started_at_dt = datetime.utcnow()
        
        attempt_obj = type('obj', (object,), {
            'id': temp_id,  # Use temp_id for URLs
            'category_id': quiz_data.get('category_id'),
            'started_at': started_at_dt,
            'answered_count': answered,
            'total_questions': total,
            'progress_percent': (answered * 100 // total) if total else 0,
            'has_session_data': True,
            'category': Category.query.get(quiz_data.get('category_id'))
        })()
        unfinished_list.append(attempt_obj)
    
    # Sort by started_at descending (most recent first)
    unfinished_list.sort(key=lambda x: x.started_at, reverse=True)
    return unfinished_list



@main_bp.route("/resume/<attempt_id>")
def resume_specific(attempt_id):
    """Resume a specific unfinished attempt chosen by the user."""
    # Check if it's a temp ID (unfinished) or real ID (submitted)
    if isinstance(attempt_id, str) and attempt_id.startswith('temp_'):
        # Unfinished quiz - check session
        quiz_data = get_quiz_data_from_session(attempt_id)
        if not quiz_data:
            return redirect(url_for("main.home", notice="Session data for this quiz is missing.", notice_category="error"))
        return _resume_attempt(attempt_id, quiz_data)
    else:
        # Submitted quiz - check DB
        attempt = QuizAttempt.query.get_or_404(int(attempt_id))
        if attempt.submitted_at is None:
            # Shouldn't happen, but handle it
            return redirect(url_for("main.home"))
        # Already submitted, redirect to results
        return redirect(url_for("history.result", attempt_id=int(attempt_id)))


@main_bp.route("/discard/<attempt_id>", methods=["POST"])
def discard_attempt(attempt_id):
    """Discard an unfinished attempt (remove from session only, no DB involved)."""
    # Check if it's a temp ID (unfinished) or real ID (submitted)
    if isinstance(attempt_id, str) and attempt_id.startswith('temp_'):
        # Unfinished quiz - just remove from session
        if 'unfinished_quizzes' in session and attempt_id in session['unfinished_quizzes']:
            del session['unfinished_quizzes'][attempt_id]
            session.modified = True
        return redirect(url_for("main.home", notice="Unfinished attempt discarded.", notice_category="auto-dismiss"))
    else:
        # Submitted quiz - cannot discard
        return redirect(url_for("main.home", notice="Cannot discard a submitted attempt.", notice_category="error"))


def _resume_attempt(temp_id, quiz_data):
    """Internal helper: redirect to the first unanswered question for the attempt."""
    # Convert question_ids to integers (session stores them as strings)
    question_ids_raw = quiz_data.get('question_ids', [])
    question_ids = []
    for qid in question_ids_raw:
        try:
            question_ids.append(int(qid))
        except (ValueError, TypeError):
            continue
    
    # Convert answer keys to integers for consistent lookups
    answers_raw = quiz_data.get('answers', {})
    answers = {}
    for k, v in answers_raw.items():
        try:
            answers[int(k)] = v
        except (ValueError, TypeError):
            continue
    
    unanswered_index = 0
    for idx, qid in enumerate(question_ids):
        if answers.get(qid) is None:
            unanswered_index = idx
            break
        unanswered_index = idx + 1

    return redirect(
        url_for(
            "quiz.question",
            attempt_id=temp_id,
            index=min(unanswered_index, len(question_ids) - 1),
        )
    )


def get_quiz_data_from_session(temp_id):
    """Helper function to get quiz data from session."""
    if 'unfinished_quizzes' not in session:
        return None
    return session['unfinished_quizzes'].get(temp_id)
