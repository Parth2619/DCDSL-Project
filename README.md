# Air Quality Monitoring System

A full-stack web application for monitoring and analyzing air quality data across major Indian cities.

## 🏗️ Tech Stack

**Backend:**
- Node.js + Express v4.18.2
- MySQL 8.0 with mysql2 driver v3.6.5
- CSV parsing with csv-parse v5.5.2
- File uploads with multer v1.4.5-lts.1
- Token-based admin authentication

**Frontend:**
- React 18.2.0
- React Router v6.20.0
- Vite v5.0.8 (dev server)

## 📋 Prerequisites

- Node.js (v16 or higher)
- MySQL 8.0
- npm or yarn

## 🚀 Setup Instructions

### 1. Database Setup

```sql
-- Create database
CREATE DATABASE IF NOT EXISTS dcds_project;
USE dcds_project;

-- Import your existing database schema and data
-- (cities, stations, aqi, pollutants, emissions_by_city, population, health_impact, vehicle_info, weather tables)
```

### 2. Install SQL Functions, Views, and Procedures

Execute the SQL files in order:

```bash
# From project root
cd backend/sql

# Run in MySQL
mysql -u root -p dcds_project < functions.sql
mysql -u root -p dcds_project < views.sql
mysql -u root -p dcds_project < procedures.sql
```

**Or run manually in MySQL Workbench:**
1. Open `backend/sql/functions.sql` and execute
2. Open `backend/sql/views.sql` and execute
3. Open `backend/sql/procedures.sql` and execute

### 3. Backend Setup

```bash
cd backend
npm install
```

**Configure environment variables:**

Edit `backend/.env`:
```properties
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=dcds_project

PORT=5000
NODE_ENV=development

ADMIN_TOKEN=your-secret-admin-token-here
```

**Start the backend server:**
```bash
npm start
```

Backend will run on http://localhost:5000

### 4. Frontend Setup

```bash
cd frontend
npm install
```

**Configure Vite proxy (already set in vite.config.js):**
```javascript
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://localhost:5000'
    }
  }
})
```

**Start the frontend dev server:**
```bash
npm run dev
```

Frontend will run on http://localhost:3000

## 📡 API Endpoints

### Public Endpoints

| Method | Endpoint | Description | Response Shape |
|--------|----------|-------------|----------------|
| GET | `/api/dashboard` | City dashboard with rankings | Array of cities with pollution_per_capita |
| GET | `/api/cities` | List all cities | Array of city objects |
| GET | `/api/cities/:id/profile` | City detail with AQI series | `{ city, aqi_series, pollutants }` |
| GET | `/api/stations/by-city/:cityId` | Stations in a city | Array of station objects |
| GET | `/api/stations/:id/aqi` | Station AQI time series | Array of AQI readings |
| GET | `/api/reports/health` | Health impact summary | Flat object with health metrics |
| POST | `/api/playground` | Execute SELECT queries | Array of query results |

### Protected Admin Endpoints (require `X-ADMIN-TOKEN` header)

| Method | Endpoint | Description | Response Shape |
|--------|----------|-------------|----------------|
| POST | `/api/admin/upload/aqi` | Upload AQI CSV data | `{ inserted, failed, errors }` |
| POST | `/api/admin/run/aggregate` | Run nightly aggregation | Success message |

## 🔐 Admin Authentication

All `/api/admin/*` endpoints require the `X-ADMIN-TOKEN` header:

```javascript
fetch('/api/admin/upload/aqi', {
  method: 'POST',
  headers: {
    'X-ADMIN-TOKEN': 'your-secret-admin-token-here'
  },
  body: formData
});
```

**Update admin token in both places:**
1. `backend/.env` → `ADMIN_TOKEN=your-secret-admin-token-here`
2. `frontend/src/pages/Admin.jsx` → `const ADMIN_TOKEN = 'your-secret-admin-token-here'`

## 📂 CSV Upload Format

**AQI CSV Structure:**
```csv
city_id,station_id,date,aqi_value
1,101,2024-01-15,85
1,101,2024-01-16,92
```

**CSV Validation:**
- Validates all 4 required columns
- Checks for valid numeric city_id, station_id, aqi_value
- Validates date format (YYYY-MM-DD)
- Tracks failed rows with error messages
- Returns detailed report: `{ inserted, failed, errors: [{row, reason}] }`

## 🗄️ Database Objects

### Functions
- `pollution_per_capita(city_id)` - Calculates pollution per 100k population (NULL-safe)
- `avg_pm25_last_n_days(city_id, n_days)` - Rolling PM2.5 average

### Views
- `city_summary` - Dashboard data with aqi_7day_avg, total_pollution, pollution_per_capita, station_count
- `health_summary` - Health metrics with asthma_per_100k, deaths_per_100k

### Stored Procedures
- `commit_staged_aqi()` - Transactional move from staged_aqi to aqi table
- `nightly_aggregate()` - Updates emissions_by_city from vehicle_info

## 🧪 Testing

### Test Backend Endpoints

```bash
# Dashboard
curl http://localhost:5000/api/dashboard

# Cities
curl http://localhost:5000/api/cities

# City Profile (replace 1 with actual city_id)
curl http://localhost:5000/api/cities/1/profile

# Health Report
curl http://localhost:5000/api/reports/health

# SQL Playground
curl -X POST http://localhost:5000/api/playground \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM cities LIMIT 5"}'

# Admin Upload (requires token)
curl -X POST http://localhost:5000/api/admin/upload/aqi \
  -H "X-ADMIN-TOKEN: your-secret-admin-token-here" \
  -F "file=@path/to/aqi.csv"
```

### Test Frontend

1. Open http://localhost:3000
2. Navigate through pages:
   - Dashboard → View city rankings
   - Cities → Click on any city → View AQI charts
   - SQL Playground → Execute queries
   - Admin → Upload CSV (with correct token)

## 🎨 Frontend Features

### Dashboard
- Responsive grid layout (260px min width cards)
- Color-coded AQI badges:
  - Green: ≤50 (Good)
  - Yellow: 51-100 (Moderate)
  - Orange: 101-200 (Unhealthy)
  - Red: >200 (Severe)
- Shows pollution_per_capita metric
- City ranking display

### City Profile
- AQI time series chart
- Pollutants breakdown table
- Export to CSV button

### SQL Playground
- SELECT-only query execution
- Automatic LIMIT 1000 enforcement
- Results table display
- Error handling

### Admin Panel
- CSV file upload with validation
- Failed row preview
- Nightly aggregation trigger

## 📊 Feature-to-SQL-Concept Checklist

| Feature | SQL Concept | Implementation |
|---------|-------------|----------------|
| Dashboard rankings | VIEW + Function | `city_summary` view with `pollution_per_capita()` |
| 7-day AQI average | Aggregate + GROUP BY | `AVG(aqi_value)` grouped by city |
| City profile charts | JOIN + Aggregation | Multi-table joins with DATE grouping |
| Health metrics | VIEW + Calculated Fields | `health_summary` view with per-capita ratios |
| CSV validation | Stored Procedure + Transaction | `commit_staged_aqi()` with ROLLBACK |
| Nightly aggregation | Stored Procedure | `nightly_aggregate()` updates emissions |
| PM2.5 trends | Window Function | `avg_pm25_last_n_days()` |
| SQL Playground | Prepared Statements | Parameterized queries with SELECT validation |
| Admin auth | Middleware + Header Check | `X-ADMIN-TOKEN` validation |

## 🔒 Security Features

- **SQL Injection Protection:** All queries use prepared statements with parameterized inputs
- **Admin Authentication:** Token-based middleware for admin operations
- **Query Restriction:** Playground only allows SELECT queries (regex validation)
- **Row Limit Enforcement:** Automatic LIMIT 1000 on all SELECT queries
- **Error Handling:** Transactional CSV uploads with ROLLBACK on failure
- **Input Validation:** CSV column and data type validation

## 📁 Project Structure

```
DCDSL-Project/
├── backend/
│   ├── middleware/
│   │   └── auth.js              # Admin authentication
│   ├── routes/
│   │   ├── dashboard.js         # Dashboard endpoint
│   │   ├── cities.js            # Cities endpoints
│   │   ├── stations.js          # Stations endpoints
│   │   ├── reports.js           # Health reports
│   │   ├── admin.js             # Admin upload & aggregate
│   │   └── playground.js        # SQL playground
│   ├── sql/
│   │   ├── functions.sql        # SQL functions
│   │   ├── views.sql            # SQL views
│   │   └── procedures.sql       # Stored procedures
│   ├── db.js                    # Database connection
│   ├── server.js                # Express app
│   ├── .env                     # Environment config
│   └── package.json
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx    # City rankings grid
│   │   │   ├── Cities.jsx       # Cities list
│   │   │   ├── CityProfile.jsx  # City detail with charts
│   │   │   ├── Stations.jsx     # Stations list
│   │   │   ├── StationDetail.jsx# Station AQI history
│   │   │   ├── Playground.jsx   # SQL query interface
│   │   │   └── Admin.jsx        # Admin panel
│   │   ├── App.jsx              # Main app with routes
│   │   └── App.css              # Global styles
│   ├── vite.config.js           # Vite configuration
│   └── package.json
└── README.md
```

## 🐛 Troubleshooting

### Backend won't start
- Check MySQL is running: `mysql -u root -p`
- Verify database exists: `SHOW DATABASES;`
- Check .env file has correct password
- Ensure all dependencies installed: `npm install`

### Frontend shows "Failed to load data"
- Verify backend is running on port 5000
- Check browser console for errors
- Ensure Vite proxy is configured correctly
- Test API directly: `curl http://localhost:5000/api/dashboard`

### Admin upload fails
- Verify `X-ADMIN-TOKEN` matches in .env and Admin.jsx
- Check CSV format matches: city_id,station_id,date,aqi_value
- Ensure `staged_aqi` table exists in database
- Check backend logs for specific error

### SQL Playground shows errors
- Only SELECT queries allowed (INSERT/UPDATE/DELETE blocked)
- Check for SQL syntax errors
- Verify table names exist in database
- LIMIT is automatically added (max 1000 rows)

## 📝 Development Notes

- Backend uses **flat JSON responses** (no `{success: true, data: ...}` wrapper)
- All SQL objects use `DROP IF EXISTS` for idempotent execution
- CSV upload uses `staged_aqi` table (not `aqi_staging`)
- Admin token must match in both backend .env and frontend Admin.jsx
- Functions use NULL-safe division (NULLIF to avoid divide by zero)

## 🚢 Deployment Checklist

- [ ] Change `ADMIN_TOKEN` to strong secret value
- [ ] Set `NODE_ENV=production` in backend .env
- [ ] Update `DB_PASSWORD` for production database
- [ ] Build frontend for production: `npm run build`
- [ ] Set up reverse proxy (nginx/Apache) for both servers
- [ ] Enable HTTPS with SSL certificates
- [ ] Set up database backups
- [ ] Configure firewall rules
- [ ] Add rate limiting middleware
- [ ] Set up logging and monitoring

---

**Built with ❤️ for Air Quality Monitoring**
