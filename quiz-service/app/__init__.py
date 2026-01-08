import os
from flask import Flask, render_template
from dotenv import load_dotenv
from sqlalchemy import inspect, text
from app.db import db

# load .env for local development variables
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Secret key for session encryption (required for Flask sessions)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    # Read DB URL from env (DATABASE_URL) 
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL"
    )


    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # register blueprints - auth, main, quiz, history
    from app.blueprints.auth import auth_bp
    from app.blueprints.main import main_bp
    from app.blueprints.quiz import quiz_bp
    from app.blueprints.history import history_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(history_bp)
    
    # Root route redirects to login (main page)
    @app.route("/")
    def root():
        from flask import redirect, url_for
        return redirect(url_for("auth.login"))

    # Create tables if they don't exist using flask SQLAlchemy. with app_context, we run functions that's oustide of the app context(web request).
    with app.app_context():
        db.create_all()
        # Ensure user_id column exists (for existing databases)
        try:
            inspector = inspect(db.engine)
            if inspector.has_table('quiz_attempts'):
                columns = [col['name'] for col in inspector.get_columns('quiz_attempts')]
                if 'user_id' not in columns:
                    with db.engine.connect() as conn:
                        conn.execute(text("ALTER TABLE quiz_attempts ADD COLUMN user_id INTEGER"))
                        conn.commit()
        except Exception:
            # Column might already exist or table doesn't exist yet
            pass

    # Custom 404 handler to render our friendly template -  when 404 error occurs, it will render 404.html template.
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    return app
