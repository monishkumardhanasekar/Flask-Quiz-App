import os
from flask import Flask
from dotenv import load_dotenv
from app.db import db

# Load .env for local development
load_dotenv()


def create_app():
    app = Flask(__name__)

    # Basic configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///user_service.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.saga import saga_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(saga_bp)

    # Create tables
    with app.app_context():
        db.create_all()

    return app



