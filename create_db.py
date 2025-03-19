import os
import sys
from dotenv import load_dotenv
import sqlite3

# 載入環境變量
load_dotenv()

# 獲取數據庫路徑
db_path = os.environ.get("DATABASE_URL", "sqlite:///instance/flypig.db")
if db_path.startswith("sqlite:///"):
    db_path = db_path[len("sqlite:///"):]

# 確保 instance 目錄存在
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# 創建資料庫並建立表格
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 創建用戶表格
cursor.execute('''
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# 創建 LINE 用戶表格
cursor.execute('''
CREATE TABLE IF NOT EXISTS line_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    line_user_id TEXT NOT NULL UNIQUE,
    display_name TEXT,
    picture_url TEXT,
    status_message TEXT,
    active_style TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# 創建聊天訊息表格
cursor.execute('''
CREATE TABLE IF NOT EXISTS chat_message (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    line_user_id TEXT NOT NULL,
    is_user_message BOOLEAN DEFAULT TRUE,
    message_text TEXT NOT NULL,
    bot_style TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# 創建機器人風格表格
cursor.execute('''
CREATE TABLE IF NOT EXISTS bot_style (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    prompt TEXT NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# 創建配置表格
cursor.execute('''
CREATE TABLE IF NOT EXISTS config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT
)
''')

# 創建文檔表格
cursor.execute('''
CREATE TABLE IF NOT EXISTS document (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    filename TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
)
''')

# 創建日誌表格
cursor.execute('''
CREATE TABLE IF NOT EXISTS log_entry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    module TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# 創建管理員帳號（如果不存在）
cursor.execute("SELECT COUNT(*) FROM user WHERE username = 'admin'")
admin_exists = cursor.fetchone()[0]
if not admin_exists:
    # 使用明文密碼 'admin'，在實際應用中應使用加密函數
    cursor.execute(
        "INSERT INTO user (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)",
        ("admin", "admin@example.com", "pbkdf2:sha256:600000$X5nArwJjSP6YoVq7$4bbf3b34b0abe2dc9ff4f7e2d6aa8bb30d96f12aeeadfb6cb04840dbe8fb6ba8", True)
    )

# 創建預設風格（如果表格為空）
cursor.execute("SELECT COUNT(*) FROM bot_style")
styles_count = cursor.fetchone()[0]
if styles_count == 0:
    default_styles = [
        (
            "貼心",
            "你是飛豬機器人，一個充滿愛心與關懷的助手。請用溫暖、貼心的方式與用戶交流，特別注重情感支持。使用溫柔的語氣，提供安慰與鼓勵。",
            "關懷輔導型",
            True
        ),
        (
            "風趣",
            "你是飛豬機器人，一個幽默風趣的伙伴。交談中請適當加入輕鬆的笑話和有趣的比喻，保持輕鬆愉快的交流氛圍。",
            "幽默風趣型",
            False
        ),
        (
            "認真",
            "你是飛豬機器人，一個專業嚴謹的助手。請使用正式、清晰的語言與用戶交流，注重資訊的準確性和完整性。",
            "正式商務型",
            False
        ),
        (
            "專業",
            "你是飛豬機器人，一個技術領域的專家。回答問題時請提供深入、專業的分析，並儘可能引用可靠資訊來源。",
            "技術專家型",
            False
        )
    ]
    
    for style in default_styles:
        cursor.execute(
            "INSERT INTO bot_style (name, prompt, description, is_default) VALUES (?, ?, ?, ?)",
            style
        )

# 提交更改並關閉連接
conn.commit()
conn.close()

print("資料庫初始化完成！") 