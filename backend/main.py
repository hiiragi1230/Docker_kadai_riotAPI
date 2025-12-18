import os
from sqlalchemy import create_engine
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import requests
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime

# --- 1. データベース設定 ---
# docker run で設定した user:password と DB名(lol_app) を使います
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:root@127.0.0.1:3306/lol_app")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# データを保存する「テーブル（表）」の設計図
class SearchResult(Base):
    __tablename__ = "search_results"
    
    id = Column(Integer, primary_key=True, index=True)
    riot_id_full = Column(String(100), index=True) # 例: "Hide on bush#KR1"
    match_data = Column(JSON)                      # 計算結果をJSONのまま保存
    updated_at = Column(DateTime, default=datetime.now)

# アプリ起動時にテーブルを自動で作る
Base.metadata.create_all(bind=engine)

# データベースを使うための便利関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 2. FastAPI設定 ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "RGAPI-e4576170-fdd3-4b96-97b9-531918a70749" # ★ここにキーを貼る
REGION = "asia"
HEADERS = {"X-Riot-Token": API_KEY}

# --- 3. APIエンドポイント ---
@app.get("/mvp/{game_name}/{tag_line}")
def get_mvp(game_name: str, tag_line: str, db: Session = Depends(get_db)):
    
    full_id = f"{game_name}#{tag_line}"
    print(f"🔍 検索中: {full_id}")

    # ★データベースを検索！
    # 直近のデータがDBにあるか確認する
    cached_data = db.query(SearchResult).filter(SearchResult.riot_id_full == full_id).first()
    
    if cached_data:
        print("✅ データベースから発見！APIは使いません。")
        return cached_data.match_data

    print("⚠️ データベースになし。Riot APIへ問い合わせます...")

    # --- ここから下は以前と同じ（Riot API通信） ---
    
    # 1. PUUID取得
    url_account = f"https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    resp_acc = requests.get(url_account, headers=HEADERS)
    
    if resp_acc.status_code != 200:
        raise HTTPException(status_code=404, detail="User not found")
        
    puuid = resp_acc.json()['puuid']

    # 2. 直近の試合取得
    url_matches = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=1"
    resp_match = requests.get(url_matches, headers=HEADERS)
    match_ids = resp_match.json()
    
    if not match_ids:
        raise HTTPException(status_code=404, detail="No matches found")

    # 3. 詳細データ取得 & MVP計算
    latest_match_id = match_ids[0]
    url_detail = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/{latest_match_id}"
    resp_detail = requests.get(url_detail, headers=HEADERS)
    match_data_raw = resp_detail.json()
    
    participants = match_data_raw['info']['participants']
    
    best_score = -1000
    mvp_data = {}

    for player in participants:
        score = (player['kills'] * 2) + player['assists'] - (player['deaths'] * 1.5) + (player['totalDamageDealtToChampions'] / 1000)
        
        if score > best_score:
            best_score = score
            mvp_data = {
                "name": player['riotIdGameName'],
                "champion": player['championName'],
                "kda": f"{player['kills']}/{player['deaths']}/{player['assists']}",
                "score": round(score, 1)
            }
            
    final_result = {
        "search_target": full_id,
        "match_id": latest_match_id,
        "mvp_result": mvp_data,
        "source": "Riot API" # どこから取ったか分かるように印をつける
    }

    # ★データベースに保存！
    # 新しいデータを作って保存する
    new_cache = SearchResult(riot_id_full=full_id, match_data=final_result)
    db.add(new_cache)
    db.commit()
    print("💾 データベースに保存しました")

    return final_result