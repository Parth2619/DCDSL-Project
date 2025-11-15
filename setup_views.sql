-- Quick setup script to create the required database views
-- Run this file with: mysql -u root -p dcds_project < setup_views.sql

USE dcds_project;

-- View 1: City Summary with 7-day average AQI
CREATE OR REPLACE VIEW city_summary AS
SELECT 
  c.city_id,
  c.city_name,
  c.state_name,
  COUNT(DISTINCT s.station_id) as station_count,
  AVG(recent_aqi.aqi_value) as avg_aqi_7day,
  MAX(recent_aqi.date) as latest_date
FROM cities c
LEFT JOIN stations s ON c.city_id = s.city_id
LEFT JOIN (
  SELECT city_id, station_id, date, aqi_value
  FROM aqi
  WHERE date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
) recent_aqi ON c.city_id = recent_aqi.city_id
GROUP BY c.city_id, c.city_name, c.state_name;

-- View 2: Health Summary with population-adjusted metrics
CREATE OR REPLACE VIEW health_summary AS
SELECT 
  h.city_id,
  c.city_name,
  c.state_name,
  h.year,
  h.asthma_cases,
  h.lung_cancer_cases,
  h.respiratory_cases,
  h.hospital_visits,
  h.pollution_deaths,
  p.total_population,
  ROUND((h.asthma_cases * 100000.0 / p.total_population), 2) as asthma_per_100k,
  ROUND((h.pollution_deaths * 100000.0 / p.total_population), 2) as deaths_per_100k
FROM health_impact h
JOIN cities c ON h.city_id = c.city_id
JOIN population p ON h.city_id = p.city_id AND h.year = p.year;

SELECT 'Views created successfully!' as Status;
