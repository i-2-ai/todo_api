import logging
from flask import Blueprint, jsonify, request, make_response, current_app, Response
from flask_restx import Api, Resource, fields
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_cors import CORS
from flask_talisman import Talisman
from werkzeug.wrappers import Response as WrapperResponse
from .models import Todo, db
from datetime import datetime
from werkzeug.exceptions import NotFound, BadRequest
from functools import wraps

logger = logging.getLogger(__name__)
bp = Blueprint('todos', __name__)
csrf = CSRFProtect()
talisman = Talisman()

# Initialize Flask-RESTX with Swagger UI
api = Api(bp,
    title='Todo API',
    version='1.0',
    description='A secure Todo API',
    doc='/swagger',
    authorizations={
        'apikey': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-API-KEY'
        }
    }
)

# Exempt all Blueprint routes from CSRF protection
csrf.exempt(bp)

# Enable CORS for the API
CORS(bp, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "X-CSRF-Token", "Authorization"],
        "expose_headers": ["X-CSRF-Token"]
    }
})

# Define the namespace for todos
ns = api.namespace('todos', description='Todo operations')

# Define models for swagger documentation
todo_model = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The todo unique identifier'),
    'title': fields.String(required=True, description='The todo title'),
    'description': fields.String(description='The todo description'),
    'completed': fields.Boolean(description='The todo completion status'),
    'due_date': fields.DateTime(description='The todo due date'),
    'created_at': fields.DateTime(readonly=True, description='The creation date')
})

todo_input = api.model('TodoInput', {
    'title': fields.String(required=True, description='The todo title'),
    'description': fields.String(description='The todo description'),
    'completed': fields.Boolean(description='The todo completion status'),
    'due_date': fields.DateTime(description='The todo due date')
})

@bp.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    logger.warning(f"Resource not found: {request.url}")
    return {'error': str(e)}, 404

@bp.errorhandler(400)
def bad_request(e):
    """Handle 400 errors"""
    logger.warning(f"Bad request: {str(e)}")
    return {'error': str(e)}, 400

@bp.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(e)}", exc_info=True)
    return {'error': str(e)}, 500

def add_csrf_token(response):
    """Add CSRF token to response headers"""
    if not isinstance(response, (Response, WrapperResponse)):
        response = make_response(response)
    token = generate_csrf()
    response.headers['X-CSRF-Token'] = token
    return response

def add_cors_headers(response):
    """Add CORS headers to response"""
    if not isinstance(response, (Response, WrapperResponse)):
        response = make_response(response)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRF-Token, Authorization'
    response.headers['Access-Control-Expose-Headers'] = 'X-CSRF-Token'
    return response

def add_response_headers(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'OPTIONS':
            response = make_response()
            response.status_code = 200
            response = add_cors_headers(response)
            return response

        response = f(*args, **kwargs)
        if isinstance(response, tuple):
            response = make_response(jsonify(response[0]), response[1])
        elif not isinstance(response, (Response, WrapperResponse)):
            response = make_response(jsonify(response))
        
        # Add CSRF token and CORS headers
        response = add_csrf_token(response)
        response = add_cors_headers(response)
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response
    return decorated_function

@ns.route('/')
class TodoList(Resource):
    method_decorators = [add_response_headers]

    @ns.doc('list_todos')
    @ns.marshal_list_with(todo_model)
    def get(self):
        """List all todos"""
        try:
            logger.info('Fetching all todos')
            todos = Todo.query.all()
            return [todo.to_dict() for todo in todos]
        except Exception as e:
            logger.error(f"Error fetching todos: {str(e)}", exc_info=True)
            raise

    @ns.doc('create_todo')
    @ns.expect(todo_input)
    @ns.marshal_with(todo_model, code=201)
    def post(self):
        """Create a new todo"""
        try:
            logger.info('Creating new todo')
            data = request.get_json()
            
            if not data or 'title' not in data:
                raise BadRequest("Title is required")
                
            todo = Todo(
                title=data['title'],
                description=data.get('description', ''),
                due_date=datetime.fromisoformat(data['due_date']) if 'due_date' in data else None,
                completed=data.get('completed', False)
            )
            
            db.session.add(todo)
            db.session.commit()
            logger.info(f"Created todo with id {todo.id}")
            
            return todo.to_dict(), 201
        except ValueError as e:
            logger.warning(f"Invalid data format: {str(e)}")
            raise BadRequest(f"Invalid data format: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating todo: {str(e)}", exc_info=True)
            raise

@ns.route('/<int:id>')
@ns.param('id', 'The todo identifier')
class TodoItem(Resource):
    method_decorators = [add_response_headers]

    @ns.doc('get_todo')
    @ns.marshal_with(todo_model)
    def get(self, id):
        """Get a specific todo"""
        try:
            logger.info(f'Fetching todo with id {id}')
            todo = Todo.query.get_or_404(id)
            return todo.to_dict()
        except Exception as e:
            logger.error(f"Error fetching todo {id}: {str(e)}", exc_info=True)
            raise

    @ns.doc('update_todo')
    @ns.expect(todo_input)
    @ns.marshal_with(todo_model)
    def put(self, id):
        """Update a todo"""
        try:
            logger.info(f'Updating todo with id {id}')
            todo = Todo.query.get_or_404(id)
            data = request.get_json()
            
            if 'title' in data:
                todo.title = data['title']
            if 'description' in data:
                todo.description = data['description']
            if 'due_date' in data:
                todo.due_date = datetime.fromisoformat(data['due_date'])
            if 'completed' in data:
                todo.completed = data['completed']
                
            db.session.commit()
            logger.info(f"Updated todo {id}")
            
            return todo.to_dict()
        except ValueError as e:
            logger.warning(f"Invalid data format: {str(e)}")
            raise BadRequest(f"Invalid data format: {str(e)}")
        except Exception as e:
            logger.error(f"Error updating todo {id}: {str(e)}", exc_info=True)
            raise

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        """Delete a todo"""
        try:
            logger.info(f'Deleting todo with id {id}')
            todo = Todo.query.get_or_404(id)
            db.session.delete(todo)
            db.session.commit()
            logger.info(f"Deleted todo {id}")
            
            return '', 204
        except Exception as e:
            logger.error(f"Error deleting todo {id}: {str(e)}", exc_info=True)
            raise

# Add a test route for CSRF protection testing
@bp.route('/protected', methods=['POST'])
def protected_route():
    """A route that requires CSRF protection"""
    csrf = current_app.extensions['csrf']
    csrf.protect()  # Explicitly enable CSRF protection for this route
    return jsonify({'message': 'CSRF protection is working'}), 200

# Add a before_request handler for OPTIONS requests
@bp.before_request
def handle_options():
    if request.method == 'OPTIONS':
        response = make_response()
        response.status_code = 200
        response = add_cors_headers(response)
        return response 

# Register error handlers for the API
@ns.errorhandler(Exception)
def handle_error(e):
    """Handle all API errors"""
    code = getattr(e, 'code', 500)
    if hasattr(e, 'data'):
        return {'error': str(e.data['message'])}, code
    return {'error': str(e)}, code 