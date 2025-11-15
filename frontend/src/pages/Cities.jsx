// File: frontend/src/pages/Cities.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Cities() {
  const [cities, setCities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetch('/api/cities')
      .then(res => res.json())
      .then(result => {
        setCities(result);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="loading">Loading cities...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div>
      <h1 className="page-title">Cities</h1>
      <div className="card">
        <table>
          <thead>
            <tr>
              <th>City Name</th>
              <th>State</th>
              <th>PIN Code</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {cities.map(city => (
              <tr key={city.city_id}>
                <td>{city.city_name}</td>
                <td>{city.state_name}</td>
                <td>{city.pin_code}</td>
                <td>
                  <button 
                    className="btn" 
                    onClick={() => navigate(`/cities/${city.city_id}`)}
                  >
                    View Profile
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Cities;
