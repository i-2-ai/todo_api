from flask import Blueprint, request, jsonify, abort
from werkzeug.exceptions import NotFound
from .models import Todo
from . import db
from datetime import datetime
import logging

bp = Blueprint('todos', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

@bp.route('/todos', methods=['GET'])
def get_todos():
    try:
        logger.info('Fetching all todos')
        todos = Todo.query.all()
        return jsonify([todo.to_dict() for todo in todos])
    except Exception as e:
        logger.error(f'Error fetching todos: {str(e)}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/todos', methods=['POST'])
def create_todo():
    try:
        logger.info('Creating new todo')
        data = request.get_json()
        
        if not data or 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400
            
        todo = Todo.from_dict(data)
        db.session.add(todo)
        db.session.commit()
        
        return jsonify(todo.to_dict()), 201
    except Exception as e:
        logger.error(f'Error creating todo: {str(e)}', exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/todos/<int:id>', methods=['GET'])
def get_todo(id):
    try:
        logger.info(f'Fetching todo with id {id}')
        todo = Todo.query.get_or_404(id)
        return jsonify(todo.to_dict())
    except NotFound:
        raise
    except Exception as e:
        logger.error(f'Error fetching todo {id}: {str(e)}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

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
        if 'completed' in data:
            todo.completed = data['completed']
        if 'due_date' in data:
            todo.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
            
        db.session.commit()
        return jsonify(todo.to_dict())
    except NotFound:
        raise
    except Exception as e:
        logger.error(f'Error updating todo {id}: {str(e)}', exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/todos/<int:id>', methods=['DELETE'])
def delete_todo(id):
    try:
        logger.info(f'Deleting todo with id {id}')
        todo = Todo.query.get_or_404(id)
        db.session.delete(todo)
        db.session.commit()
        return '', 204
    except NotFound:
        raise
    except Exception as e:
        logger.error(f'Error deleting todo {id}: {str(e)}', exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500 