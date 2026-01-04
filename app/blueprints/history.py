from flask import Blueprint, render_template
from app.models import QuizAttempt, AttemptAnswer, Question

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
    attempts = QuizAttempt.query.order_by(QuizAttempt.id.desc()).all()
    return render_template("history.html", attempts=attempts)


# this shows the result of the current quiz. (score, total questions, etc.)
@history_bp.route("/result/<int:attempt_id>")
def result(attempt_id):
    attempt = QuizAttempt.query.get_or_404(attempt_id)
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

