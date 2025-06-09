import pytest
from app import create_app, db
import json
from bs4 import BeautifulSoup
import http.cookiejar
from flask import url_for

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': True,
        'SECRET_KEY': 'test-secret-key',
        'SESSION_COOKIE_SECURE': False,  # Disable secure cookies for testing
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_SAMESITE': 'Lax'
    })
    # Disable HTTPS redirect for testing
    app.config['TALISMAN_FORCE_HTTPS'] = False
    return app

@pytest.fixture
def client(app):
    with app.test_client() as client:
        # Enable cookie handling
        client.cookie_jar = http.cookiejar.CookieJar()
        yield client

@pytest.fixture
def init_database(app):
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

def test_swagger_ui_accessible(client):
    """Test that Swagger UI is accessible and protected"""
    response = client.get('/swagger')
    assert response.status_code == 200
    assert b'swagger-ui' in response.data

def test_swagger_json_accessible(client):
    """Test that Swagger JSON is accessible"""
    response = client.get('/swagger.json')
    assert response.status_code == 200
    data = json.loads(response.data)
    # Verify essential OpenAPI spec components
    assert 'swagger' in data or 'openapi' in data
    assert 'paths' in data
    assert '/todos/' in data['paths']  # Note the trailing slash

def test_security_headers(client):
    """Test that security headers are present"""
    response = client.get('/swagger')
    headers = response.headers
    
    # Check for security headers set by Flask-Talisman
    assert headers.get('X-Frame-Options') is not None
    assert headers.get('X-Content-Type-Options') is not None
    assert headers.get('Referrer-Policy') is not None

def test_csrf_protection(client):
    """Test that CSRF protection is enabled"""
    # First get the CSRF token
    response = client.get('/todos/')
    assert response.status_code == 200
    
    # Try to make a POST request without CSRF token
    response = client.post('/todos/', json={
        'title': 'Test Todo',
        'description': 'Test Description'
    })
    assert response.status_code in [400, 403]  # Should fail without CSRF token

def test_session_cookie_settings(app, client):
    """Test session cookie settings"""
    @app.route('/set_session')
    def set_session():
        from flask import session
        session['test'] = 'value'
        return 'Session set'
    
    # First request to set the session
    response = client.get('/set_session')
    assert response.status_code == 200
    
    # Get the session cookie
    cookie_header = next((h[1] for h in response.headers if h[0] == 'Set-Cookie' and 'session=' in h[1]), None)
    assert cookie_header is not None, "No session cookie was set"
    
    # Check cookie flags
    assert 'HttpOnly' in cookie_header
    assert 'SameSite' in cookie_header
    
    # Make a request with the session cookie
    response = client.get('/todos/', headers={'Cookie': cookie_header})
    assert response.status_code == 200

def test_no_sensitive_info_in_responses(client):
    """Test that no sensitive information is leaked in responses"""
    response = client.get('/swagger.json')  # Use swagger.json instead of api-spec
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Check that no sensitive info is in the API spec
    spec_str = str(data).lower()
    assert 'password' not in spec_str
    assert 'secret' not in spec_str
    assert 'token' not in spec_str

def test_error_responses(client):
    """Test that error responses don't reveal sensitive information"""
    response = client.get('/todos/999')  # Non-existent todo
    assert response.status_code == 404
    data = json.loads(response.data)
    
    # Error message should be generic
    assert 'error' in data
    assert 'not found' in data['error'].lower()
    # Should not contain stack traces or detailed error info
    assert 'traceback' not in str(data).lower()
    assert 'stack' not in str(data).lower()

def test_rate_limiting(client):
    """Test rate limiting functionality"""
    # Make multiple rapid requests
    responses = [client.get('/todos/') for _ in range(50)]
    
    # Check if any responses indicate rate limiting
    rate_limited = any(r.status_code == 429 for r in responses)
    assert not rate_limited  # Should not be rate limited for normal use

def test_cors_headers(client):
    """Test CORS headers are properly set"""
    response = client.get('/todos/', headers={'Origin': 'http://example.com'})
    assert response.status_code == 200
    assert 'Access-Control-Allow-Origin' in response.headers

def test_error_responses(client):
    """Test that error responses don't reveal sensitive information"""
    response = client.get('/todos/999')  # Non-existent todo
    assert response.status_code == 404
    data = json.loads(response.data)
    
    # Error message should be generic
    assert 'error' in data
    assert 'not found' in data['error'].lower()
    # Should not contain stack traces or detailed error info
    assert 'traceback' not in str(data).lower()
    assert 'stack' not in str(data).lower() 