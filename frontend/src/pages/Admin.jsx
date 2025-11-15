// File: frontend/src/pages/Admin.jsx
import React, { useState } from 'react';

const ADMIN_TOKEN = 'your-secret-admin-token-here'; // Match backend .env

function Admin() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [aggregating, setAggregating] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
    setError(null);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setResult(null);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/admin/upload/aqi', {
        method: 'POST',
        headers: {
          'X-ADMIN-TOKEN': ADMIN_TOKEN
        },
        body: formData,
      });
      const data = await response.json();
      
      if (response.ok) {
        setResult(data);
        setFile(null);
        e.target.reset();
      } else {
        setError(data.error || 'Upload failed');
      }
    } catch (err) {
      setError(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleAggregate = async () => {
    setAggregating(true);
    setResult(null);
    setError(null);

    try {
      const response = await fetch('/api/admin/run/aggregate', {
        method: 'POST',
        headers: {
          'X-ADMIN-TOKEN': ADMIN_TOKEN
        }
      });
      const data = await response.json();
      
      if (response.ok) {
        setResult({ message: 'Aggregation completed successfully' });
      } else {
        setError(data.error || 'Aggregation failed');
      }
    } catch (err) {
      setError(`Aggregation failed: ${err.message}`);
    } finally {
      setAggregating(false);
    }
  };

  return (
    <div>
      <h1 className="page-title">Admin Panel</h1>

      {error && <div className="error">{error}</div>}
      {result && (
        <div className="success">
          {result.message || `Inserted: ${result.inserted}, Failed: ${result.failed}`}
          {result.errors && result.errors.length > 0 && (
            <details style={{ marginTop: '0.5rem' }}>
              <summary>Failed rows (first 10)</summary>
              <pre style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>
                {JSON.stringify(result.errors, null, 2)}
              </pre>
            </details>
          )}
        </div>
      )}

      <div className="card">
        <h2>Upload AQI Data (CSV)</h2>
        <p style={{ marginBottom: '1rem', color: '#666' }}>
          CSV format: city_id, station_id, date, aqi_value
        </p>
        <form onSubmit={handleUpload}>
          <div className="form-group">
            <label>Select CSV File:</label>
            <input 
              type="file" 
              accept=".csv" 
              onChange={handleFileChange}
              disabled={uploading}
            />
          </div>
          <button type="submit" className="btn" disabled={uploading}>
            {uploading ? 'Uploading...' : 'Upload & Process'}
          </button>
        </form>
      </div>

      <div className="card">
        <h2>Run Nightly Aggregation</h2>
        <p style={{ marginBottom: '1rem', color: '#666' }}>
          Updates total pollution from vehicle emissions.
        </p>
        <button 
          className="btn" 
          onClick={handleAggregate}
          disabled={aggregating}
        >
          {aggregating ? 'Running...' : 'Run Aggregation'}
        </button>
      </div>
    </div>
  );
}

export default Admin;
