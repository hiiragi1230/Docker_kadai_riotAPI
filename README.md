# 🏆 LoL Match History Analyzer

League of Legendsの戦績を検索・分析し、プレイヤーのパフォーマンスを自動評価するフルスタックWebアプリケーションです。
Riot APIを使用し、直近の試合データの取得、MVPの判定、ロールごとの成績評価（Great/Good/Bad）を行います。

![Project Screenshot](https://via.placeholder.com/800x400?text=Screen+Shot+PlaceHolder)
## ✨ 特徴 (Features)

* **戦績検索**: Riot ID (GameName #TagLine) でプレイヤーを検索。
* **パフォーマンス自動評価**:
    * ADC: CS/分 に基づき評価 (例: 9.0以上でGREAT)
    * SUP: 視界スコアに基づき評価
    * その他: KDAに基づき評価
* **高速なデータ取得 (Caching)**:
    * 一度取得した試合データは **MySQL** に保存。
    * 2回目以降のアクセスはDBから読み込むため爆速で表示されます。
* **リッチなUI**:
    * 最新パッチのチャンピオン画像を自動取得して表示。
    * 勝敗、MVP、評価バッジを視覚的に分かりやすく表示。
* **Docker完全対応**: コマンド一発でFrontend, Backend, DB環境が立ち上がります。

## 🛠 使用技術 (Tech Stack)

### Frontend
* **React** (Vite)
* **CSS3** (Grid/Flexbox, Custom Badges)

### Backend
* **Python** (FastAPI)
* **SQLAlchemy** (ORM)
* **Riot Games API**

### Database
* **MySQL 8.0**

### Infrastructure
* **Docker / Docker Compose**

## 🚀 起動方法 (Setup)

### 1. 前提条件
* Docker Desktop がインストールされていること
* Riot Games API Key を取得していること (Development Key)

### 2. クローンと設定
```bash
git clone <このリポジトリのURL>
cd <フォルダ名>
### 3. APIキーの設定

api/main.py を開き、Riot APIキーを設定してください。
Python

# api/main.py
API_KEY = "RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

### 4. 起動

Docker Composeを使用してアプリケーションを起動します。
Bash

docker-compose up --build

### 5. アクセス

ブラウザで以下のURLにアクセスしてください。

    Local: http://localhost:5173

⚙️ 構成 (Project Structure)

.
├── api/                # Backend (FastAPI)
│   ├── main.py         # APIロジック・DB設計・評価アルゴリズム
│   └── Dockerfile
├── frontend/           # Frontend (React)
│   ├── src/
│   │   ├── App.jsx     # UIコンポーネント・データ取得
│   │   └── App.css     # スタイリング
│   └── Dockerfile
├── docker-compose.yml  # コンテナ構成定義
└── README.md

⚠️ 注意点 (Note)

    LAN内アクセス: 他のPC/スマホからアクセスする場合は、frontend/src/App.jsx 内の fetch 先IPアドレスをホストPCのIPに変更してください。

    APIキーの有効期限: RiotのDevelopment Keyは24時間で失効するため、キーが切れた場合は main.py を更新して再ビルドしてください。
