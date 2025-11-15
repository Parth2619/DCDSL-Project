// File: backend/routes/dashboard.js
import express from 'express';
import { query } from '../config/db.js';

const router = express.Router();

// GET /api/dashboard - Returns city_summary VIEW with pollution_per_capita function
router.get('/', async (req, res, next) => {
  try {
    const sql = `
      SELECT 
        cs.*,
        pollution_per_capita(cs.city_id) as pollution_per_capita
      FROM city_summary cs
      ORDER BY cs.aqi_7day_avg DESC
      LIMIT 20
    `;
    const results = await query(sql);
    res.json(results);
  } catch (error) {
    console.error('Dashboard error:', error);
    next(error);
  }
});

export default router;
