import os
import time
import logging
import traceback
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from flask import Flask, request, abort, render_template, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 載入環境變量
load_dotenv()

# 日誌配置
logging.basicConfig(
    level=logging.getLevelName(os.environ.get('LOG_LEVEL', 'DEBUG')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 定義基礎類別
class Base(DeclarativeBase):
    pass

# 初始化擴展（但不立即綁定到應用）
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# LINE Bot API 實例 (會在應用初始化時設置)
line_bot_api = None
webhook_handler = None

def create_app(test_config=None):
    """應用工廠：創建並配置Flask應用"""
    # 創建 Flask 應用
    app = Flask(__name__)
    
    # 載入配置
    if test_config is None:
        # 預設配置
        app.config['SECRET_KEY'] = os.environ.get("SESSION_SECRET", "flypig-line-bot-secret")
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///instance/flypig.db")
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            "pool_recycle": 180,
            "pool_pre_ping": True,
            "pool_size": 10,
            "max_overflow": 15,
            "pool_timeout": 30,
            "connect_args": {"connect_timeout": 10}
        }
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    else:
        # 使用測試配置
        app.config.from_mapping(test_config)
    
    # 確保 instance 資料夾存在
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # 初始化資料庫
    db.init_app(app)
    
    # 初始化登入管理器
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # 初始化 LINE Bot API
    global line_bot_api, webhook_handler
    line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', ''))
    webhook_handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET', ''))
    
    # 初始化模型 (避免循環導入問題)
    with app.app_context():
        from models import init_models
        models = init_models(db)
        
        @login_manager.user_loader
        def load_user(user_id):
            """載入用戶，供 Flask-Login 使用"""
            from models import User
            return User.query.get(int(user_id))
    
    # 註冊藍圖
    register_blueprints(app)
    
    # 定義路由
    @app.route("/")
    def index():
        """首頁路由"""
        return render_template('index.html')
    
    @app.route("/webhook", methods=['POST'])
    def webhook():
        """LINE Bot Webhook 處理路由"""
        # 獲取 X-Line-Signature 標頭
        signature = request.headers['X-Line-Signature']
        
        # 獲取請求正文
        body = request.get_data(as_text=True)
        logger.debug("Request body: %s", body)
        
        try:
            # 驗證簽名並處理請求
            webhook_handler.handle(body, signature)
        except InvalidSignatureError:
            logger.error("Invalid signature. Check LINE Channel Secret.")
            abort(400)
        
        return 'OK'
    
    # LINE Bot 消息處理
    @webhook_handler.add(MessageEvent, message=TextMessage)
    def handle_text_message(event):
        """處理文字消息事件"""
        from services.llm_service import LLMService
        from routes.utils.config_service import get_active_bot_style
        
        try:
            # 獲取使用者 ID 和消息文本
            user_id = event.source.user_id
            message_text = event.message.text
            
            # 獲取使用者資訊
            line_user = get_or_create_line_user(user_id)
            
            # 記錄使用者消息
            save_chat_message(user_id, message_text, is_user_message=True)
            
            # 獲取機器人風格
            bot_style = get_active_bot_style(line_user.active_style)
            
            # 使用 LLM 生成回覆
            llm_service = LLMService()
            response = llm_service.generate_response(message_text, bot_style.prompt)
            
            # 記錄機器人回覆
            save_chat_message(user_id, response, is_user_message=False, bot_style=bot_style.name)
            
            # 發送回覆
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=response)
            )
            
            # 更新使用者最後互動時間
            update_last_interaction(user_id)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            traceback.print_exc()
            
            # 發送錯誤訊息
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="抱歉，處理您的訊息時發生錯誤，請稍後再試。")
            )
    
    # 錯誤處理
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500
    
    return app

def register_blueprints(app):
    """註冊所有藍圖"""
    # 在這裡導入並註冊所有藍圖
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

# 使用者相關輔助函數
def get_or_create_line_user(line_user_id):
    """獲取或創建LINE使用者記錄"""
    from models import LineUser
    
    line_user = LineUser.query.filter_by(line_user_id=line_user_id).first()
    
    if not line_user:
        try:
            # 從 LINE 平台獲取使用者資訊
            profile = line_bot_api.get_profile(line_user_id)
            line_user = LineUser(
                line_user_id=line_user_id,
                display_name=profile.display_name,
                picture_url=profile.picture_url,
                status_message=profile.status_message
            )
            db.session.add(line_user)
            db.session.commit()
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            # 建立最小使用者資訊
            line_user = LineUser(line_user_id=line_user_id)
            db.session.add(line_user)
            db.session.commit()
    
    return line_user

def save_chat_message(line_user_id, message_text, is_user_message=True, bot_style=None):
    """保存聊天訊息"""
    from models import ChatMessage
    
    chat_message = ChatMessage(
        line_user_id=line_user_id,
        message_text=message_text,
        is_user_message=is_user_message,
        bot_style=bot_style
    )
    
    db.session.add(chat_message)
    db.session.commit()

def update_last_interaction(line_user_id):
    """更新使用者最後互動時間"""
    from models import LineUser
    
    line_user = LineUser.query.filter_by(line_user_id=line_user_id).first()
    if line_user:
        line_user.last_interaction = datetime.utcnow()
        db.session.commit()

# 如果直接執行此文件，則啟動應用
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
