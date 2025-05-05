
DB  PROJECT
==
#### !! 建議先下載好軟體 之後會commit push才會比較方便
## 下載套件
```
pip install -r requirement.txt
```
## 編譯執行
### crtl+c quit
- 結束執行
### crtl+按網址
- 開啟網頁

### 架構

```
project/
├── app.py                   ← 主程式（Flask）
├── models.db                ← SQLite 本地資料庫（使用者資料、配對、聊天）
├── schema.sql               ← SQL 資料表定義檔（老師需要）
├── firebase_init.py         ← Firestore 初始化（額外擴充用）
├── serviceAccountKey.json   ← Firebase 憑證（不要上傳 GitHub）
├── requirements.txt         ← 所需套件（sqlite3, firebase-admin, flask）
│
├── templates/               ← 前端 HTML
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── match.html
│   └── profile.html
│
├── static/                  ← CSS / 圖片 / JS
│   └── style.css
│
└── README.md                ← 專案說明
```
mac 虛擬環境

python3 -m venv venv          # 建立虛擬環境
source venv/bin/activate      # 啟動虛擬環境（Mac/Linux）
# 如果你是 Windows： venv\Scripts\activate
pip install -r requirements.txt

退出虛擬環境 deactivate
```