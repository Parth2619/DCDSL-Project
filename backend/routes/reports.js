// File: backend/routes/reports.js
import express from 'express';
import { query } from '../config/db.js';

const router = express.Router();

// GET /api/reports/health/:cityId/:year - Health impact report using health_summary VIEW
router.get('/health/:cityId/:year', async (req, res, next) => {
  try {
    const { cityId, year } = req.params;
    
    const sql = `
      SELECT * FROM health_summary
      WHERE city_id = ? AND year = ?
    `;
    const results = await query(sql, [parseInt(cityId), parseInt(year)]);
    
    if (results.length === 0) {
      return res.status(404).json({ error: 'Health data not found' });
    }

    res.json(results[0]);
  } catch (error) {
    next(error);
  }
});

export default router;
