import os
import logging
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from app import create_app, db

# 配置日誌
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

def init_db():
    """初始化資料庫：創建表格和初始數據"""
    logger.info("開始初始化資料庫...")
    
    # 創建應用實例
    app = create_app()
    
    # 使用應用上下文
    with app.app_context():
        # 導入模型
        from models import init_models
        models_dict = init_models(db)
        
        # 獲取模型類
        User = models_dict['User']
        BotStyle = models_dict['BotStyle']
        Config = models_dict['Config']
        
        # 創建所有表格
        logger.info("創建資料庫表格...")
        db.create_all()
        
        # 檢查是否已有管理員
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            logger.info("創建管理員帳號...")
            admin = User(
                username="admin",
                email="admin@example.com",
                password_hash=generate_password_hash("admin"),
                is_admin=True
            )
            db.session.add(admin)
        
        # 檢查是否已有機器人風格
        styles = BotStyle.query.all()
        if not styles:
            logger.info("創建預設機器人風格...")
            default_styles = [
                BotStyle(
                    name="貼心",
                    description="關懷輔導型",
                    prompt="你是飛豬機器人，一個充滿愛心與關懷的助手。請用溫暖、貼心的方式與用戶交流，特別注重情感支持。使用溫柔的語氣，提供安慰與鼓勵。",
                    is_default=True
                ),
                BotStyle(
                    name="風趣",
                    description="幽默風趣型",
                    prompt="你是飛豬機器人，一個幽默風趣的伙伴。交談中請適當加入輕鬆的笑話和有趣的比喻，保持輕鬆愉快的交流氛圍。"
                ),
                BotStyle(
                    name="認真",
                    description="正式商務型",
                    prompt="你是飛豬機器人，一個專業嚴謹的助手。請使用正式、清晰的語言與用戶交流，注重資訊的準確性和完整性。"
                ),
                BotStyle(
                    name="專業",
                    description="技術專家型",
                    prompt="你是飛豬機器人，一個技術領域的專家。回答問題時請提供深入、專業的分析，並儘可能引用可靠資訊來源。"
                )
            ]
            for style in default_styles:
                db.session.add(style)
        
        # 檢查是否已有配置項
        configs = Config.query.all()
        if not configs:
            logger.info("創建預設配置項...")
            default_configs = [
                Config(key="OPENAI_TEMPERATURE", value="0.7"),
                Config(key="OPENAI_MAX_TOKENS", value="500"),
                Config(key="LINE_CHANNEL_ID", value=os.environ.get("LINE_CHANNEL_ID", "")),
                Config(key="LINE_CHANNEL_SECRET", value=os.environ.get("LINE_CHANNEL_SECRET", "")),
                Config(key="LINE_CHANNEL_ACCESS_TOKEN", value=os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")),
                Config(key="ACTIVE_BOT_STYLE", value="貼心"),
                Config(key="RAG_ENABLED", value="False"),
                Config(key="WEB_SEARCH_ENABLED", value="False"),
            ]
            for config in default_configs:
                db.session.add(config)
        
        # 確保知識庫目錄存在
        if not os.path.exists("knowledge_base"):
            os.makedirs("knowledge_base", exist_ok=True)
            logger.info("創建知識庫目錄")
        
        # 提交所有更改
        db.session.commit()
        logger.info("資料庫初始化完成！")

if __name__ == "__main__":
    init_db() 