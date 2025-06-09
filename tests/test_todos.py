import pytest
from app import create_app, db
from app.models import Todo
import json
from datetime import datetime, timedelta

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_database(app):
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

def test_create_todo(client, init_database):
    response = client.post('/api/todos',
        json={
            'title': 'Test Todo',
            'description': 'Test Description',
            'due_date': (datetime.utcnow() + timedelta(days=1)).isoformat()
        }
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == 'Test Todo'
    assert data['description'] == 'Test Description'

def test_get_todos(client, init_database):
    # Create a test todo
    todo = Todo(title='Test Todo', description='Test Description')
    init_database.session.add(todo)
    init_database.session.commit()

    response = client.get('/api/todos')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['title'] == 'Test Todo'

def test_get_todo(client, init_database):
    # Create a test todo
    todo = Todo(title='Test Todo', description='Test Description')
    init_database.session.add(todo)
    init_database.session.commit()

    response = client.get(f'/api/todos/{todo.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == 'Test Todo'

def test_update_todo(client, init_database):
    # Create a test todo
    todo = Todo(title='Test Todo', description='Test Description')
    init_database.session.add(todo)
    init_database.session.commit()

    response = client.put(f'/api/todos/{todo.id}',
        json={
            'title': 'Updated Todo',
            'description': 'Updated Description'
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == 'Updated Todo'
    assert data['description'] == 'Updated Description'

def test_delete_todo(client, init_database):
    # Create a test todo
    todo = Todo(title='Test Todo', description='Test Description')
    init_database.session.add(todo)
    init_database.session.commit()

    response = client.delete(f'/api/todos/{todo.id}')
    assert response.status_code == 204

    # Verify todo is deleted
    response = client.get(f'/api/todos/{todo.id}')
    assert response.status_code == 404 