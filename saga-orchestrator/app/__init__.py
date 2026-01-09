import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'saga-secret-key')
    
    # Enable CORS for all routes
    # Allow requests from Quiz Service UI
    CORS(app, 
         origins=['http://localhost:5002', 'http://127.0.0.1:5002'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         supports_credentials=False,
         max_age=3600)
    
    # Register blueprints
    from app.blueprints.saga import saga_bp
    app.register_blueprint(saga_bp)
    
    return app

