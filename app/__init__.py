import os
from flask import Flask, render_template
from dotenv import load_dotenv
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

    # register blueprints - 3 pages: main, quiz, history
    from app.blueprints.main import main_bp
    from app.blueprints.quiz import quiz_bp
    from app.blueprints.history import history_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(history_bp)

    # Create tables if they don't exist using flask SQLAlchemy. with app_context, we run functions that's oustide of the app context(web request).
    with app.app_context():
        db.create_all()

    # Custom 404 handler to render our friendly template -  when 404 error occurs, it will render 404.html template.
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    return app
