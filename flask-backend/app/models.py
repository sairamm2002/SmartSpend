from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db
import json

from .ai_models import Prediction, Forecast, Heatmap, Comparison, Anomaly, Insight, Recommendation

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add missing fields for preferences
    currency = db.Column(db.String(3), default='USD')
    language = db.Column(db.String(10), default='en')
    theme = db.Column(db.String(10), default='light')
    
    # Optional profile fields
    display_name = db.Column(db.String(80), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    avatar = db.Column(db.String(200), nullable=True)

    # All relationships with back_populates
    expenses = db.relationship('Expense', back_populates='user', lazy=True, cascade='all, delete-orphan')
    categories = db.relationship('Category', back_populates='user', lazy=True, cascade='all, delete-orphan')
    budgets = db.relationship('Budget', back_populates='user', lazy=True, cascade='all, delete-orphan')
    recurring_rules = db.relationship('RecurringRule', back_populates='user', lazy=True, cascade='all, delete-orphan')
    goals = db.relationship('Goal', back_populates='user', lazy=True, cascade='all, delete-orphan')
    debts = db.relationship('Debt', back_populates='user', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', back_populates='user', lazy=True, cascade='all, delete-orphan')
    import_history = db.relationship('ImportHistory', back_populates='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'display_name': self.display_name,
            'bio': self.bio,
            'avatar': self.avatar,
            'currency': self.currency,
            'language': self.language,
            'theme': self.theme,
            'created_at': self.created_at.isoformat() if self.created_at else None
 }
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default='#3b82f6')
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='categories')  # ADD THIS LINE
    expenses = db.relationship('Expense', back_populates='category', lazy=True)
    recurring_rules = db.relationship('RecurringRule', back_populates='category', lazy=True)

    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='unique_user_category'),)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'color': self.color,
            'is_default': self.is_default
        }
class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='expenses')
    category = db.relationship('Category', back_populates='expenses')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'category_color': self.category.color if self.category else None,
            'amount': float(self.amount),
            'description': self.description,
            'date': self.date.isoformat()
        }

class Budget(db.Model):
    __tablename__ = 'budgets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = db.relationship('User', back_populates='budgets')

    __table_args__ = (db.UniqueConstraint('user_id', 'month', 'year', name='unique_user_budget'),)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'month': self.month,
            'year': self.year,
            'amount': float(self.amount)
        }

class RecurringRule(db.Model):
    __tablename__ = 'recurring_rules'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    description = db.Column(db.String(200))
    frequency = db.Column(db.String(20), nullable=False)
    interval = db.Column(db.Integer, default=1)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    next_date = db.Column(db.Date, nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships - use back_populates instead of backref to avoid conflicts
    user = db.relationship('User', back_populates='recurring_rules')
    category = db.relationship('Category', back_populates='recurring_rules')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'category_color': self.category.color if self.category else None,
            'amount': float(self.amount),
            'description': self.description,
            'frequency': self.frequency,
            'interval': self.interval,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'next_date': self.next_date.isoformat(),
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Goal(db.Model):
    __tablename__ = 'goals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Numeric(10,2), nullable=False)
    current_amount = db.Column(db.Numeric(10,2), default=0.0)
    deadline = db.Column(db.Date, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship('User', back_populates='goals')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'target_amount': float(self.target_amount),
            'current_amount': float(self.current_amount),
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'completed': self.completed,
            'progress': (float(self.current_amount) / float(self.target_amount) * 100) if self.target_amount else 0
        }

class Debt(db.Model):
    __tablename__ = 'debts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    person = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    is_owed = db.Column(db.Boolean, default=True)
    description = db.Column(db.String(200))
    due_date = db.Column(db.Date, nullable=True)
    settled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship('User', back_populates='debts')

    def to_dict(self):
        return {
            'id': self.id,
            'person': self.person,
            'amount': float(self.amount),
            'is_owed': self.is_owed,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'settled': self.settled
        }

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship('User', back_populates='notifications')

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'message': self.message,
            'read': self.read,
            'created_at': self.created_at.isoformat()
        }

class ImportHistory(db.Model):
    __tablename__ = 'import_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    record_count = db.Column(db.Integer, default=0)
    error_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='success')
    errors = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', back_populates='import_history')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'record_count': self.record_count,
            'error_count': self.error_count,
            'status': self.status,
            'errors': json.loads(self.errors) if self.errors else [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }