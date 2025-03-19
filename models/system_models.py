from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey

def ConfigModel(db):
    """Config model factory with correct db instance."""
    
    class Config(db.Model):
        """Model to store configuration values"""
        __tablename__ = 'config'
        
        id = Column(Integer, primary_key=True)
        key = Column(String(64), unique=True, nullable=False)
        value = Column(Text, nullable=True)
        
        def __repr__(self):
            return f'<Config {self.key}>'
        
        @classmethod
        def get_value(cls, key, default=None):
            """獲取配置值，如果不存在則返回默認值"""
            config = db.session.query(cls).filter_by(key=key).first()
            if config:
                return config.value
            return default
        
        @classmethod
        def set_value(cls, key, value):
            """設置配置值，如果不存在則創建新配置"""
            config = db.session.query(cls).filter_by(key=key).first()
            if config:
                config.value = value
            else:
                config = cls(key=key, value=value)
                db.session.add(config)
            db.session.commit()
    
    return Config

def LogEntryModel(db):
    """Log entry model factory with correct db instance."""
    
    class LogEntry(db.Model):
        """Model to store system logs"""
        __tablename__ = 'log_entry'
        
        id = Column(Integer, primary_key=True)
        level = Column(String(10), nullable=False)
        message = Column(Text, nullable=False)
        module = Column(String(64), nullable=False)
        timestamp = Column(DateTime, default=datetime.utcnow)
        
        def __repr__(self):
            return f'<LogEntry {self.id}>'
        
        @classmethod
        def log(cls, level, message, module):
            """創建新日誌條目"""
            log_entry = cls(level=level, message=message, module=module)
            db.session.add(log_entry)
            db.session.commit()
            return log_entry
    
    return LogEntry 