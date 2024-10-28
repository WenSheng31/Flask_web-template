# Flask Web 應用範本

這是一個基於 Flask 框架開發的網站專案，提供了完整的用戶系統和文章管理功能。

## 功能特點

### 用戶系統
- 註冊/登入功能
- 個人資料管理
- 大頭貼上傳功能
- 密碼加密存儲
- Remember me 功能
- 最後登入時間記錄

### 文章系統
- 發布/編輯/刪除文章
- 文章列表（分頁）
- 文章詳情頁面
- 作者資訊顯示
- 修改時間記錄

### 會員管理
- 會員列表頁面
- 會員資料顯示
- 活躍用戶統計
- 新增會員統計

### 設定頁面
- 系統總覽
- 個人資料設定
- 密碼修改
- 其他設定選項

## 技術架構

### 後端框架
- Flask 3.0.0
- Flask-SQLAlchemy（資料庫 ORM）
- Flask-Login（用戶認證）
- Pillow（圖片處理）
- python-dotenv（環境變數）

### 前端框架
- Bootstrap 5.3.2
- Bootstrap Icons
- 自適應設計

### 資料庫
- SQLite（開發環境）

## 專案結構
```
project/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── post.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── auth.py
│   │   ├── post.py
│   │   └── settings.py
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   ├── uploads/
│   │   │   └── avatars/
│   │   └── icon/
│   └── templates/
│       ├── auth/
│       ├── components/
│       ├── errors/
│       ├── main/
│       ├── pages/
│       ├── posts/
│       └── base.html
├── requirements.txt
├── run.py
└── .env
```

## 安裝說明

1. 克隆專案
```bash
git clone https://github.com/WenSheng31/Flask_web-template.git
cd Flask_web-template
```

2. 創建虛擬環境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

3. 安裝依賴
```bash
pip install -r requirements.txt
```

4. 配置環境變數
創建 `.env` 文件：
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
SQLALCHEMY_DATABASE_URI=sqlite:///app.db
```

5. 初始化資料庫
```bash
flask db upgrade
```

6. 運行應用
```bash
flask run
```

## 使用說明

1. 訪問 `http://localhost:5000` 進入首頁
2. 點擊「註冊」創建新帳號
3. 使用註冊的帳號登入系統
4. 登入後可以：
   - 發布/編輯/刪除文章
   - 修改個人資料
   - 上傳頭像
   - 查看會員列表

## 安全性考慮

- 密碼使用 werkzeug.security 進行加密
- 實作 CSRF 保護
- 檔案上傳限制和驗證
- 用戶認證和授權控制

## 開發注意事項

1. 生產環境建議：
   - 使用 PostgreSQL 替換 SQLite
   - 配置適當的日誌記錄
   - 設置郵件服務
   - 增加錯誤監控

2. 待優化項目：
   - 添加文章評論功能
   - 實現用戶權限管理
   - 改進文章編輯器
   - 添加搜索功能
   - 實現用戶互動功能

## 版本信息

- 版本：1.0.0
- 最後更新：2024-10-28

## 聯繫方式

wensheng@evo-techlab.com
