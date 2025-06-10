from datetime import datetime
from . import db
from sqlalchemy import CheckConstraint
from sqlalchemy.sql import text

class Todo(db.Model):
    __tablename__ = 'todo'  # Explicitly set the table name
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    completed = db.Column(db.Integer, default=0, nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    
    # Add check constraint to ensure completed is only 0 or 1
    __table_args__ = (
        CheckConstraint('completed IN (0, 1)', name='check_completed_boolean'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': bool(self.completed),  # Convert Integer to Boolean
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data['title'],
            description=data.get('description', ''),
            completed=1 if data.get('completed', False) else 0,  # Convert Boolean to Integer
            due_date=datetime.fromisoformat(data['due_date']) if 'due_date' in data and data['due_date'] else None
        )
    
    def __repr__(self):
        return f'<Todo {self.id}: {self.title}>' 