// File: frontend/src/pages/CityProfile.jsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import LineChart from '../components/LineChart';

function CityProfile() {
  const { id } = useParams();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`/api/cities/${id}/profile`)
      .then(res => res.json())
      .then(result => {
        setProfile(result);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [id]);

  const exportCSV = () => {
    if (!profile || !profile.aqi_series) return;
    
    const csv = [
      ['Date', 'Avg AQI'],
      ...profile.aqi_series.map(d => [d.date, d.avg_aqi])
    ].map(row => row.join(',')).join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${profile.city.city_name}_aqi_data.csv`;
    a.click();
  };

  if (loading) return <div className="loading">Loading city profile...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!profile) return <div className="error">No data found</div>;

  const { city, aqi_series, pollutants } = profile;

  return (
    <div>
      <h1 className="page-title">{city.city_name}, {city.state_name}</h1>
      
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2>AQI Time Series (Last 90 Days)</h2>
          <button className="btn" onClick={exportCSV}>Export CSV</button>
        </div>
        {aqi_series && aqi_series.length > 0 ? (
          <LineChart 
            data={aqi_series.map(d => ({ x: d.date, y: d.avg_aqi }))} 
            width={900} 
            height={300}
          />
        ) : (
          <p>No AQI data available</p>
        )}
      </div>

      <div className="card">
        <h2>Pollutants (Last 90 Days)</h2>
        {pollutants && pollutants.length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>PM2.5</th>
                <th>PM10</th>
                <th>NO2</th>
                <th>SO2</th>
                <th>CO</th>
                <th>O3</th>
              </tr>
            </thead>
            <tbody>
              {pollutants.slice(0, 10).map((p, i) => (
                <tr key={i}>
                  <td>{p.date}</td>
                  <td>{p.pm25?.toFixed(2)}</td>
                  <td>{p.pm10?.toFixed(2)}</td>
                  <td>{p.no2?.toFixed(2)}</td>
                  <td>{p.so2?.toFixed(2)}</td>
                  <td>{p.co?.toFixed(2)}</td>
                  <td>{p.o3?.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No pollutant data available</p>
        )}
      </div>
    </div>
  );
}

export default CityProfile;
