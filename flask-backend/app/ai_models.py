from .extensions import db
from datetime import datetime
import json

class Prediction(db.Model):
    """Store AI-generated spending predictions"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    predicted_amount = db.Column(db.Numeric(10,2), nullable=False)
    confidence = db.Column(db.String(20), default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Store prediction details as JSON
    details = db.Column(db.Text)  # JSON string with category predictions
    
    user = db.relationship('User', backref='predictions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'month': self.month,
            'year': self.year,
            'predicted_amount': float(self.predicted_amount),
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'details': json.loads(self.details) if self.details else {}
        }

class Forecast(db.Model):
    """Store forecast data for charts"""
    __tablename__ = 'forecasts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    forecast_date = db.Column(db.DateTime, default=datetime.utcnow)
    months = db.Column(db.Integer, nullable=False)
    
    # Store historical and forecast data as JSON
    historical_data = db.Column(db.Text)  # JSON array of historical points
    forecast_data = db.Column(db.Text)    # JSON array of forecast points
    forecast_metadata = db.Column(db.Text)  # JSON object with metadata
    
    user = db.relationship('User', backref='forecasts')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'forecast_date': self.forecast_date.isoformat() if self.forecast_date else None,
            'months': self.months,
            'historical': json.loads(self.historical_data) if self.historical_data else [],
            'forecast': json.loads(self.forecast_data) if self.forecast_data else [],
            'metadata': json.loads(self.forecast_metadata) if self.forecast_metadata else {}
        }

class Heatmap(db.Model):
    """Store heatmap data for spending visualization"""
    __tablename__ = 'heatmaps'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Store heatmap data as JSON
    heatmap_data = db.Column(db.Text)  # JSON array of heatmap points
    heatmap_metadata = db.Column(db.Text)  # JSON object with metadata
    
    user = db.relationship('User', backref='heatmaps')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'year', 'month', name='unique_user_heatmap'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'year': self.year,
            'month': self.month,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'data': json.loads(self.heatmap_data) if self.heatmap_data else [],
            'metadata': json.loads(self.heatmap_metadata) if self.heatmap_metadata else {}
        }

class Comparison(db.Model):
    """Store comparative analysis data"""
    __tablename__ = 'comparisons'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    period1 = db.Column(db.String(50), nullable=False)  # e.g., 'this_month', 'last_month', or date range
    period2 = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Store comparison data as JSON
    period1_data = db.Column(db.Text)   # JSON object with period1 details
    period2_data = db.Column(db.Text)   # JSON object with period2 details
    comparison_data = db.Column(db.Text) # JSON object with comparison results
    
    user = db.relationship('User', backref='comparisons')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'period1': self.period1,
            'period2': self.period2,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'period1_data': json.loads(self.period1_data) if self.period1_data else {},
            'period2_data': json.loads(self.period2_data) if self.period2_data else {},
            'comparison': json.loads(self.comparison_data) if self.comparison_data else {}
        }

class Anomaly(db.Model):
    """Store detected anomalies"""
    __tablename__ = 'anomalies'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    amount = db.Column(db.Numeric(10,2), nullable=True)
    date = db.Column(db.Date, nullable=True)
    description = db.Column(db.String(200), nullable=True)
    reason = db.Column(db.Text)
    severity = db.Column(db.String(20), default='medium')  # high/medium/low
    is_reviewed = db.Column(db.Boolean, default=False)
    detected_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='anomalies')
    expense = db.relationship('Expense', backref='anomalies')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'expense_id': self.expense_id,
            'category': self.category,
            'amount': float(self.amount) if self.amount else None,
            'date': self.date.isoformat() if self.date else None,
            'description': self.description,
            'reason': self.reason,
            'severity': self.severity,
            'is_reviewed': self.is_reviewed,
            'detected_date': self.detected_date.isoformat() if self.detected_date else None
        }

class Insight(db.Model):
    """Store AI-generated insights"""
    __tablename__ = 'insights'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50))  # savings/budget/pattern/alert
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    action = db.Column(db.String(200))
    priority = db.Column(db.Integer, default=1)  # 1-5
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='insights')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'description': self.description,
            'action': self.action,
            'priority': self.priority,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Recommendation(db.Model):
    """Store personalized recommendations"""
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50))  # FIXED: was db.Column.db.String(50)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    action_text = db.Column(db.String(100))
    action_link = db.Column(db.String(200))
    impact = db.Column(db.String(50))  # high/medium/low
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    user = db.relationship('User', backref='recommendations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'action_text': self.action_text,
            'action_link': self.action_link,
            'impact': self.impact,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }