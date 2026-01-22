import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import requests
from sqlalchemy import create_engine, Column, String, JSON, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:root@127.0.0.1:3306/lol_app")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class MatchCache(Base):
    __tablename__ = "match_cache"
    match_id = Column(String(50), primary_key=True, index=True)
    match_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 開発中は制限を緩めておきます
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "RGAPI-012dd7d3-bee6-43d5-88ac-b0be437ad8bc" # ★キーをセット
REGION = "asia"
HEADERS = {"X-Riot-Token": API_KEY}

# ★ここが今回のキモ！評価ロジック関数
def evaluate_performance(role, stats, duration_minutes):
    grade = "BAD"
    reason = ""

    # 1. ADC (BOTTOM) の評価基準: CSスコア(CSPM)
    if role == "BOTTOM":
        cspm = stats['cs'] / duration_minutes
        if cspm >= 9.0:
            grade = "GREAT"
        elif cspm >= 7.0:
            grade = "GOOD"
        else:
            grade = "BAD"
        reason = f"CS/分: {round(cspm, 1)}"

    # 2. SUP (UTILITY) の評価基準: 視界スコア/分
    elif role == "UTILITY":
        vspm = stats['vision_score'] / duration_minutes
        if vspm >= 2.0:
            grade = "GREAT"
        elif vspm >= 1.5:
            grade = "GOOD"
        else:
            grade = "BAD"
        reason = f"視界/分: {round(vspm, 1)}"

    # 3. その他 (TOP, JUNGLE, MIDDLE): とりあえずKDAで判定
    else:
        kda_val = stats['kda_ratio']
        if kda_val >= 4.0:
            grade = "GREAT"
        elif kda_val >= 2.5:
            grade = "GOOD"
        else:
            grade = "BAD"
        reason = f"KDA: {round(kda_val, 1)}"

    return {"grade": grade, "reason": reason}

# メイン分析関数
def analyze_match(match_data, target_puuid):
    participants = match_data['info']['participants']
    game_duration = match_data['info']['gameDuration'] # 秒単位
    duration_minutes = game_duration / 60 if game_duration > 0 else 1

    best_score = -1000
    mvp_player = {}
    target_stats = {}

    for player in participants:
        # スコア計算 (MVP用)
        score = (player['kills'] * 2) + player['assists'] - (player['deaths'] * 1.5) + (player['totalDamageDealtToChampions'] / 1000)
        
        if score > best_score:
            best_score = score
            mvp_player = {
                "name": player['riotIdGameName'],
                "champion": player['championName'],
                "score": round(score, 1)
            }
        
        # 検索対象プレイヤーの詳細データ作成
        if player['puuid'] == target_puuid:
            # CS数 = ミニオン + 中立モンスター
            total_cs = player['totalMinionsKilled'] + player['neutralMinionsKilled']
            deaths = player['deaths'] if player['deaths'] > 0 else 1
            kda_ratio = (player['kills'] + player['assists']) / deaths

            raw_stats = {
                "cs": total_cs,
                "vision_score": player['visionScore'],
                "kda_ratio": kda_ratio,
                "kills": player['kills'],
                "deaths": player['deaths'],
                "assists": player['assists']
            }

            # ★ここで評価を実行！
            evaluation = evaluate_performance(player['teamPosition'], raw_stats, duration_minutes)

            target_stats = {
                "champion": player['championName'],
                "role": player['teamPosition'], # BOTTOM, MIDDLE, etc.
                "kda_display": f"{player['kills']}/{player['deaths']}/{player['assists']}",
                "win": player['win'],
                "evaluation": evaluation # {grade: "GREAT", reason: "CS/分: 9.2"}
            }

    return {
        "match_id": match_data['metadata']['matchId'],
        "game_mode": match_data['info']['gameMode'],
        "duration": f"{int(duration_minutes)}分",
        "mvp": mvp_player,
        "target_player": target_stats
    }

# --- エンドポイント ---
@app.get("/history/{game_name}/{tag_line}")
def get_history(game_name: str, tag_line: str, db: Session = Depends(get_db)):
    # ... (前回と同じコードなので省略してもOKですが、全文貼り付ける際は前回の内容維持で) ...
    # APIキーを使ってPUUID取得 -> マッチIDリスト取得 -> ループ処理 の部分は変更なし
    
    # ※省略して記載します。前回のコードの analyze_match 関数だけ置き換えれば動きます。
    # もし不安なら「全文ください」と言ってください！
    
    # (以下略: 前回と同じロジック)
    url_account = f"https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    resp_acc = requests.get(url_account, headers=HEADERS)
    if resp_acc.status_code != 200: raise HTTPException(status_code=404, detail="User not found")
    puuid = resp_acc.json()['puuid']

    url_matches = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=10"
    resp_match = requests.get(url_matches, headers=HEADERS)
    match_ids = resp_match.json()
    
    results = []
    for match_id in match_ids:
        cached_match = db.query(MatchCache).filter(MatchCache.match_id == match_id).first()
        match_detail = None
        if cached_match:
            match_detail = cached_match.match_data
        else:
            url_detail = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"
            resp_detail = requests.get(url_detail, headers=HEADERS)
            if resp_detail.status_code == 200:
                match_detail = resp_detail.json()
                new_cache = MatchCache(match_id=match_id, match_data=match_detail)
                db.add(new_cache)
                db.commit()
            else: continue

        if match_detail:
            results.append(analyze_match(match_detail, puuid))

    return {"search_target": f"{game_name}#{tag_line}", "history": results}