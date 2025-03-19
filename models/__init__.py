"""
Models package initializer.
This file helps avoid circular imports by providing a central place to import all models.
"""

# These will be populated when db_init is called
User = None
LineUser = None
ChatMessage = None
BotStyle = None
Config = None
Document = None
DocumentChunk = None
LogEntry = None

def init_models(db):
    """Initialize all models with the database instance to avoid circular imports."""
    
    # Import the model definitions
    from .user_models import UserModel, LineUserModel
    from .chat_models import ChatMessageModel, BotStyleModel
    from .document_models import DocumentModel, DocumentChunkModel
    from .system_models import ConfigModel, LogEntryModel
    
    # Set global models
    global User, LineUser, ChatMessage, BotStyle, Config, Document, DocumentChunk, LogEntry
    
    User = UserModel(db)
    LineUser = LineUserModel(db)
    ChatMessage = ChatMessageModel(db)
    BotStyle = BotStyleModel(db)
    Config = ConfigModel(db)
    Document = DocumentModel(db)
    DocumentChunk = DocumentChunkModel(db)
    LogEntry = LogEntryModel(db)
    
    # 建立模型間的關聯關係
    
    # ChatMessage 關聯
    ChatMessage.line_user = db.relationship("LineUser", back_populates="messages", 
                                          foreign_keys=[ChatMessage.line_user_id])
    ChatMessage.style = db.relationship("BotStyle", back_populates="messages", 
                                      foreign_keys=[ChatMessage.bot_style])
    
    # LineUser 關聯
    LineUser.messages = db.relationship("ChatMessage", back_populates="line_user", 
                                       cascade="all, delete-orphan")
    
    # BotStyle 關聯
    BotStyle.messages = db.relationship("ChatMessage", back_populates="style")
    
    # Document 關聯
    Document.chunks = db.relationship("DocumentChunk", back_populates="document", 
                                     cascade="all, delete-orphan")
    
    # DocumentChunk 關聯
    DocumentChunk.document = db.relationship("Document", back_populates="chunks")
    
    # Return all models for convenience
    return {
        'User': User,
        'LineUser': LineUser,
        'ChatMessage': ChatMessage,
        'BotStyle': BotStyle,
        'Config': Config,
        'Document': Document,
        'DocumentChunk': DocumentChunk,
        'LogEntry': LogEntry
    } 