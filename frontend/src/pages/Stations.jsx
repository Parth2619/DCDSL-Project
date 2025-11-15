// File: frontend/src/pages/Stations.jsx
import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';

function Stations() {
  const { cityId } = useParams();
  const [stations, setStations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`/api/stations/by-city/${cityId}`)
      .then(res => res.json())
      .then(data => {
        setStations(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [cityId]);

  if (loading) return <div className="loading">Loading stations...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div>
      <h1 className="page-title">Monitoring Stations</h1>
      
      <div className="card">
        <table>
          <thead>
            <tr>
              <th>Station Name</th>
              <th>Latest AQI</th>
              <th>Last Updated</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            {stations.map(station => (
              <tr key={station.station_id}>
                <td>{station.station_name}</td>
                <td>
                  <span className={`aqi-badge ${getAQIClass(station.latest_aqi)}`}>
                    {station.latest_aqi || 'N/A'}
                  </span>
                </td>
                <td>{station.last_updated ? new Date(station.last_updated).toLocaleDateString() : 'N/A'}</td>
                <td>
                  <Link to={`/stations/${station.station_id}`} className="btn">
                    View Details
                  </Link>
                </td>
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

export default Stations;
