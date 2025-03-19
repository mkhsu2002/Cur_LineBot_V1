from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

def ChatMessageModel(db):
    """Chat message model factory with correct db instance."""
    
    class ChatMessage(db.Model):
        """Model to store chat message history"""
        __tablename__ = 'chat_message'
        
        id = Column(Integer, primary_key=True)
        line_user_id = Column(String(64), ForeignKey('line_user.line_user_id'), nullable=False)
        is_user_message = Column(Boolean, default=True)
        message_text = Column(Text, nullable=False)
        bot_style = Column(String(64), ForeignKey('bot_style.name'), nullable=True)
        timestamp = Column(DateTime, default=datetime.utcnow)
        
        # 關聯會在初始化後設置
        line_user = None
        style = None
        
        def __repr__(self):
            return f'<ChatMessage {self.id}>'
    
    return ChatMessage

def BotStyleModel(db):
    """Bot style model factory with correct db instance."""
    
    class BotStyle(db.Model):
        """Model to store different bot response styles"""
        __tablename__ = 'bot_style'
        
        id = Column(Integer, primary_key=True)
        name = Column(String(64), unique=True, nullable=False)
        prompt = Column(Text, nullable=False)
        description = Column(Text, nullable=True)
        is_default = Column(Boolean, default=False)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # 關聯會在初始化後設置
        messages = None
        
        def __repr__(self):
            return f'<BotStyle {self.name}>'
    
    return BotStyle 