from flask import Blueprint, request, jsonify
from .models import Todo
from . import db
from datetime import datetime

bp = Blueprint('todos', __name__)

@bp.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    return jsonify([todo.to_dict() for todo in todos])

@bp.route('/todos/<int:id>', methods=['GET'])
def get_todo(id):
    todo = Todo.query.get_or_404(id)
    return jsonify(todo.to_dict())

@bp.route('/todos', methods=['POST'])
def create_todo():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    
    if 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
    
    todo = Todo.from_dict(data)
    db.session.add(todo)
    db.session.commit()
    
    return jsonify(todo.to_dict()), 201

@bp.route('/todos/<int:id>', methods=['PUT'])
def update_todo(id):
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    todo = Todo.query.get_or_404(id)
    data = request.get_json()
    
    if 'title' in data:
        todo.title = data['title']
    if 'description' in data:
        todo.description = data['description']
    if 'due_date' in data:
        todo.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
    
    db.session.commit()
    return jsonify(todo.to_dict())

@bp.route('/todos/<int:id>', methods=['DELETE'])
def delete_todo(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    return '', 204 