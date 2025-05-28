from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def create_app(config=None):
    app = Flask(__name__)
    
    # Default configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Override with custom config if provided
    if config:
        app.config.update(config)
    
    db.init_app(app)
    
    from .routes import bp
    app.register_blueprint(bp)
    
    with app.app_context():
        db.create_all()
    
    return app 