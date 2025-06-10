import pytest
from app import create_app, db
from app.models import Todo
import json
from datetime import datetime

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': True,
        'SECRET_KEY': 'test-secret-key'
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

@pytest.fixture
def csrf_token(client):
    """Get a CSRF token for testing"""
    response = client.get('/todos/')
    csrf_token = response.headers.get('X-CSRF-Token')
    if not csrf_token:
        raise ValueError("CSRF token not found in response headers")
    return csrf_token

def test_create_todo(client, init_database, csrf_token):
    """Test creating a new todo"""
    todo_data = {
        'title': 'Test Todo',
        'description': 'Test Description',
        'completed': False,
        'due_date': datetime.utcnow().isoformat()
    }
    response = client.post('/todos/',
        json=todo_data,
        headers={'X-CSRF-Token': csrf_token}
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == todo_data['title']
    assert data['description'] == todo_data['description']
    assert data['completed'] == todo_data['completed']

def test_get_todos(client, init_database):
    """Test getting all todos"""
    # Create a test todo
    todo = Todo.from_dict({
        'title': 'Test Todo',
        'description': 'Test Description',
        'completed': False
    })
    init_database.session.add(todo)
    init_database.session.commit()

    response = client.get('/todos/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['title'] == todo.title
    assert data[0]['description'] == todo.description
    assert data[0]['completed'] == todo.completed

def test_get_todo(client, init_database):
    """Test getting a specific todo"""
    # Create a test todo
    todo = Todo.from_dict({
        'title': 'Test Todo',
        'description': 'Test Description',
        'completed': False
    })
    init_database.session.add(todo)
    init_database.session.commit()

    response = client.get(f'/todos/{todo.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == todo.title
    assert data['description'] == todo.description
    assert data['completed'] == todo.completed

def test_update_todo(client, init_database, csrf_token):
    """Test updating a todo"""
    # Create a test todo
    todo = Todo.from_dict({
        'title': 'Test Todo',
        'description': 'Test Description',
        'completed': False
    })
    init_database.session.add(todo)
    init_database.session.commit()

    # Update the todo
    update_data = {
        'title': 'Updated Todo',
        'description': 'Updated Description',
        'completed': True
    }
    response = client.put(f'/todos/{todo.id}',
        json=update_data,
        headers={'X-CSRF-Token': csrf_token}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == update_data['title']
    assert data['description'] == update_data['description']
    assert data['completed'] == update_data['completed']

def test_delete_todo(client, init_database, csrf_token):
    """Test deleting a todo"""
    # Create a test todo
    todo = Todo.from_dict({
        'title': 'Test Todo',
        'description': 'Test Description',
        'completed': False
    })
    init_database.session.add(todo)
    init_database.session.commit()

    response = client.delete(f'/todos/{todo.id}',
        headers={'X-CSRF-Token': csrf_token}
    )
    assert response.status_code == 204

    # Verify the todo was deleted
    response = client.get(f'/todos/{todo.id}')
    assert response.status_code == 404 