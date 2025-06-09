import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy()
talisman = Talisman()

def create_app(test_config=None):
    # Create Flask app
    app = Flask(__name__)
    
    if test_config is None:
        # Set the database path for Azure environment
        # Use a writable location in Azure App Service
        db_path = os.path.join(os.environ.get('HOME', '/home/site/wwwroot'), 'data', 'todos.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        app.config.update(
            SQLALCHEMY_DATABASE_URI=f'sqlite:///{db_path}',
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            # Add security-related configurations
            SESSION_COOKIE_SECURE=True,
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE='Lax',
            PERMANENT_SESSION_LIFETIME=1800,  # 30 minutes
            WTF_CSRF_ENABLED=True,
            WTF_CSRF_TIME_LIMIT=3600  # 1 hour
        )
        logger.info(f"Using database path: {db_path}")
        
        # Initialize Talisman for security headers in production
        talisman.init_app(app,
            force_https=True,
            strict_transport_security=True,
            session_cookie_secure=True,
            content_security_policy={
                'default-src': "'self'",
                'img-src': "'self' data:",
                'script-src': "'self'",
                'style-src': "'self' 'unsafe-inline'",
                'frame-ancestors': "'none'"
            }
        )
    else:
        app.config.update(test_config)
        # Set a secret key for session management in tests
        app.config['SECRET_KEY'] = test_config.get('SECRET_KEY', 'test-secret-key')
        # Initialize Talisman with reduced security for testing
        talisman.init_app(app,
            force_https=False,
            session_cookie_secure=False,
            content_security_policy=None
        )

    try:
        # Initialize the database
        db.init_app(app)
        
        # Import models here to ensure they are registered with SQLAlchemy
        from . import models
        
        with app.app_context():
            # Verify the table doesn't exist before creating
            inspector = db.inspect(db.engine)
            if not inspector.has_table("todo"):
                logger.info("Creating database tables...")
                db.create_all()
                logger.info("Database tables created successfully")
            else:
                logger.info("Database tables already exist")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}", exc_info=True)
        raise

    # Register blueprints
    try:
        from .routes import bp, csrf
        csrf.init_app(app)  # Initialize CSRF protection
        app.register_blueprint(bp)
        logger.info("Routes registered successfully")
    except Exception as e:
        logger.error(f"Error registering routes: {str(e)}", exc_info=True)
        raise

    return app 