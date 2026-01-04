from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, session
from app.db import db
from app.models import QuizAttempt, AttemptAnswer, Question
import random


quiz_bp = Blueprint("quiz", __name__, url_prefix="/quiz")

@quiz_bp.route("/<attempt_id>/q/<int:index>", methods=["GET", "POST"])
def question(attempt_id, index):
    # Check if it's a temp ID (unfinished) or real ID (submitted)
    is_temp_id = isinstance(attempt_id, str) and attempt_id.startswith('temp_')
    
    if is_temp_id:
        # Unfinished quiz - get data from session only
        quiz_data = _get_quiz_data_from_session(attempt_id)
        if not quiz_data:
            return redirect(url_for("main.home", notice="Session data for this quiz is missing. Please discard and start a new quiz.", notice_category="error"))
    else:
        return redirect(url_for("main.home"))

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

    if index < 0 or index >= len(question_ids):
        return redirect(url_for("quiz.question", attempt_id=attempt_id, index=0))

    current_qid = question_ids[index]
    question = Question.query.get_or_404(current_qid)

    # Get selected answer from session
    selected_answer = answers.get(current_qid)

    # count answered questions for progress display from session
    answered_count = len([v for v in answers.values() if v is not None])

    # Create attempt object for template compatibility (needed for both GET and POST/error rendering)
    if is_temp_id:
        from app.models import Category
        category = Category.query.get(quiz_data.get('category_id'))
        # Create a simple object to mimic QuizAttempt for template
        attempt_obj = type('obj', (object,), {
            'id': attempt_id,
            'category': category,
            'category_id': quiz_data.get('category_id'),
        })()
    else:
        # This shouldn't happen for unfinished quizzes, but handle it
        attempt_obj = QuizAttempt.query.get_or_404(int(attempt_id))

    if request.method == "POST":
        chosen = request.form.get("choice")  # "A"/"B"/"C"/"D"
        action = request.form.get("action")  # prev/next/submit

        # Update answer in session (only for unfinished quizzes)
        if chosen and is_temp_id:
            if 'unfinished_quizzes' not in session:
                session['unfinished_quizzes'] = {}
            # Update answer in session
            if attempt_id not in session['unfinished_quizzes']:
                # Shouldn't happen, but initialize if needed
                session['unfinished_quizzes'][attempt_id] = quiz_data.copy()
            session['unfinished_quizzes'][attempt_id]['answers'][str(current_qid)] = chosen
            session.modified = True
            # Update local answers dict for immediate use (use int key)
            answers[current_qid] = chosen
            answered_count = len([v for v in answers.values() if v is not None])

        # Navigate
        if action == "prev":
            return redirect(url_for("quiz.question", attempt_id=attempt_id, index=index - 1))

        if action == "next":
            return redirect(url_for("quiz.question", attempt_id=attempt_id, index=index + 1))

        if action == "submit":
            # Require all questions answered (check session)
            missing = [qid for qid in question_ids if answers.get(qid) is None]

            if missing:
                # render with an error message
                error = "Please answer all questions before submitting."
                total = len(question_ids)
                is_last = (index == total - 1)
                options = [
                    ("A", question.option_a),
                    ("B", question.option_b),
                    ("C", question.option_c),
                    ("D", question.option_d),
                ]
                random.shuffle(options)
                return render_template(
                    "question.html",
                    attempt=attempt_obj,
                    question=question,
                    options=options,
                    selected=answers.get(current_qid),
                    index=index,
                    total=total,
                    is_last=is_last,
                    answered_count=answered_count,
                    progress_percent=(answered_count * 100 // total if total else 0),
                    error=error,
                )

            # once, All questions answered - create DB records and submit
            if is_temp_id:
                # Create QuizAttempt record in DB (first time!)
                quiz_data = _get_quiz_data_from_session(attempt_id)
                category_id = quiz_data.get('category_id')
                started_at = datetime.fromisoformat(quiz_data.get('started_at', datetime.utcnow().isoformat()))
                
                attempt = QuizAttempt(
                    category_id=category_id,
                    question_ids_csv=",".join(map(str, question_ids)),
                    started_at=started_at,
                    submitted_at=datetime.utcnow()
                )
                db.session.add(attempt)
                db.session.commit()
                
                # Now save answers to DB
                _save_answers_to_db(attempt.id, question_ids, answers)
                
                # Remove from session since it's now submitted
                if 'unfinished_quizzes' in session and attempt_id in session['unfinished_quizzes']:
                    del session['unfinished_quizzes'][attempt_id]
                    session.modified = True
                
                # Redirect to results using the real DB ID
                return redirect(url_for("history.result", attempt_id=attempt.id))
            else:
                # This shouldn't happen for unfinished quizzes, but handle it
                return redirect(url_for("main.home"))

    total = len(question_ids)
    is_last = (index == total - 1)

    options = [
        ("A", question.option_a),
        ("B", question.option_b),
        ("C", question.option_c),
        ("D", question.option_d),
    ]

    random.shuffle(options)

    return render_template(
        "question.html",
        attempt=attempt_obj,
        question=question,
        options=options,
        selected=selected_answer,
        index=index,
        total=total,
        is_last=is_last,
        answered_count=answered_count,
        progress_percent=(answered_count * 100 // total if total else 0)
    )


def _get_quiz_data_from_session(temp_id):
    """Helper function to get quiz data from session."""
    if 'unfinished_quizzes' not in session:
        return None
    return session['unfinished_quizzes'].get(temp_id)


def _save_answers_to_db(attempt_id, question_ids, answers):
    """Save all answers from session to database when quiz is submitted."""
    for qid in question_ids:
        chosen_option = answers.get(qid)
        answer_row = AttemptAnswer(
            attempt_id=attempt_id,
            question_id=qid,
            chosen_option=chosen_option
        )
        db.session.add(answer_row)
    db.session.commit()

