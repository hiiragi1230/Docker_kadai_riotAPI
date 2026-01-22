import { useState } from 'react'
import './App.css'

function App() {
  const [name, setName] = useState('')
  const [tag, setTag] = useState('')
  const [data, setData] = useState(null) // 変数名をresultからdataに変更
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const getChampIcon = (champName) => {
    return `https://ddragon.leagueoflegends.com/cdn/16.1.1/img/champion/${champName}.png`;
  }

  const handleSearch = async () => {
    if (!name || !tag) return;
    
    setLoading(true);
    setError('');
    setData(null);

    try {
      const response = await fetch(`/api/history/${name}/${tag}`);
      
      if (!response.ok) {
        throw new Error('ユーザーが見つからないか、データが取得できません');
      }

      const jsonData = await response.json();
      setData(jsonData);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <h1>🏆 LoL History Analyzer</h1>
      
      <div className="search-box">
        <input 
          type="text" 
          placeholder="GameName" 
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <span className="separator">#</span>
        <input 
          type="text" 
          placeholder="Tag" 
          className="tag-input"
          value={tag}
          onChange={(e) => setTag(e.target.value)}
        />
        <button onClick={handleSearch} disabled={loading}>
          {loading ? '分析中...' : '検索'}
        </button>
      </div>

      {error && <p className="error">{error}</p>}

      {/* 結果表示エリア */}
      {data && (
        <div className="history-container">
          <h2>{data.search_target} の直近10戦</h2>
          <div className="cards-grid">
            {data.history.map((match) => (
              <div key={match.match_id} className={`match-card ${match.target_player.win ? 'win' : 'lose'}`}>
                
                <div className="match-header">
                  <span className="mode">{match.game_mode} ({match.duration})</span>
                  <span className="role-badge">{match.target_player.role}</span>
                </div>

                <div className="main-content">
                  <img 
                    src={getChampIcon(match.target_player.champion)} 
                    alt={match.target_player.champion}
                    className="champ-img"
                  />
                  <div className="champ-info">
                    <div className="champ-name">{match.target_player.champion}</div>
                    <div className="kda-text">{match.target_player.kda_display}</div>
                  </div>

                  {/* 評価バッジ表示エリア */}
                  <div className={`grade-badge ${match.target_player.evaluation.grade}`}>
                    <div className="grade-title">{match.target_player.evaluation.grade}</div>
                    <div className="grade-reason">{match.target_player.evaluation.reason}</div>
                  </div>
                </div>

                <div className="mvp-section">
                  <img 
                    src={getChampIcon(match.mvp.champion)} 
                    alt="MVP" 
                    className="mvp-img-small"
                  />
                  <small>MVP: {match.mvp.name} ({match.mvp.score})</small>
                </div>
                
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default App