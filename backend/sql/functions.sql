-- File: backend/sql/functions.sql
-- Execute this after importing MySQL Local.session.sql

USE dcds_project;

DELIMITER $$

-- Function 1: pollution_per_capita - Returns total_pollution / total_population (NULL-safe)
DROP FUNCTION IF EXISTS pollution_per_capita$$
CREATE FUNCTION pollution_per_capita(p_city_id INT)
RETURNS DECIMAL(10,4)
DETERMINISTIC
READS SQL DATA
BEGIN
  DECLARE total_poll DECIMAL(10,2);
  DECLARE total_pop BIGINT;
  
  -- Get total pollution from emissions_by_city
  SELECT total_pollution INTO total_poll
  FROM emissions_by_city
  WHERE city_id = p_city_id
  LIMIT 1;
  
  -- Get total population
  SELECT total_population INTO total_pop
  FROM population
  WHERE city_id = p_city_id
  LIMIT 1;
  
  -- NULL-safe division
  IF total_pop IS NULL OR total_pop = 0 OR total_poll IS NULL THEN
    RETURN NULL;
  END IF;
  
  -- Return pollution per capita (tonnes per person)
  RETURN total_poll / total_pop;
END$$

-- Function 2: avg_pm25_last_n_days - Returns average PM2.5 for last N days
DROP FUNCTION IF EXISTS avg_pm25_last_n_days$$
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
END$$

DELIMITER ;

-- Test functions
SELECT 
  city_name, 
  pollution_per_capita(city_id) as pollution_per_capita,
  avg_pm25_last_n_days(city_id, 7) as avg_pm25_7days
FROM cities
LIMIT 5;
