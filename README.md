# Flask Web 應用專案

這是一個基於 Flask 框架開發的網站專案，提供了完整的用戶系統、文章管理、留言互動和按讚功能。

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
- 文章搜索功能
- 文章詳情頁面
- 作者資訊顯示
- 修改時間記錄

### 互動功能
- 文章留言
- 留言回覆
- 文章按讚
- 按讚狀態追蹤
- 使用者互動記錄

### 系統管理
- 會員列表頁面
- 會員資料顯示
- 活躍用戶統計
- 新增會員統計
- 系統總覽
- 個人設定

## 技術架構

### 後端框架
- Flask 3.0.0
- Flask-SQLAlchemy（資料庫 ORM）
- Flask-Login（用戶認證）
- Pillow（圖片處理）
- python-dotenv（環境變數）
- Blueprint（模組化路由）
- Service Layer（業務邏輯層）

### 前端框架
- Bootstrap 5.3.2
- Bootstrap Icons
- JavaScript（AJAX）
- 自適應設計

### 資料庫
- SQLite（開發環境）

## 專案結構
```
project/
├── app/
│   ├── models/              # 數據模型
│   │   ├── user.py         # 用戶模型
│   │   ├── post.py         # 文章模型
│   │   ├── comment.py      # 留言模型
│   │   └── like.py         # 按讚模型
│   │
│   ├── routes/             # 路由控制器
│   │   ├── main.py         # 主頁路由
│   │   ├── auth.py         # 認證路由
│   │   ├── post.py         # 文章路由
│   │   └── settings.py     # 設定路由
│   │
│   ├── services/           # 業務邏輯層
│   │   ├── base_service.py # 基礎服務類
│   │   ├── user_service.py # 用戶服務
│   │   ├── post_service.py # 文章服務
│   │   ├── comment_service.py # 留言服務
│   │   └── like_service.py # 按讚服務
│   │
│   ├── static/            # 靜態文件
│   │   ├── css/          # 樣式文件
│   │   ├── js/           # JavaScript
│   │   ├── images/       # 圖片資源
│   │   ├── icon/         # 圖標文件
│   │   └── uploads/      # 上傳文件
│   │       └── avatars/  # 頭像
│   │
│   └── templates/         # 模板文件
│       ├── auth/         # 認證相關
│       ├── components/   # 組件
│       ├── errors/       # 錯誤頁面
│       ├── main/         # 主要頁面
│       ├── pages/        # 其他頁面
│       └── posts/        # 文章相關
│
├── instance/             # 實例配置
├── migrations/           # 數據遷移
├── .env                 # 環境變量
└── run.py               # 啟動文件
```

## 安裝說明

1. 克隆專案
```bash
git clone https://github.com/WenSheng31/Flask_web-template.git
cd Flask_web-template
```

2. 創建虛擬環境
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate    # Windows
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

## 開發指南

### 資料庫遷移
```bash
# 創建遷移
flask db migrate -m "Migration message"

# 應用遷移
flask db upgrade
```

### 添加新功能
1. 在 models/ 添加新的數據模型
2. 在 services/ 實現業務邏輯
3. 在 routes/ 添加路由控制
4. 在 templates/ 添加視圖模板

## 項目依賴

主要依賴包：
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-Migrate==4.0.5
python-dotenv==1.0.0
Pillow==10.1.0
Werkzeug==3.0.1
```

## 待優化項目

1. 功能改進
   - 添加文章分類功能
   - 實現更複雜的權限系統
   - 添加文章標籤功能
   - 改進搜索功能

2. 技術改進
   - 添加單元測試
   - 完善錯誤處理
   - 改進緩存機制
   - 添加日誌系統

3. 性能優化
   - 資料庫查詢優化
   - 靜態資源優化
   - 圖片處理優化

## 版本信息

- 版本：1.0.0
- 最後更新：2024-10-28

## 聯繫方式

wensheng@evo-techlab.com
