from datetime import datetime
from . import db

class Todo(db.Model):
    __tablename__ = 'todo'  # Explicitly set the table name
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        todo = cls(
            title=data['title'],
            description=data.get('description', ''),
            completed=data.get('completed', False),
            due_date=datetime.fromisoformat(data['due_date']) if 'due_date' in data else None
        )
        return todo 