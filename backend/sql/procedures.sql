-- File: backend/sql/procedures.sql
-- Execute this after importing MySQL Local.session.sql

USE dcds_project;

DELIMITER $$

-- Procedure 1: commit_staged_aqi - Moves rows from staged_aqi to aqi table transactionally
DROP PROCEDURE IF EXISTS commit_staged_aqi$$
CREATE PROCEDURE commit_staged_aqi()
BEGIN
  DECLARE row_count INT;
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;
  
  START TRANSACTION;
  
  -- Insert from staged_aqi to aqi table (update on duplicate)
  INSERT INTO aqi (city_id, station_id, date, aqi_value)
  SELECT city_id, station_id, date, aqi_value
  FROM staged_aqi
  ON DUPLICATE KEY UPDATE
    aqi_value = VALUES(aqi_value);
  
  SET row_count = ROW_COUNT();
  
  -- Clear staging table
  TRUNCATE TABLE staged_aqi;
  
  COMMIT;
  
  SELECT CONCAT('Committed ', row_count, ' rows to aqi table') as message;
END$$

-- Procedure 2: nightly_aggregate - Updates emissions_by_city total_pollution from vehicle emissions
DROP PROCEDURE IF EXISTS nightly_aggregate$$
CREATE PROCEDURE nightly_aggregate()
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;
  
  START TRANSACTION;
  
  -- Update total emissions from vehicle_info aggregation
  UPDATE emissions_by_city e
  SET e.pollution_transport = (
    SELECT IFNULL(SUM(v.total_emission), 0)
    FROM vehicle_info v
    WHERE v.city_id = e.city_id
  );
  
  -- Recalculate total_pollution
  UPDATE emissions_by_city
  SET total_pollution = 
    pollution_transport + 
    pollution_construction + 
    pollution_industry + 
    pollution_residential + 
    pollution_other;
  
  COMMIT;
  
  SELECT 'Nightly aggregation completed' as message;
END$$

DELIMITER ;

-- Test procedures (uncomment to test)
-- CALL nightly_aggregate();
