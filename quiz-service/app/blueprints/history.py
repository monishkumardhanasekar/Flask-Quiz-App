from flask import Blueprint, render_template, abort
from app.models import QuizAttempt, AttemptAnswer, Question
from app.helpers import get_user_id

def option_text(question, key):
    return {
        "A": question.option_a,
        "B": question.option_b,
        "C": question.option_c,
        "D": question.option_d,
    }.get(key)

history_bp = Blueprint("history", __name__, url_prefix="/history")

@history_bp.route("/")
def history():
    user_id = get_user_id()
    if not user_id:
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))
    
    # CRITICAL: Only show attempts for this specific user
    # Filter out NULL user_id attempts (old data) and ensure strict user matching
    attempts = (
        QuizAttempt.query
        .filter(QuizAttempt.user_id == user_id)  # Strict equality, no NULL
        .filter(QuizAttempt.user_id.isnot(None))  # Explicitly exclude NULL
        .order_by(QuizAttempt.id.desc())
        .all()
    )
    return render_template("history.html", attempts=attempts)


# this shows the result of the current quiz. (score, total questions, etc.)
@history_bp.route("/result/<int:attempt_id>")
def result(attempt_id):
    user_id = get_user_id()
    if not user_id:
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))

    attempt = QuizAttempt.query.get_or_404(attempt_id)

    # CRITICAL: Strict security check - user must own this attempt
    # Block NULL user_id attempts and ensure exact user match
    if attempt.user_id is None:
        abort(403, description="This quiz attempt has no owner")
    if attempt.user_id != user_id:
        abort(403, description="You can only view your own quiz results")

    answers = AttemptAnswer.query.filter_by(attempt_id=attempt_id).all()

    # compute score 
    score = 0
    details = []
    for a in answers:
        q = Question.query.get(a.question_id)
        is_correct = (a.chosen_option == q.correct_option)
        if is_correct:
            score += 1
        details.append({
            "question": q,
            "chosen_key": a.chosen_option,
            "chosen_text": option_text(q, a.chosen_option),
            "correct_key": q.correct_option,
            "correct_text": option_text(q, q.correct_option),
            "is_correct": is_correct
        })


    return render_template("result.html", attempt=attempt, score=score, total=len(answers), details=details)

