import os
import logging
from app import create_app, db
from app.models import Todo

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def deploy():
    try:
        # Create the app with the database path
        db_path = os.path.join(os.environ.get('HOME', '/home/site/wwwroot'), 'data', 'todos.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        app = create_app({
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False
        })
        
        # Drop and recreate all tables
        with app.app_context():
            logger.info(f"Dropping all tables in {db_path}")
            db.drop_all()
            
            logger.info("Creating all tables with updated schema")
            db.create_all()
            
            logger.info("Database initialization completed successfully")
            
    except Exception as e:
        logger.error(f"Error during deployment: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    deploy() 