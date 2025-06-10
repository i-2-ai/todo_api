import os
import sys
import logging
import sqlite3
from app import create_app, db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verify_table_schema(db_path):
    """Verify the table schema has the required columns"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(todo)")
        columns = {row[1] for row in cursor.fetchall()}
        
        required_columns = {'id', 'title', 'description', 'completed', 'due_date', 'created_at'}
        missing_columns = required_columns - columns
        
        if missing_columns:
            logger.warning(f"Missing columns in todo table: {missing_columns}")
            return False
            
        logger.info("Table schema verification successful")
        return True
        
    except Exception as e:
        logger.error(f"Error verifying table schema: {str(e)}", exc_info=True)
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def deploy():
    try:
        # Create the app with the database path
        db_path = os.path.join(os.environ.get('HOME', '/home/site/wwwroot'), 'data', 'todos.db')
        db_dir = os.path.dirname(db_path)
        
        # Ensure the data directory exists
        logger.info(f"Creating database directory: {db_dir}")
        os.makedirs(db_dir, exist_ok=True)
        
        # Set directory permissions
        try:
            os.chmod(db_dir, 0o777)
            logger.info("Set database directory permissions to 777")
        except Exception as e:
            logger.warning(f"Could not set directory permissions: {str(e)}")
        
        app = create_app({
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False
        })
        
        # Drop and recreate all tables
        with app.app_context():
            logger.info(f"Checking database at {db_path}")
            
            if os.path.exists(db_path):
                if verify_table_schema(db_path):
                    logger.info("Existing database has correct schema")
                    return
                else:
                    logger.info("Dropping existing tables due to schema mismatch")
                    db.drop_all()
            
            logger.info("Creating all tables with updated schema")
            db.create_all()
            
            # Verify the schema after creation
            if verify_table_schema(db_path):
                logger.info("Database initialization completed successfully")
            else:
                raise Exception("Failed to create tables with correct schema")
            
    except Exception as e:
        logger.error(f"Error during deployment: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    deploy() 