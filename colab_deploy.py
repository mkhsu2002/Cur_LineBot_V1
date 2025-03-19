#!/usr/bin/env python3
"""
Google Colab 部署腳本
此腳本用於在 Google Colab 環境中快速部署 IvyLineBot
"""

import os
import sys
import subprocess
import time
import logging
from IPython.display import clear_output, display, HTML

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_command(cmd, description=None):
    """運行命令並顯示輸出"""
    if description:
        logger.info(f"📋 {description}")
    
    process = subprocess.Popen(
        cmd, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    for line in process.stdout:
        print(line.strip())
    
    # 等待命令執行完成
    process.wait()
    return process.returncode

def setup_project():
    """安裝依賴並設置專案"""
    clear_output(wait=True)
    print("🚀 開始設置 IvyLineBot...")
    
    # 檢查是否在 Colab 環境中
    try:
        import google.colab
        IN_COLAB = True
    except ImportError:
        IN_COLAB = False
    
    if not IN_COLAB:
        logger.warning("⚠️ 此腳本設計用於 Google Colab 環境!")
        cont = input("是否繼續? (y/n): ")
        if cont.lower() != 'y':
            logger.info("🛑 終止設置")
            return False
    
    # 安裝必要的套件
    run_command("pip install python-dotenv flask flask-sqlalchemy flask-login line-bot-sdk openai flask-wtf faiss-cpu", 
                "安裝依賴")
    
    # 如果在 Colab 環境中，設置穿透服務
    if IN_COLAB:
        run_command("pip install pyngrok", "安裝 ngrok 穿透服務")
    
    # 檢查環境變數
    if not os.path.exists('.env'):
        logger.info("📝 創建 .env 文件...")
        with open('.env', 'w') as f:
            f.write("""# 請填寫以下環境變數
OPENAI_API_KEY=
SESSION_SECRET=flypig-line-bot-secret
LINE_CHANNEL_SECRET=
LINE_CHANNEL_ACCESS_TOKEN=
DATABASE_URL=sqlite:///instance/flypig.db
SERPAPI_KEY=
""")
        logger.info("✅ .env 文件已創建，請填寫必要的環境變數")
    
    # 確保目錄存在
    os.makedirs('instance', exist_ok=True)
    os.makedirs('knowledge_base', exist_ok=True)
    os.makedirs('templates/auth', exist_ok=True)
    os.makedirs('templates/admin', exist_ok=True)
    os.makedirs('templates/errors', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # 創建基本模板文件
    if not os.path.exists('templates/index.html'):
        with open('templates/index.html', 'w') as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <title>IvyLineBot</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <h1>IvyLineBot</h1>
        <p>歡迎使用 IvyLineBot - 智能 LINE 聊天機器人</p>
        <div class="buttons">
            <a href="{{ url_for('auth.login') }}" class="button">登入管理面板</a>
        </div>
    </div>
</body>
</html>
""")
    
    if not os.path.exists('templates/auth/login.html'):
        with open('templates/auth/login.html', 'w') as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <title>登入 - IvyLineBot</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <h1>管理員登入</h1>
        <form method="post">
            <div class="form-group">
                <label for="username">用戶名:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">密碼:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <div class="form-buttons">
                <button type="submit" class="button">登入</button>
            </div>
        </form>
        <div class="messages">
            {% for category, message in get_flashed_messages(with_categories=true) %}
            <div class="message {{ category }}">{{ message }}</div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
""")
    
    # 創建基本 CSS 文件
    if not os.path.exists('static/css/style.css'):
        with open('static/css/style.css', 'w') as f:
            f.write("""/* 基本樣式 */
body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 0;
    background-color: #f8f9fa;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

h1, h2, h3 {
    color: #2c3e50;
}

/* 表單樣式 */
.form-group {
    margin-bottom: 15px;
}

label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

input[type="text"],
input[type="email"],
input[type="password"],
textarea,
select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
}

.button {
    display: inline-block;
    background-color: #3498db;
    color: white;
    padding: 10px 15px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    text-decoration: none;
    font-size: 16px;
}

.button:hover {
    background-color: #2980b9;
}

/* 消息樣式 */
.messages {
    margin: 20px 0;
}

.message {
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 4px;
}

.success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.danger {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.info {
    background-color: #d1ecf1;
    color: #0c5460;
    border: 1px solid #bee5eb;
}
""")
    
    # 初始化資料庫
    logger.info("🗄️ 初始化資料庫...")
    run_command("python init_db.py", "初始化資料庫")
    
    logger.info("✅ 專案設置完成!")
    return True

def run_app(port=5000, use_ngrok=True):
    """啟動 Flask 應用程式"""
    clear_output(wait=True)
    
    # 檢查是否在 Colab 環境中
    try:
        import google.colab
        IN_COLAB = True
    except ImportError:
        IN_COLAB = False
        use_ngrok = False
    
    if use_ngrok and IN_COLAB:
        # 設置 ngrok 服務
        from pyngrok import ngrok
        
        # 如果有提供 ngrok 鑰匙，則使用它
        ngrok_key = os.environ.get('NGROK_AUTH_TOKEN')
        if ngrok_key:
            ngrok.set_auth_token(ngrok_key)
        
        # 開始穿透服務
        public_url = ngrok.connect(port)
        logger.info(f"🌐 公開 URL: {public_url}")
        
        # 顯示 QR code
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={public_url}"
        display(HTML(f"""
        <div style="background-color: white; padding: 20px; border-radius: 10px; margin: 10px 0;">
            <h3>LINE Bot 連接資訊:</h3>
            <p>公開 URL: <a href="{public_url}" target="_blank">{public_url}</a></p>
            <p>Webhook URL: <b>{public_url}/webhook</b></p>
            <img src="{qr_url}" alt="QR Code" />
        </div>
        """))
    
    # 啟動應用程式
    logger.info(f"🚀 啟動 Flask 應用於 port {port}...")
    
    if IN_COLAB:
        # 在 Colab 中使用命令行啟動（這樣可以保持輸出）
        cmd = f"python -m flask --app app run --host=0.0.0.0 --port={port}"
        run_command(cmd)
    else:
        # 在本地環境中直接導入並運行
        from app import create_app
        app = create_app()
        app.run(host='0.0.0.0', port=port, debug=True)

def main():
    """主函數"""
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        setup_project()
    elif len(sys.argv) > 1 and sys.argv[1] == "--run":
        port = 5000
        if len(sys.argv) > 2:
            try:
                port = int(sys.argv[2])
            except ValueError:
                pass
        run_app(port=port)
    else:
        print("""
🤖 IvyLineBot Colab 部署工具

使用方法:
- python colab_deploy.py --setup  # 安裝依賴和設置專案
- python colab_deploy.py --run    # 運行應用
- python colab_deploy.py --run 8080  # 指定端口運行應用
        """)

if __name__ == "__main__":
    main() 