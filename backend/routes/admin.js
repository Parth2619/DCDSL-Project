// File: backend/routes/admin.js
import express from 'express';
import multer from 'multer';
import { query } from '../config/db.js';
import { parse } from 'csv-parse/sync';
import fs from 'fs/promises';

const router = express.Router();
const upload = multer({ dest: 'uploads/' });

// POST /api/admin/upload/aqi - Upload CSV with validation and staging
router.post('/upload/aqi', upload.single('file'), async (req, res, next) => {
  let filePath = null;
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    filePath = req.file.path;
    const fileContent = await fs.readFile(filePath, 'utf-8');
    
    // Parse CSV
    const records = parse(fileContent, {
      columns: true,
      skip_empty_lines: true,
      trim: true
    });

    // Validate required columns
    const requiredColumns = ['city_id', 'station_id', 'date', 'aqi_value'];
    if (records.length > 0) {
      const firstRow = records[0];
      const missingColumns = requiredColumns.filter(col => !(col in firstRow));
      if (missingColumns.length > 0) {
        throw new Error(`Missing required columns: ${missingColumns.join(', ')}`);
      }
    }

    // Create staging table if not exists
    await query(`
      CREATE TABLE IF NOT EXISTS staged_aqi (
        city_id INT,
        station_id INT,
        date DATE,
        aqi_value INT
      )
    `);

    // Clear staging table
    await query('TRUNCATE TABLE staged_aqi');

    // Validate and insert into staging
    const errors = [];
    let inserted = 0;
    
    for (let i = 0; i < records.length; i++) {
      const row = records[i];
      try {
        await query(
          'INSERT INTO staged_aqi (city_id, station_id, date, aqi_value) VALUES (?, ?, ?, ?)',
          [row.city_id, row.station_id, row.date, row.aqi_value]
        );
        inserted++;
      } catch (err) {
        errors.push({ row: i + 2, data: row, error: err.message });
      }
    }

    // Only commit if no errors
    if (errors.length === 0 && inserted > 0) {
      await query('CALL commit_staged_aqi()');
    }

    // Cleanup
    await fs.unlink(filePath);

    res.json({ 
      inserted,
      failed: errors.length,
      errors: errors.slice(0, 10) // Return first 10 errors only
    });
  } catch (error) {
    // Cleanup on error
    if (filePath) {
      await fs.unlink(filePath).catch(() => {});
    }
    next(error);
  }
});

// POST /api/admin/run/aggregate - Trigger nightly aggregation stored procedure
router.post('/run/aggregate', async (req, res, next) => {
  try {
    await query('CALL nightly_aggregate()');
    res.json({ success: true });
  } catch (error) {
    next(error);
  }
});

export default router;
