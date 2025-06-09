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
    test_data = {
        'title': 'Test Todo',
        'description': 'Test Description',
        'completed': False,
        'due_date': (datetime.utcnow() + timedelta(days=1)).isoformat()
    }
    response = client.post('/api/todos', json=test_data)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == test_data['title']
    assert data['description'] == test_data['description']
    assert data['completed'] == test_data['completed']

def test_get_todos(client, init_database):
    # Create a test todo
    todo = Todo.from_dict({
        'title': 'Test Todo',
        'description': 'Test Description',
        'completed': False
    })
    init_database.session.add(todo)
    init_database.session.commit()

    response = client.get('/api/todos')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['title'] == todo.title
    assert data[0]['completed'] == todo.completed

def test_get_todo(client, init_database):
    # Create a test todo
    todo = Todo.from_dict({
        'title': 'Test Todo',
        'description': 'Test Description',
        'completed': False
    })
    init_database.session.add(todo)
    init_database.session.commit()

    response = client.get(f'/api/todos/{todo.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == todo.title
    assert data['completed'] == todo.completed

def test_update_todo(client, init_database):
    # Create a test todo
    todo = Todo.from_dict({
        'title': 'Test Todo',
        'description': 'Test Description',
        'completed': False
    })
    init_database.session.add(todo)
    init_database.session.commit()

    update_data = {
        'title': 'Updated Todo',
        'description': 'Updated Description',
        'completed': True
    }
    response = client.put(f'/api/todos/{todo.id}', json=update_data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == update_data['title']
    assert data['description'] == update_data['description']
    assert data['completed'] == update_data['completed']

def test_delete_todo(client, init_database):
    # Create a test todo
    todo = Todo.from_dict({
        'title': 'Test Todo',
        'description': 'Test Description',
        'completed': False
    })
    init_database.session.add(todo)
    init_database.session.commit()

    response = client.delete(f'/api/todos/{todo.id}')
    assert response.status_code == 204

    # Verify todo is deleted
    response = client.get(f'/api/todos/{todo.id}')
    assert response.status_code == 404 