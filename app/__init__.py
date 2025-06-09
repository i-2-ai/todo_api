from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import logging
import sys

db = SQLAlchemy()

def create_app(config=None):
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)
    
    logger.info('Starting application initialization')
    app = Flask(__name__)
    
    # Default configuration
    try:
        db_path = os.path.join(os.environ.get('HOME', '/home/site/wwwroot'), 'todos.db')
        logger.info(f'Using database path: {db_path}')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Override with custom config if provided
        if config:
            logger.info('Applying custom configuration')
            app.config.update(config)
        
        logger.info('Initializing database')
        db.init_app(app)
        
        logger.info('Registering blueprints')
        from .routes import bp
        app.register_blueprint(bp)
        
        logger.info('Creating database tables')
        with app.app_context():
            db.create_all()
        
        logger.info('Application initialization completed successfully')
        return app
    except Exception as e:
        logger.error(f'Error during application initialization: {str(e)}', exc_info=True)
        raise 