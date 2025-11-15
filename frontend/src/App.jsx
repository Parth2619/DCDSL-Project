import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Cities from './pages/Cities';
import CityProfile from './pages/CityProfile';
import Stations from './pages/Stations';
import StationDetail from './pages/StationDetail';
import Playground from './pages/Playground';
import Admin from './pages/Admin';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <nav className="navbar">
          <h1>🌍 Air Quality Monitor</h1>
          <div className="nav-links">
            <Link to="/">Dashboard</Link>
            <Link to="/cities">Cities</Link>
            <Link to="/playground">SQL</Link>
            <Link to="/admin">Admin</Link>
          </div>
        </nav>
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/cities" element={<Cities />} />
            <Route path="/cities/:id" element={<CityProfile />} />
            <Route path="/stations/by-city/:cityId" element={<Stations />} />
            <Route path="/stations/:stationId" element={<StationDetail />} />
            <Route path="/playground" element={<Playground />} />
            <Route path="/admin" element={<Admin />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
