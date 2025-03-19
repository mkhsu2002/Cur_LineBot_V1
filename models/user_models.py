from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

def UserModel(db):
    """User model factory with correct db instance."""
    
    class User(db.Model, UserMixin):
        """User model for authentication and admin panel access"""
        __tablename__ = 'user'
        
        id = Column(Integer, primary_key=True)
        username = Column(String(64), unique=True, nullable=False)
        email = Column(String(120), unique=True, nullable=False)
        password_hash = Column(String(256), nullable=False)
        is_admin = Column(Boolean, default=False)
        created_at = Column(DateTime, default=datetime.utcnow)
        
        def __repr__(self):
            return f'<User {self.username}>'
    
    return User

def LineUserModel(db):
    """LINE user model factory with correct db instance."""
    
    class LineUser(db.Model):
        """Model to store LINE user information"""
        __tablename__ = 'line_user'
        
        id = Column(Integer, primary_key=True)
        line_user_id = Column(String(64), unique=True, nullable=False)
        display_name = Column(String(64), nullable=True)
        picture_url = Column(String(256), nullable=True)
        status_message = Column(String(256), nullable=True)
        active_style = Column(String(64), nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        last_interaction = Column(DateTime, default=datetime.utcnow)
    
        def __repr__(self):
            return f'<LineUser {self.line_user_id}>'
    
    return LineUser 