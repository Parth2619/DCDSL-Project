// File: backend/routes/playground.js
import express from 'express';
import { query } from '../config/db.js';

const router = express.Router();

// POST /api/playground - Execute SELECT-only queries with row limit enforcement
router.post('/', async (req, res, next) => {
  try {
    const { sql } = req.body;
    
    if (!sql || typeof sql !== 'string') {
      return res.status(400).json({ error: 'SQL query is required' });
    }

    // Security: Only allow SELECT queries (case-insensitive)
    const trimmedSql = sql.trim();
    if (!trimmedSql.match(/^SELECT/i)) {
      return res.status(403).json({ error: 'Only SELECT queries are allowed' });
    }

    // Enforce row limit if not present
    let finalSql = trimmedSql;
    if (!trimmedSql.match(/LIMIT\s+\d+/i)) {
      finalSql = `${trimmedSql} LIMIT 1000`;
    }

    // Execute query
    const results = await query(finalSql);
    
    res.json(results);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

export default router;
