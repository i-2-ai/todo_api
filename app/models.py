from datetime import datetime
from . import db
from sqlalchemy import Boolean, Integer, String, DateTime

class Todo(db.Model):
    __tablename__ = 'todo'  # Explicitly set the table name
    
    id = db.Column(Integer, primary_key=True)
    title = db.Column(String(100), nullable=False)
    description = db.Column(String(500))
    completed = db.Column(Integer, default=0)  # Using Integer instead of Boolean for SQLite compatibility
    due_date = db.Column(DateTime)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
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
        todo = cls(
            title=data['title'],
            description=data.get('description', ''),
            completed=1 if data.get('completed', False) else 0,  # Convert Boolean to Integer
            due_date=datetime.fromisoformat(data['due_date']) if 'due_date' in data else None
        )
        return todo 