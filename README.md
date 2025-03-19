# 🤖 FlyPig LineBot

這是一個基於 Flask 和 OpenAI 的 LINE 聊天機器人專案，可以處理自然語言查詢並提供智能回覆。

## 🌟 功能特點

- 基於 OpenAI API 的自然語言處理
- 整合 LINE Messaging API 實現即時對話
- 自定義知識庫擴展回答能力
- 用戶管理和身份驗證功能
- 支援 Google Colab 一鍵部署

## 📋 系統需求

- Python 3.8+
- Flask 和相關套件
- OpenAI API 金鑰
- LINE 開發者帳號與頻道設定
- SQLite 或其他支援的數據庫

## 🛠️ 安裝設定

1. 複製存儲庫：
   ```bash
   git clone https://github.com/YOUR_USERNAME/IvyLineBot.git
   cd IvyLineBot
   ```

2. 安裝依賴：
   ```bash
   pip install -r requirements.txt
   ```

3. 配置環境變數：
   - 創建 `.env` 文件並設定必要的環境變數
   ```
   OPENAI_API_KEY=您的OpenAI_API金鑰
   LINE_CHANNEL_SECRET=您的LINE頻道密鑰
   LINE_CHANNEL_ACCESS_TOKEN=您的LINE頻道訪問令牌
   DATABASE_URL=sqlite:///instance/flypig.db
   SESSION_SECRET=您的會話密鑰
   ```

4. 初始化數據庫：
   ```bash
   python init_db.py
   ```

5. 運行應用：
   ```bash
   python app.py
   ```

## 🚀 在 Google Colab 上部署

我們提供了簡便的 Google Colab 部署方案：

1. 訪問 [IvyLineBot Colab 筆記本](https://colab.research.google.com/github/YOUR_USERNAME/IvyLineBot/blob/main/IvyLineBot_Colab.ipynb)
2. 按照筆記本中的指示操作
3. 獲取公共 URL 並設置到 LINE 開發者控制台

## 🔧 專案結構

```
IvyLineBot/
├── app.py                  # 應用程式入口點
├── init_db.py              # 數據庫初始化腳本
├── colab_deploy.py         # Google Colab 部署腳本
├── requirements.txt        # 專案依賴
├── config.py               # 配置設定
├── models/                 # 數據模型
│   ├── __init__.py
│   ├── user.py
│   └── chat_history.py
├── routes/                 # 應用路由
│   ├── __init__.py
│   ├── admin.py
│   ├── auth.py
│   └── api.py
├── services/               # 業務邏輯層
│   ├── __init__.py
│   ├── line_service.py
│   └── openai_service.py
├── knowledge_base/         # 知識庫文件
└── instance/               # 實例文件（數據庫等）
```

## 📝 使用方法

1. 設置 LINE Bot 的 Webhook URL 為您的應用程式 URL + `/callback`
2. 在 LINE Developers 控制台啟用 Webhook
3. 將機器人添加為好友並開始對話

## 🤝 貢獻指南

歡迎提交問題報告和貢獻代碼！請遵循以下步驟：

1. Fork 專案
2. 創建您的功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m '添加一些驚人的功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟一個 Pull Request

## 📄 授權協議

本專案採用 MIT 授權協議 - 詳情參見 [LICENSE](LICENSE) 文件。

## 🙏 鳴謝

- [Flask](https://flask.palletsprojects.com/)
- [LINE Messaging API](https://developers.line.biz/en/services/messaging-api/)
- [OpenAI API](https://openai.com/blog/openai-api/)
