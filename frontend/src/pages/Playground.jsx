// File: frontend/src/pages/Playground.jsx
import React, { useState } from 'react';

function Playground() {
  const [query, setQuery] = useState('SELECT * FROM cities LIMIT 10;');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const executeQuery = async () => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch('/api/playground', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      const data = await response.json();
      
      if (response.ok) {
        setResults(data);
      } else {
        setError(data.error || 'Query failed');
      }
    } catch (err) {
      setError(`Request failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="page-title">SQL Playground</h1>
      
      <div className="card">
        <h2>Query Editor</h2>
        <p style={{ marginBottom: '1rem', color: '#666', fontSize: '0.9rem' }}>
          ⚠️ Only SELECT queries are allowed. Results automatically limited to 1000 rows.
        </p>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{
            width: '100%',
            minHeight: '150px',
            padding: '0.75rem',
            fontFamily: 'monospace',
            fontSize: '0.95rem',
            border: '1px solid #ddd',
            borderRadius: '4px',
            resize: 'vertical'
          }}
        />
        <button 
          onClick={executeQuery} 
          className="btn" 
          disabled={loading}
          style={{ marginTop: '1rem' }}
        >
          {loading ? 'Executing...' : 'Execute Query'}
        </button>
      </div>

      {error && (
        <div className="error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {results && results.length > 0 && (
        <div className="card">
          <h2>Results ({results.length} rows)</h2>
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead>
                <tr>
                  {Object.keys(results[0]).map(col => (
                    <th key={col}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {results.map((row, idx) => (
                  <tr key={idx}>
                    {Object.values(row).map((val, i) => (
                      <td key={i}>{val !== null ? String(val) : 'NULL'}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {results && results.length === 0 && (
        <div className="card">
          <p>Query executed successfully but returned no rows.</p>
        </div>
      )}
    </div>
  );
}

export default Playground;
