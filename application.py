from app import create_app
import os

# Configure the application for Azure
app = create_app({
    'SQLALCHEMY_DATABASE_URI': f'sqlite:///{os.path.join(os.environ.get("HOME", "/home/site/wwwroot"), "todos.db")}',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
})

if __name__ == '__main__':
    app.run() 