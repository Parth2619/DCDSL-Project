// File: frontend/src/pages/StationDetail.jsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

function StationDetail() {
  const { stationId } = useParams();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`/api/stations/${stationId}/aqi`)
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [stationId]);

  if (loading) return <div className="loading">Loading station data...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  const latestReading = data[0];

  return (
    <div>
      <h1 className="page-title">
        {latestReading?.station_name || `Station ${stationId}`}
      </h1>

      {latestReading && (
        <div className="card">
          <h2>Latest Reading</h2>
          <div style={{ fontSize: '3rem', fontWeight: 'bold', margin: '1rem 0' }}>
            <span className={`aqi-badge ${getAQIClass(latestReading.aqi_value)}`}>
              {latestReading.aqi_value}
            </span>
          </div>
          <p><strong>Date:</strong> {new Date(latestReading.date).toLocaleDateString()}</p>
          <p><strong>PM2.5:</strong> {latestReading.pm25_value || 'N/A'}</p>
          <p><strong>PM10:</strong> {latestReading.pm10_value || 'N/A'}</p>
        </div>
      )}

      <div className="card">
        <h2>Historical Data</h2>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>AQI</th>
              <th>PM2.5</th>
              <th>PM10</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr key={idx}>
                <td>{new Date(row.date).toLocaleDateString()}</td>
                <td>
                  <span className={`aqi-badge ${getAQIClass(row.aqi_value)}`}>
                    {row.aqi_value}
                  </span>
                </td>
                <td>{row.pm25_value || 'N/A'}</td>
                <td>{row.pm10_value || 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function getAQIClass(aqi) {
  if (!aqi) return 'aqi-good';
  if (aqi <= 50) return 'aqi-good';
  if (aqi <= 100) return 'aqi-moderate';
  if (aqi <= 200) return 'aqi-unhealthy';
  return 'aqi-severe';
}

export default StationDetail;
