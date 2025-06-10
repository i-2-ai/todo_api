import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_cors import CORS
from flask_talisman import Talisman

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
talisman = Talisman()

def create_app(test_config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)

    # Load default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///todos.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=True,  # Enable CSRF protection globally
        WTF_CSRF_SSL_STRICT=True,  # Enforce SSL for CSRF tokens
        WTF_CSRF_CHECK_DEFAULT=True,  # Enable CSRF check by default
        WTF_CSRF_METHODS=['POST', 'PUT', 'PATCH', 'DELETE'],  # Methods to protect
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        # CORS settings
        CORS_METHODS=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        CORS_ALLOW_HEADERS=['Content-Type', 'X-CSRF-Token', 'Authorization'],
        CORS_EXPOSE_HEADERS=['X-CSRF-Token'],
        CORS_SUPPORTS_CREDENTIALS=True
    )

    # Override configuration with test config if provided
    if test_config is not None:
        app.config.update(test_config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Initialize Talisman with security headers
    csp = {
        'default-src': "'self'",
        'img-src': "'self' data:",
        'script-src': "'self' 'unsafe-inline' 'unsafe-eval'",
        'style-src': "'self' 'unsafe-inline'",
    }
    
    talisman.init_app(app,
        force_https=not app.config.get('TESTING', False),
        strict_transport_security=True,
        session_cookie_secure=True,
        content_security_policy=csp,
        content_security_policy_nonce_in=['script-src', 'style-src'],
        feature_policy={
            'geolocation': "'none'",
            'midi': "'none'",
            'notifications': "'none'",
            'push': "'none'",
            'sync-xhr': "'none'",
            'microphone': "'none'",
            'camera': "'none'",
            'magnetometer': "'none'",
            'gyroscope': "'none'",
            'speaker': "'none'",
            'vibrate': "'none'",
            'fullscreen': "'none'",
            'payment': "'none'"
        }
    )

    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(e):
        return {'error': str(e)}, 404

    @app.errorhandler(400)
    def bad_request_error(e):
        return {'error': str(e)}, 400

    @app.errorhandler(500)
    def internal_error(e):
        return {'error': str(e)}, 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return {'error': str(e)}, 400

    # Register blueprints
    from .routes import bp as api_bp
    app.register_blueprint(api_bp)  # Remove the url_prefix to allow Swagger UI access

    # Enable CORS after registering blueprints
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": app.config['CORS_METHODS'],
            "allow_headers": app.config['CORS_ALLOW_HEADERS'],
            "expose_headers": app.config['CORS_EXPOSE_HEADERS'],
            "supports_credentials": app.config['CORS_SUPPORTS_CREDENTIALS']
        }
    })

    # Create database tables
    with app.app_context():
        db.create_all()

    return app 