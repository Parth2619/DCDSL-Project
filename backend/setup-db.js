// File: backend/setup-db.js
// Quick script to set up SQL functions, views, and procedures
import mysql from 'mysql2/promise';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables
dotenv.config({ path: path.join(__dirname, '.env') });

async function setupDatabase() {
  const connection = await mysql.createConnection({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME
  });

  console.log('✅ Connected to database');

  try {
    // Drop existing objects
    console.log('\n🗑️  Dropping existing objects...');
    await connection.query('DROP FUNCTION IF EXISTS pollution_per_capita');
    await connection.query('DROP FUNCTION IF EXISTS avg_pm25_last_n_days');
    await connection.query('DROP VIEW IF EXISTS city_summary');
    await connection.query('DROP VIEW IF EXISTS health_summary');
    await connection.query('DROP PROCEDURE IF EXISTS commit_staged_aqi');
    await connection.query('DROP PROCEDURE IF EXISTS nightly_aggregate');

    // Create Function 1: pollution_per_capita
    console.log('\n📝 Creating pollution_per_capita function...');
    await connection.query(`
      CREATE FUNCTION pollution_per_capita(p_city_id INT)
      RETURNS DECIMAL(10,4)
      DETERMINISTIC
      READS SQL DATA
      BEGIN
        DECLARE total_poll DECIMAL(10,2);
        DECLARE total_pop BIGINT;
        
        SELECT total_pollution INTO total_poll
        FROM emissions_by_city
        WHERE city_id = p_city_id
        LIMIT 1;
        
        SELECT total_population INTO total_pop
        FROM population
        WHERE city_id = p_city_id
        LIMIT 1;
        
        IF total_pop IS NULL OR total_pop = 0 OR total_poll IS NULL THEN
          RETURN NULL;
        END IF;
        
        RETURN total_poll / total_pop;
      END
    `);
    console.log('✅ pollution_per_capita created');

    // Create Function 2: avg_pm25_last_n_days
    console.log('\n📝 Creating avg_pm25_last_n_days function...');
    await connection.query(`
      CREATE FUNCTION avg_pm25_last_n_days(p_city_id INT, n_days INT)
      RETURNS DECIMAL(6,2)
      DETERMINISTIC
      READS SQL DATA
      BEGIN
        DECLARE avg_pm DECIMAL(6,2);
        
        SELECT AVG(pm25) INTO avg_pm
        FROM pollutants
        WHERE city_id = p_city_id
          AND date >= DATE_SUB(CURDATE(), INTERVAL n_days DAY);
        
        RETURN IFNULL(avg_pm, 0);
      END
    `);
    console.log('✅ avg_pm25_last_n_days created');

    // Create View 1: city_summary
    console.log('\n📝 Creating city_summary view...');
    await connection.query(`
      CREATE VIEW city_summary AS
      SELECT 
        c.city_id,
        c.city_name,
        AVG(a.aqi_value) as aqi_7day_avg,
        e.total_pollution,
        p.total_population,
        COUNT(DISTINCT s.station_id) as station_count
      FROM cities c
      LEFT JOIN stations s ON c.city_id = s.city_id
      LEFT JOIN aqi a ON s.station_id = a.station_id 
        AND a.date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
      LEFT JOIN emissions_by_city e ON c.city_id = e.city_id
      LEFT JOIN population p ON c.city_id = p.city_id
      GROUP BY c.city_id, c.city_name, e.total_pollution, p.total_population
    `);
    console.log('✅ city_summary created');

    // Create View 2: health_summary
    console.log('\n📝 Creating health_summary view...');
    await connection.query(`
      CREATE VIEW health_summary AS
      SELECT 
        c.city_name,
        h.asthma_cases,
        h.pollution_deaths,
        p.total_population,
        (h.asthma_cases / NULLIF(p.total_population, 0)) * 100000 as asthma_per_100k,
        (h.pollution_deaths / NULLIF(p.total_population, 0)) * 100000 as deaths_per_100k
      FROM health_impact h
      JOIN cities c ON h.city_id = c.city_id
      JOIN population p ON h.city_id = p.city_id
    `);
    console.log('✅ health_summary created');

    // Create Procedure 1: commit_staged_aqi
    console.log('\n📝 Creating commit_staged_aqi procedure...');
    await connection.query(`
      CREATE PROCEDURE commit_staged_aqi()
      BEGIN
        DECLARE EXIT HANDLER FOR SQLEXCEPTION
        BEGIN
          ROLLBACK;
          SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Failed to commit staged AQI data';
        END;
        
        START TRANSACTION;
        
        INSERT INTO aqi (station_id, date, aqi_value)
        SELECT station_id, date, aqi_value
        FROM staged_aqi;
        
        DELETE FROM staged_aqi;
        
        COMMIT;
      END
    `);
    console.log('✅ commit_staged_aqi created');

    // Create Procedure 2: nightly_aggregate
    console.log('\n📝 Creating nightly_aggregate procedure...');
    await connection.query(`
      CREATE PROCEDURE nightly_aggregate()
      BEGIN
        UPDATE emissions_by_city e
        JOIN (
          SELECT city_id, 
                 SUM(total_vehicles * emission_factor) as calc_pollution
          FROM vehicle_info
          GROUP BY city_id
        ) v ON e.city_id = v.city_id
        SET e.total_pollution = v.calc_pollution;
      END
    `);
    console.log('✅ nightly_aggregate created');

    console.log('\n🎉 Database setup completed successfully!');
    console.log('\nYou can now restart the backend server.');
    console.log('The dashboard should load without errors.\n');

  } catch (error) {
    console.error('❌ Error setting up database:', error.message);
    if (error.sql) {
      console.error('Failed SQL:', error.sql.substring(0, 200));
    }
  } finally {
    await connection.end();
  }
}

setupDatabase().catch(console.error);
