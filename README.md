# Flask Web 範本系統

這是一個使用 Flask 框架建立的網站範本，包含基本的會員系統和後台管理功能。

## 功能

- **會員系統**
  - 使用者註冊/登入
  - 個人資料管理
  - 密碼加密存儲
  
- **後台管理**
  - 系統總覽
  - 使用者統計
  - 系統資訊顯示

- **介面設計**
  - 響應式設計 (Bootstrap 5)
  - 現代化 UI/UX
  - 易於客製化

## 技術棧

- Python 3.9+
- Flask 3.0.0
- SQLAlchemy
- Flask-Login
- Bootstrap 5
- SQLite

## 配置說明

在 `.env` 文件中配置以下環境變數：

```plaintext
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
```

## 自定義開發
### 新增路由 

在 app/routes/ 中創建新的路由文件
在 app/__init__.py 中註冊新的藍圖
### 添加新功能

在 app/models/ 中添加新的資料模型
在 app/templates/ 中創建對應的模板
### 修改樣式

編輯 app/static/css/ 中的 CSS 文件
修改 app/templates/ 中的模板文件
