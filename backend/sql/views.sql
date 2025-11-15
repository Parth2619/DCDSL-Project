-- File: backend/sql/views.sql
-- Execute this after importing MySQL Local.session.sql

USE dcds_project;

-- View 1: city_summary - Used by /api/dashboard endpoint
CREATE OR REPLACE VIEW city_summary AS
SELECT 
  c.city_id,
  c.city_name,
  c.state_name,
  AVG(recent_aqi.aqi_value) as aqi_7day_avg,
  e.total_pollution,
  p.total_population,
  COUNT(DISTINCT s.station_id) as station_count
FROM cities c
LEFT JOIN stations s ON c.city_id = s.city_id
LEFT JOIN emissions_by_city e ON c.city_id = e.city_id
LEFT JOIN population p ON c.city_id = p.city_id
LEFT JOIN (
  SELECT city_id, station_id, date, aqi_value
  FROM aqi
  WHERE date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
) recent_aqi ON c.city_id = recent_aqi.city_id
GROUP BY c.city_id, c.city_name, c.state_name, e.total_pollution, p.total_population;

-- View 2: health_summary - Used by /api/reports/health endpoint
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
  ROUND((h.asthma_cases * 100000.0 / NULLIF(p.total_population, 0)), 2) as asthma_per_100k,
  ROUND((h.lung_cancer_cases * 100000.0 / NULLIF(p.total_population, 0)), 2) as lung_cancer_per_100k,
  ROUND((h.respiratory_cases * 100000.0 / NULLIF(p.total_population, 0)), 2) as respiratory_per_100k,
  ROUND((h.pollution_deaths * 100000.0 / NULLIF(p.total_population, 0)), 2) as deaths_per_100k
FROM health_impact h
JOIN cities c ON h.city_id = c.city_id
JOIN population p ON h.city_id = p.city_id AND h.year = p.year;

-- Test the views
SELECT * FROM city_summary ORDER BY aqi_7day_avg DESC LIMIT 5;
SELECT * FROM health_summary WHERE year = 2024 LIMIT 5;
