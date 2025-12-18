import { useState } from 'react'
import './App.css'

function App() {
  const [name, setName] = useState('')
  const [tag, setTag] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSearch = async () => {
    if (!name || !tag) return;
    
    setLoading(true);
    setError('');
    setResult(null);

    try {
      // PythonのAPIを呼び出す
      const response = await fetch(`http://127.0.0.1:8000/mvp/${name}/${tag}`);
      
      if (!response.ok) {
        throw new Error('ユーザーが見つからないか、試合データがありません');
      }

      const data = await response.json();
      setResult(data);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <h1>🏆 LoL MVP Analyzer</h1>
      <p>直近の試合から独自のロジックでMVPを判定します</p>
      
      <div className="search-box">
        <input 
          type="text" 
          placeholder="GameName (例: Hide on bush)" 
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <span className="separator">#</span>
        <input 
          type="text" 
          placeholder="Tag (例: KR1)" 
          className="tag-input"
          value={tag}
          onChange={(e) => setTag(e.target.value)}
        />
        <button onClick={handleSearch} disabled={loading}>
          {loading ? '分析中...' : '検索'}
        </button>
      </div>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="result-card">
          <h2>今日のMVP</h2>
          <div className="mvp-name">{result.mvp_result.name}</div>
          <div className="mvp-champ">Champion: {result.mvp_result.champion}</div>
          <div className="mvp-stats">
            KDA: {result.mvp_result.kda} <br/>
            Score: {result.mvp_result.score} 点
          </div>
          <p className="match-id">Match ID: {result.match_id}</p>
        </div>
      )}
    </div>
  )
}

export default App