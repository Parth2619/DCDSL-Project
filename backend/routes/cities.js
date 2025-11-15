// File: backend/routes/cities.js
import express from 'express';
import { query } from '../config/db.js';

const router = express.Router();

// GET /api/cities - List all cities
router.get('/', async (req, res, next) => {
  try {
    const sql = `
      SELECT city_id, city_name, state_name, pin_code
      FROM cities
      ORDER BY city_name
    `;
    const results = await query(sql);
    res.json(results);
  } catch (error) {
    next(error);
  }
});

// GET /api/cities/:id/profile - City profile with aggregated AQI series and pollutants
router.get('/:id/profile', async (req, res, next) => {
  try {
    const cityId = parseInt(req.params.id);
    
    // City info
    const cityInfo = await query(
      'SELECT * FROM cities WHERE city_id = ?',
      [cityId]
    );
    
    if (cityInfo.length === 0) {
      return res.status(404).json({ error: 'City not found' });
    }

    // AQI series aggregated by date (last 90 days)
    const aqiSeries = await query(
      `SELECT 
         DATE(date) as date, 
         AVG(aqi_value) as avg_aqi
       FROM aqi
       WHERE city_id = ? 
         AND date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
       GROUP BY DATE(date)
       ORDER BY date DESC`,
      [cityId]
    );

    // Pollutants by date
    const pollutants = await query(
      `SELECT 
         DATE(date) as date,
         AVG(pm25) as pm25,
         AVG(pm10) as pm10,
         AVG(no2) as no2,
         AVG(so2) as so2,
         AVG(co) as co,
         AVG(o3) as o3
       FROM pollutants
       WHERE city_id = ? 
         AND date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
       GROUP BY DATE(date)
       ORDER BY date DESC`,
      [cityId]
    );

    res.json({
      city: cityInfo[0],
      aqi_series: aqiSeries,
      pollutants: pollutants
    });
  } catch (error) {
    next(error);
  }
});

export default router;
