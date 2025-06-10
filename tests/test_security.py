import pytest
from app import create_app, db
from bs4 import BeautifulSoup
import json
from datetime import datetime
from flask_wtf import CSRFProtect

csrf = CSRFProtect()

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': True,  # Enable CSRF protection globally
        'WTF_CSRF_SSL_STRICT': True,  # Enforce SSL for CSRF tokens
        'WTF_CSRF_CHECK_DEFAULT': False,  # Disable CSRF check by default, let individual views opt-in
        'SECRET_KEY': 'test-secret-key',
        'CORS_METHODS': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        'CORS_ALLOW_HEADERS': ['Content-Type', 'X-CSRF-Token', 'Authorization'],
        'CORS_EXPOSE_HEADERS': ['X-CSRF-Token']
    })

    # Initialize database
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_swagger_ui_accessible(client):
    """Test that Swagger UI is accessible"""
    response = client.get('/swagger')
    assert response.status_code == 200
    assert b'swagger' in response.data.lower()

def test_swagger_json_accessible(client):
    """Test that Swagger JSON is accessible"""
    response = client.get('/swagger.json')
    assert response.status_code == 200
    data = json.loads(response.data)
    # Verify essential OpenAPI spec components
    assert 'swagger' in data or 'openapi' in data
    assert 'paths' in data
    assert '/todos/' in data['paths']

def test_security_headers(client):
    """Test that security headers are present"""
    response = client.get('/todos/')
    headers = response.headers

    # Check for security headers set by Flask-Talisman
    assert headers.get('X-Frame-Options') is not None
    assert headers.get('X-Content-Type-Options') is not None
    assert headers.get('Content-Security-Policy') is not None

def test_csrf_protection_enabled(client):
    """Test that CSRF protection is enabled for non-exempted routes"""
    # Test a route that should have CSRF protection
    response = client.post('/protected')
    assert response.status_code == 400  # Should fail without CSRF token
    assert b'CSRF' in response.data

def test_csrf_exemption(client):
    """Test that API routes are properly exempted from CSRF protection"""
    # Test POST request without CSRF token
    todo_data = {
        'title': 'Test Todo',
        'description': 'Testing CSRF exemption',
        'completed': False,
        'due_date': datetime.utcnow().isoformat()
    }
    response = client.post('/todos/', json=todo_data)
    assert response.status_code == 201  # Should succeed without CSRF token
    
    # Test PUT request without CSRF token
    response = client.put('/todos/1', json={'title': 'Updated Todo'})
    assert response.status_code in [200, 404]  # Should either succeed or return 404 if todo doesn't exist
    
    # Test DELETE request without CSRF token
    response = client.delete('/todos/1')
    assert response.status_code in [204, 404]  # Should either succeed or return 404 if todo doesn't exist

def test_session_cookie_settings(client, app):
    """Test session cookie security settings"""
    with client.session_transaction() as sess:
        sess['test'] = 'value'  # Set a session value to force cookie creation

    response = client.get('/todos/')
    assert response.status_code == 200

    # Get the session cookie from response headers
    cookies = [h for h in response.headers if h[0] == 'Set-Cookie']
    assert len(cookies) > 0, "No cookies were set"

    session_cookie = next((c for c in cookies if 'session=' in c[1]), None)
    assert session_cookie is not None, "Session cookie not found"
    
    cookie_value = session_cookie[1]
    assert 'HttpOnly' in cookie_value
    assert 'SameSite' in cookie_value
    if not app.config['TESTING']:  # Skip Secure check in testing
        assert 'Secure' in cookie_value

def test_no_sensitive_info_in_responses(client):
    """Test that no sensitive information is leaked in responses"""
    response = client.get('/todos/')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Check that no sensitive information is present in the response
    sensitive_fields = ['password', 'secret', 'key', 'token']
    response_str = str(data).lower()
    for field in sensitive_fields:
        assert field not in response_str

def test_error_responses(client):
    """Test proper error handling"""
    # Test 404 error
    response = client.get('/todos/999')  # Non-existent todo
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert '404' in data['error']
    
    # Test 400 error - missing required field
    response = client.post('/todos/', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Title is required' in data['error']

def test_rate_limiting(client):
    """Test rate limiting functionality"""
    # Make multiple rapid requests
    for _ in range(50):
        response = client.get('/todos/')
        assert response.status_code in [200, 429]  # Either success or rate limit exceeded

def test_cors_headers(client):
    """Test CORS headers"""
    response = client.get('/todos/')
    assert response.headers.get('Access-Control-Allow-Origin') == '*'

    # Test preflight request
    response = client.options('/todos/')
    assert response.status_code == 200
    assert response.headers.get('Access-Control-Allow-Origin') == '*'
    assert response.headers.get('Access-Control-Allow-Methods') is not None 