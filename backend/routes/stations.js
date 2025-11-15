// File: backend/routes/stations.js
import express from 'express';
import { query } from '../config/db.js';

const router = express.Router();

// GET /api/stations/by-city/:cityId - Get stations by city
router.get('/by-city/:cityId', async (req, res, next) => {
  try {
    const cityId = parseInt(req.params.cityId);
    const sql = `
      SELECT s.*, c.city_name
      FROM stations s
      JOIN cities c ON s.city_id = c.city_id
      WHERE s.city_id = ?
    `;
    const results = await query(sql, [cityId]);
    res.json(results);
  } catch (error) {
    next(error);
  }
});

// GET /api/stations/:id/aqi - Get AQI data for a specific station
router.get('/:id/aqi', async (req, res, next) => {
  try {
    const stationId = parseInt(req.params.id);
    const limit = parseInt(req.query.limit) || 90;
    
    const sql = `
      SELECT 
        DATE(date) as date,
        AVG(aqi_value) as aqi_value
      FROM aqi
      WHERE station_id = ?
      GROUP BY DATE(date)
      ORDER BY date DESC
      LIMIT ?
    `;
    const results = await query(sql, [stationId, limit]);
    res.json(results);
  } catch (error) {
    next(error);
  }
});

export default router;
