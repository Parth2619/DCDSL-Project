// File: frontend/src/pages/Dashboard.jsx
import React, { useState, useEffect } from 'react';

function Dashboard() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/dashboard')
      .then(res => res.json())
      .then(result => {
        setData(result);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const getAqiColor = (aqi) => {
    if (!aqi) return '#ccc';
    if (aqi <= 50) return '#27ae60';   // green
    if (aqi <= 100) return '#f39c12';  // yellow
    if (aqi <= 200) return '#e67e22';  // orange
    return '#e74c3c';                   // red
  };

  if (loading) return <div className="loading">Loading dashboard...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div>
      <h1 className="page-title">Air Quality Dashboard</h1>
      <div className="dashboard-grid">
        {data.map((city, index) => (
          <div key={city.city_id} className="dashboard-card">
            <div className="rank">#{index + 1}</div>
            <h3>{city.city_name}</h3>
            <p className="state">{city.state_name}</p>
            <div 
              className="aqi-badge" 
              style={{ backgroundColor: getAqiColor(city.aqi_7day_avg) }}
            >
              AQI: {city.aqi_7day_avg ? Math.round(city.aqi_7day_avg) : 'N/A'}
            </div>
            <div className="metrics">
              <div className="metric">
                <span className="label">Stations:</span>
                <span className="value">{city.station_count}</span>
              </div>
              <div className="metric">
                <span className="label">Pollution/capita:</span>
                <span className="value">
                  {city.pollution_per_capita ? city.pollution_per_capita.toFixed(4) : 'N/A'}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Dashboard;
