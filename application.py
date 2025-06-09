import os
import sys
import logging

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # Configure the application for Azure
    app = create_app({
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{os.path.join(os.environ.get("HOME", "/home/site/wwwroot"), "todos.db")}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
    logger.info("Application created successfully")
except Exception as e:
    logger.error(f"Error creating application: {str(e)}", exc_info=True)
    raise

if __name__ == '__main__':
    app.run() 