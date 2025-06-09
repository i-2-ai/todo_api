import logging
from flask import Blueprint, jsonify, request
from .models import Todo, db
from datetime import datetime
from werkzeug.exceptions import NotFound, BadRequest

logger = logging.getLogger(__name__)
bp = Blueprint('todos', __name__)

@bp.errorhandler(NotFound)
def handle_404(e):
    logger.warning(f"404 error: {str(e)}")
    return jsonify(error=str(e)), 404

@bp.errorhandler(BadRequest)
def handle_400(e):
    logger.warning(f"400 error: {str(e)}")
    return jsonify(error=str(e)), 400

@bp.errorhandler(Exception)
def handle_500(e):
    logger.error(f"Unexpected error: {str(e)}", exc_info=True)
    return jsonify(error="Internal server error"), 500

@bp.route('/todos', methods=['GET'])
def get_todos():
    try:
        logger.info('Fetching all todos')
        todos = Todo.query.all()
        return jsonify([todo.to_dict() for todo in todos])
    except Exception as e:
        logger.error(f"Error fetching todos: {str(e)}", exc_info=True)
        raise

@bp.route('/todos', methods=['POST'])
def create_todo():
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
        return jsonify(todo.to_dict()), 201
    except ValueError as e:
        logger.warning(f"Invalid data format: {str(e)}")
        raise BadRequest(f"Invalid data format: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating todo: {str(e)}", exc_info=True)
        raise

@bp.route('/todos/<int:id>', methods=['GET'])
def get_todo(id):
    try:
        logger.info(f'Fetching todo with id {id}')
        todo = Todo.query.get_or_404(id)
        return jsonify(todo.to_dict())
    except Exception as e:
        logger.error(f"Error fetching todo {id}: {str(e)}", exc_info=True)
        raise

@bp.route('/todos/<int:id>', methods=['PUT'])
def update_todo(id):
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
        return jsonify(todo.to_dict())
    except ValueError as e:
        logger.warning(f"Invalid data format: {str(e)}")
        raise BadRequest(f"Invalid data format: {str(e)}")
    except Exception as e:
        logger.error(f"Error updating todo {id}: {str(e)}", exc_info=True)
        raise

@bp.route('/todos/<int:id>', methods=['DELETE'])
def delete_todo(id):
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