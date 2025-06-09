import logging
from flask import Blueprint, jsonify, request
from flask_restx import Api, Resource, fields
from .models import Todo, db
from datetime import datetime
from werkzeug.exceptions import NotFound, BadRequest

logger = logging.getLogger(__name__)
bp = Blueprint('todos', __name__)
api = Api(bp,
    title='Todo API',
    version='1.0',
    description='A simple Todo API',
    doc='/swagger'
)

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

@api.errorhandler(NotFound)
def handle_404(e):
    logger.warning(f"404 error: {str(e)}")
    return {'error': str(e)}, 404

@api.errorhandler(BadRequest)
def handle_400(e):
    logger.warning(f"400 error: {str(e)}")
    return {'error': str(e)}, 400

@api.errorhandler(Exception)
def handle_500(e):
    logger.error(f"Unexpected error: {str(e)}", exc_info=True)
    return {'error': 'Internal server error'}, 500

@ns.route('/')
class TodoList(Resource):
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo_model)
    def get(self):
        """List all todos"""
        try:
            logger.info('Fetching all todos')
            todos = Todo.query.all()
            return todos
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
            return todo, 201
        except ValueError as e:
            logger.warning(f"Invalid data format: {str(e)}")
            raise BadRequest(f"Invalid data format: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating todo: {str(e)}", exc_info=True)
            raise

@ns.route('/<int:id>')
@ns.param('id', 'The todo identifier')
class TodoItem(Resource):
    @ns.doc('get_todo')
    @ns.marshal_with(todo_model)
    def get(self, id):
        """Get a specific todo"""
        try:
            logger.info(f'Fetching todo with id {id}')
            todo = Todo.query.get_or_404(id)
            return todo
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
            return todo
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