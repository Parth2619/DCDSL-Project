# 🏗️ Project Architecture Explanation
## Air Quality Monitoring System - Full Stack Implementation

---

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Technology Stack](#technology-stack)
3. [Database Layer](#database-layer)
4. [Backend Layer](#backend-layer)
5. [Frontend Layer](#frontend-layer)
6. [How They Connect](#how-they-connect)
7. [Request-Response Flow](#request-response-flow)
8. [CRUD Operations Example](#crud-operations-example)

---

## 1. System Overview

This is a **3-Tier Architecture** web application:

```
┌─────────────────────────────────────────────────────────┐
│                    USER BROWSER                         │
│           (Chrome, Firefox, Edge, etc.)                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP Request/Response
                     │
┌────────────────────▼────────────────────────────────────┐
│                  FRONTEND LAYER                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  HTML Templates (Jinja2)                        │   │
│  │  - dashboard.html, cities.html, analytics.html  │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  CSS (Bootstrap + Custom)                       │   │
│  │  - style.css                                    │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  JavaScript (jQuery + Chart.js)                 │   │
│  │  - main.js, DataTables, Modal popups           │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ AJAX / Form Submission
                     │
┌────────────────────▼────────────────────────────────────┐
│                   BACKEND LAYER                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Flask Web Framework (Python)                   │   │
│  │  - app.py (Main application file)              │   │
│  │  - Routes (URLs → Functions)                    │   │
│  │  - Request handling                             │   │
│  │  - Response generation                          │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  Business Logic                                 │   │
│  │  - Data validation                              │   │
│  │  - Authentication & Authorization               │   │
│  │  - Error handling                               │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  Database Connection Pool (database.py)         │   │
│  │  - Connection management                        │   │
│  │  - Query execution                              │   │
│  │  - Transaction handling                         │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ SQL Queries
                     │
┌────────────────────▼────────────────────────────────────┐
│                   DATABASE LAYER                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │  MySQL Database Server                          │   │
│  │  Database: dcds_project                         │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  Tables:                                        │   │
│  │  - cities (11 cities)                           │   │
│  │  - aqi (4,026 air quality records)             │   │
│  │  - pollutants (PM2.5, PM10, NO2, SO2, CO, O3)  │   │
│  │  - users (authentication)                       │   │
│  │  - stations (monitoring stations)               │   │
│  │  - health_impact (disease data)                 │   │
│  │  - emissions (pollution sources)                │   │
│  │  - vehicles (traffic data)                      │   │
│  │  - waste_management                             │   │
│  │  - audit_log (tracking changes)                 │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Technology Stack

### **Frontend (Client-Side)**
| Technology | Purpose | Files |
|------------|---------|-------|
| **HTML5** | Structure of web pages | `templates/*.html` |
| **CSS3** | Styling and layout | `static/css/style.css` |
| **Bootstrap 5.3** | Responsive UI framework | CDN link in templates |
| **JavaScript** | Interactive behavior | `static/js/main.js` |
| **jQuery 3.7** | DOM manipulation | CDN link |
| **Chart.js 4.4** | Data visualization (graphs) | CDN link |
| **DataTables 1.13** | Interactive tables | CDN link |
| **Font Awesome 6.4** | Icons | CDN link |

### **Backend (Server-Side)**
| Technology | Purpose | Files |
|------------|---------|-------|
| **Python 3.14** | Programming language | All `.py` files |
| **Flask 3.0** | Web framework | `app.py` |
| **Jinja2** | Template engine (HTML + Python) | Embedded in Flask |
| **Werkzeug** | Security (password hashing) | `from werkzeug.security` |
| **MySQL Connector** | Database driver | `database.py` |

### **Database**
| Technology | Purpose | Files |
|------------|---------|-------|
| **MySQL 8.0** | Relational database | `DCDS Project.sql` |
| **Connection Pooling** | Performance optimization | `database.py` |

---

## 3. Database Layer

### **File: `database.py`**

This file handles ALL database connections:

```python
from mysql.connector import pooling
import mysql.connector
from config import Config

# ============================================
# CONNECTION POOL CREATION
# ============================================
# Instead of creating a new connection for each request,
# we create a POOL of 10 reusable connections
connection_pool = pooling.MySQLConnectionPool(
    pool_name="dcds_pool",
    pool_size=10,           # 10 connections ready to use
    host=Config.DB_HOST,    # localhost
    user=Config.DB_USER,    # root
    password=Config.DB_PASSWORD,  # 2630
    database=Config.DB_NAME       # dcds_project
)

# ============================================
# GET CONNECTION FROM POOL
# ============================================
def get_db_connection():
    """
    Get a connection from the pool (not creating new one!)
    This is FAST because connection already exists
    """
    return connection_pool.get_connection()

# ============================================
# EXECUTE QUERY (SELECT, INSERT, UPDATE, DELETE)
# ============================================
def execute_query(query, params=None, fetch=False):
    """
    This function is used EVERYWHERE in the project
    - query: SQL statement (SELECT, INSERT, UPDATE, DELETE)
    - params: Values to insert safely (prevents SQL injection)
    - fetch: True for SELECT, False for INSERT/UPDATE/DELETE
    """
    connection = None
    cursor = None
    try:
        # Step 1: Get connection from pool
        connection = get_db_connection()
        
        # Step 2: Create cursor (used to execute queries)
        cursor = connection.cursor(dictionary=True)
        
        # Step 3: Execute the SQL query with parameters
        cursor.execute(query, params or ())
        
        # Step 4: Handle result based on query type
        if fetch:
            # SELECT query - return data
            result = cursor.fetchall()
            return result
        else:
            # INSERT/UPDATE/DELETE - save changes
            connection.commit()
            return True
            
    except Exception as e:
        # If error, rollback changes
        if connection:
            connection.rollback()
        logger.error(f"Query execution error: {e}")
        return None if fetch else False
        
    finally:
        # Step 5: Always close cursor and return connection to pool
        if cursor:
            cursor.close()
        if connection:
            connection.close()  # Returns to pool, doesn't actually close!
```

### **Why Connection Pooling?**

**Without Pool:**
```
Request 1 → Create Connection (slow) → Query → Close Connection
Request 2 → Create Connection (slow) → Query → Close Connection
Request 3 → Create Connection (slow) → Query → Close Connection
```

**With Pool (What we have):**
```
Startup → Create 10 Connections (one-time)

Request 1 → Get Connection from Pool (fast) → Query → Return to Pool
Request 2 → Get Connection from Pool (fast) → Query → Return to Pool
Request 3 → Get Connection from Pool (fast) → Query → Return to Pool
```

---

## 4. Backend Layer

### **File: `app.py` (1,467 lines)**

This is the **heart** of the application. It handles:

#### **A) Application Setup**
```python
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import execute_query, get_db_connection
from config import Config
import logging

# Create Flask application
app = Flask(__name__)
app.secret_key = Config.SECRET_KEY  # For sessions and security

# Setup logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

#### **B) Routes (URL → Function Mapping)**

Flask uses **decorators** to map URLs to functions:

```python
# Example 1: Dashboard Route
@app.route('/dashboard')
@login_required  # User must be logged in
def dashboard():
    """
    When user visits http://127.0.0.1:5000/dashboard
    This function runs automatically
    """
    # Step 1: Get data from database
    query = "SELECT city_name, AVG(aqi_value) as avg_aqi FROM aqi GROUP BY city_name"
    aqi_data = execute_query(query, fetch=True)
    
    # Step 2: Render HTML template with data
    return render_template('dashboard.html', aqi_data=aqi_data)

# Example 2: Cities Route
@app.route('/cities')
@login_required
def cities():
    """When user visits /cities"""
    # Get all cities from database
    cities_query = """
        SELECT c.*, 
               COUNT(DISTINCT s.station_id) as station_count,
               COUNT(DISTINCT a.aqi_id) as aqi_count
        FROM cities c
        LEFT JOIN stations s ON c.city_id = s.city_id
        LEFT JOIN aqi a ON c.city_id = a.city_id
        GROUP BY c.city_id
    """
    cities_data = execute_query(cities_query, fetch=True)
    
    # Get AQI data for chart
    aqi_query = """
        SELECT c.city_name, ROUND(AVG(a.aqi_value), 2) as avg_aqi
        FROM cities c
        LEFT JOIN aqi a ON c.city_id = a.city_id
        GROUP BY c.city_id
        ORDER BY avg_aqi DESC
        LIMIT 10
    """
    aqi_data = execute_query(aqi_query, fetch=True)
    
    # Render template with data
    return render_template('cities.html', 
                         cities=cities_data, 
                         aqi_data=aqi_data)

# Example 3: Add City (POST request)
@app.route('/cities/add', methods=['POST'])
@admin_required  # Only admin can add
def add_city():
    """When admin submits the Add City form"""
    # Step 1: Get form data from frontend
    city_id = request.form.get('city_id')
    city_name = request.form.get('city_name')
    pin_code = request.form.get('pin_code')
    state_name = request.form.get('state_name')
    
    # Step 2: Validate data (19 validation checks!)
    if not city_name or len(city_name) < 2:
        flash('City name must be at least 2 characters!', 'danger')
        return redirect(url_for('cities'))
    
    # Step 3: Check for duplicates
    check_query = "SELECT * FROM cities WHERE city_name = %s"
    existing = execute_query(check_query, (city_name,), fetch=True)
    
    if existing:
        flash('City already exists!', 'warning')
        return redirect(url_for('cities'))
    
    # Step 4: Insert into database
    insert_query = """
        INSERT INTO cities (city_id, city_name, pin_code, state_name) 
        VALUES (%s, %s, %s, %s)
    """
    result = execute_query(insert_query, (city_id, city_name, pin_code, state_name))
    
    # Step 5: Show success message
    if result:
        flash(f'City {city_name} added successfully!', 'success')
    else:
        flash('Error adding city!', 'danger')
    
    return redirect(url_for('cities'))

# Example 4: Update AQI (POST request)
@app.route('/cities/update-aqi/<int:city_id>', methods=['POST'])
@admin_required
def update_city_aqi(city_id):
    """When admin updates AQI values"""
    # Get form data
    aqi_value = request.form.get('aqi_value')
    date = request.form.get('date')
    pm25 = request.form.get('pm25')
    pm10 = request.form.get('pm10')
    # ... get all pollutants
    
    # Validation (13 checks!)
    if not aqi_value or not date:
        flash('AQI and date are required!', 'danger')
        return redirect(url_for('cities'))
    
    # Check if AQI is in valid range
    if float(aqi_value) < 0 or float(aqi_value) > 500:
        flash('AQI must be between 0 and 500!', 'danger')
        return redirect(url_for('cities'))
    
    # Check if record exists
    check_query = "SELECT * FROM pollutants WHERE city_id = %s AND date = %s"
    existing = execute_query(check_query, (city_id, date), fetch=True)
    
    if existing:
        # UPDATE existing record
        update_query = """
            UPDATE pollutants
            SET pm25 = %s, pm10 = %s, no2 = %s, so2 = %s, co = %s, o3 = %s
            WHERE city_id = %s AND date = %s
        """
        execute_query(update_query, (pm25, pm10, no2, so2, co, o3, city_id, date))
        
        # Also update AQI table
        aqi_update = "UPDATE aqi SET aqi_value = %s WHERE city_id = %s AND date = %s"
        execute_query(aqi_update, (aqi_value, city_id, date))
        
        flash('AQI updated successfully!', 'success')
    else:
        # INSERT new record
        insert_query = """
            INSERT INTO pollutants (city_id, date, pm25, pm10, no2, so2, co, o3)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        execute_query(insert_query, (city_id, date, pm25, pm10, no2, so2, co, o3))
        
        aqi_insert = "INSERT INTO aqi (city_id, date, aqi_value) VALUES (%s, %s, %s)"
        execute_query(aqi_insert, (city_id, date, aqi_value))
        
        flash('AQI added successfully!', 'success')
    
    return redirect(url_for('cities'))
```

#### **C) Authentication & Security**

```python
# Decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first!', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator to check if user is admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required!', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check credentials in database
        query = "SELECT * FROM users WHERE username = %s"
        user = execute_query(query, (username,), fetch=True)
        
        if user and check_password_hash(user[0]['password'], password):
            # Login successful - store in session
            session['user_id'] = user[0]['user_id']
            session['username'] = user[0]['username']
            session['role'] = user[0]['role']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    
    return render_template('login.html')
```

---

## 5. Frontend Layer

### **A) HTML Templates (Jinja2)**

**File: `templates/cities.html`**

Jinja2 allows Python code inside HTML:

```html
{% extends "base.html" %}

{% block content %}
<div class="container">
    <h2>Cities Management</h2>
    
    <!-- Button to add new city -->
    {% if role == 'admin' %}
    <button data-bs-toggle="modal" data-bs-target="#addCityModal">
        Add New City
    </button>
    {% endif %}
    
    <!-- Display cities in table -->
    <table class="table" id="citiesTable">
        <thead>
            <tr>
                <th>City ID</th>
                <th>City Name</th>
                <th>Pin Code</th>
                <th>State</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <!-- Loop through cities from backend -->
            {% for city in cities %}
            <tr>
                <td>{{ city.city_id }}</td>
                <td>{{ city.city_name }}</td>
                <td>{{ city.pin_code }}</td>
                <td>{{ city.state_name }}</td>
                <td>
                    <!-- Update AQI button -->
                    <button class="btn btn-warning update-aqi-btn" 
                            data-city='{{ city | tojson | safe }}'>
                        AQI
                    </button>
                    
                    <!-- Delete button -->
                    <button onclick="deleteCity({{ city.city_id }}, '{{ city.city_name }}')">
                        Delete
                    </button>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <!-- AQI Chart using Chart.js -->
    <canvas id="aqiChart"></canvas>
    
    <script>
        // Convert Python data to JavaScript
        const aqiData = {{ aqi_data | tojson | safe }};
        
        // Create chart
        const ctx = document.getElementById('aqiChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: aqiData.map(d => d.city_name),
                datasets: [{
                    label: 'Average AQI',
                    data: aqiData.map(d => d.avg_aqi),
                    backgroundColor: aqiData.map(d => {
                        if (d.avg_aqi <= 50) return 'green';
                        if (d.avg_aqi <= 100) return 'yellow';
                        if (d.avg_aqi <= 150) return 'orange';
                        if (d.avg_aqi <= 200) return 'red';
                        if (d.avg_aqi <= 300) return 'purple';
                        return 'maroon';
                    })
                }]
            }
        });
    </script>
</div>

<!-- Modal for updating AQI -->
<div class="modal" id="updateAQIModal">
    <form method="POST" id="updateAQIForm">
        <input type="hidden" name="city_id" id="aqi_city_id">
        
        <label>AQI Value:</label>
        <input type="number" name="aqi_value" min="0" max="500" required>
        
        <label>Date:</label>
        <input type="date" name="date" required>
        
        <label>PM2.5:</label>
        <input type="number" name="pm25" step="0.01">
        
        <!-- More pollutant fields... -->
        
        <button type="submit">Update AQI</button>
    </form>
</div>

<script>
    // Function to open modal and populate data
    function updateAQI(city) {
        document.getElementById('aqi_city_id').value = city.city_id;
        document.getElementById('updateAQIForm').action = '/cities/update-aqi/' + city.city_id;
        
        // Show modal
        new bootstrap.Modal(document.getElementById('updateAQIModal')).show();
    }
    
    // Event delegation for dynamically loaded buttons
    $(document).ready(function() {
        $('#citiesTable').DataTable();
        
        $('#citiesTable').on('click', '.update-aqi-btn', function() {
            const cityData = $(this).data('city');
            updateAQI(cityData);
        });
    });
</script>
{% endblock %}
```

### **B) CSS (Styling)**

**File: `static/css/style.css`**

```css
/* Custom styles for the application */
.navbar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.card {
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
}

.card:hover {
    transform: translateY(-5px);
}

.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
}

/* AQI color coding */
.aqi-good { background-color: #00e400; }
.aqi-moderate { background-color: #ffff00; }
.aqi-unhealthy { background-color: #ff7e00; }
.aqi-very-unhealthy { background-color: #ff0000; }
.aqi-hazardous { background-color: #8f3f97; }
```

### **C) JavaScript (Interactivity)**

**File: `static/js/main.js`**

```javascript
// Initialize DataTables for all tables
$(document).ready(function() {
    $('.table').DataTable({
        pageLength: 10,
        order: [[1, 'asc']]
    });
});

// Flash message auto-hide
setTimeout(function() {
    $('.alert').fadeOut('slow');
}, 3000);

// Confirm delete action
function confirmDelete(itemName) {
    return confirm(`Are you sure you want to delete ${itemName}?`);
}

// AJAX request for live city search
function searchCity(cityName) {
    $.ajax({
        url: '/api/city-search',
        method: 'GET',
        data: { city: cityName },
        success: function(response) {
            // Update UI with response data
            $('#live_aqi').text(response.live_aqi);
            $('#temperature').text(response.temperature + '°C');
            $('#humidity').text(response.humidity + '%');
            // ... update other fields
        },
        error: function(error) {
            console.error('Error fetching city data:', error);
        }
    });
}
```

---

## 6. How They Connect

### **Data Flow Diagram:**

```
1. USER ACTION
   User clicks "Update AQI" button on Cities page
   
   ↓

2. FRONTEND (JavaScript)
   - Captures button click event
   - Extracts city data from button's data attribute
   - Populates modal form with city info
   - Shows modal popup
   
   ↓

3. USER FILLS FORM
   - Enters AQI value: 250
   - Selects date: 2024-11-04
   - Optionally enters pollutants
   
   ↓

4. FORM SUBMISSION
   User clicks "Update AQI" button in modal
   
   ↓

5. HTTP POST REQUEST
   Browser sends POST request to:
   URL: http://127.0.0.1:5000/cities/update-aqi/1
   Data: {
       aqi_value: 250,
       date: '2024-11-04',
       pm25: 75.5,
       pm10: 150.2,
       ...
   }
   
   ↓

6. BACKEND (Flask Route)
   @app.route('/cities/update-aqi/<int:city_id>', methods=['POST'])
   def update_city_aqi(city_id):
       - Receives request
       - Extracts form data: request.form.get('aqi_value')
       - Validates data (13 validation checks)
       
       ↓

7. DATABASE QUERY (database.py)
   - Checks if record exists:
     SELECT * FROM pollutants WHERE city_id = 1 AND date = '2024-11-04'
   
   - If exists: UPDATE
     UPDATE pollutants SET pm25 = 75.5, pm10 = 150.2 ...
     UPDATE aqi SET aqi_value = 250 ...
   
   - If not exists: INSERT
     INSERT INTO pollutants VALUES (...)
     INSERT INTO aqi VALUES (...)
   
   ↓

8. DATABASE (MySQL)
   - Executes SQL query
   - Updates/Inserts data
   - Commits transaction
   - Returns success/failure
   
   ↓

9. BACKEND RESPONSE
   - If success: flash('✅ AQI updated successfully!', 'success')
   - If error: flash('❌ Error: ...', 'danger')
   - Redirects to: return redirect(url_for('cities'))
   
   ↓

10. HTTP REDIRECT
    Server sends redirect response:
    Status: 302 Found
    Location: /cities
    
    ↓

11. BROWSER FOLLOWS REDIRECT
    Browser makes new GET request to /cities
    
    ↓

12. BACKEND RENDERS PAGE
    @app.route('/cities')
    def cities():
        - Fetches updated data from database
        - Renders template with new data
        - Includes flash message
    
    ↓

13. FRONTEND DISPLAYS
    - Page reloads with updated data
    - Success message appears at top
    - Table shows updated AQI value
    - Chart updates with new data
    
    ↓

14. USER SEES RESULT
    ✅ "AQI values for Mumbai updated successfully!"
```

---

## 7. Request-Response Flow

### **Example: Loading Cities Page**

```python
# STEP 1: User types URL in browser
http://127.0.0.1:5000/cities

# STEP 2: Browser sends HTTP GET request
GET /cities HTTP/1.1
Host: 127.0.0.1:5000
Cookie: session=abc123...

# STEP 3: Flask receives request and routes to function
@app.route('/cities')
@login_required
def cities():
    
    # STEP 4: Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # STEP 5: Execute database queries
    cities_query = "SELECT * FROM cities"
    cities_data = execute_query(cities_query, fetch=True)
    
    # This calls database.py:
    # - get_db_connection() → Gets connection from pool
    # - cursor.execute(query) → Runs SQL
    # - cursor.fetchall() → Gets results
    # - Returns: [
    #     {'city_id': 1, 'city_name': 'Mumbai', ...},
    #     {'city_id': 2, 'city_name': 'Delhi', ...},
    #     ...
    #   ]
    
    aqi_query = "SELECT city_name, AVG(aqi_value) as avg_aqi FROM aqi GROUP BY city_name"
    aqi_data = execute_query(aqi_query, fetch=True)
    
    # Returns: [
    #     {'city_name': 'Pune', 'avg_aqi': 404.43},
    #     {'city_name': 'Delhi', 'avg_aqi': 303.66},
    #     ...
    # ]
    
    # STEP 6: Render HTML template with data
    return render_template('cities.html', 
                         cities=cities_data,
                         aqi_data=aqi_data,
                         role=session.get('role'))
    
    # This does:
    # - Opens templates/cities.html
    # - Replaces {{ cities }} with cities_data
    # - Replaces {{ aqi_data }} with aqi_data
    # - Replaces {{ role }} with 'admin'
    # - Generates final HTML

# STEP 7: Flask sends HTTP response
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 19934

<!DOCTYPE html>
<html>
<head>
    <title>Cities Management</title>
    ...
</head>
<body>
    <table>
        <tr>
            <td>1</td>
            <td>Mumbai</td>
            ...
        </tr>
        ...
    </table>
    
    <script>
        const aqiData = [
            {"city_name": "Pune", "avg_aqi": 404.43},
            {"city_name": "Delhi", "avg_aqi": 303.66},
            ...
        ];
        
        // Create chart with this data
        new Chart(...);
    </script>
</body>
</html>

# STEP 8: Browser receives and renders HTML
# - Parses HTML
# - Loads CSS from static/css/style.css
# - Loads JS from static/js/main.js
# - Executes JavaScript
# - Draws Chart.js chart
# - Displays page to user
```

---

## 8. CRUD Operations Example

### **CREATE (Insert New City)**

```
┌──────────────────────────────────────────────────────────┐
│ FRONTEND: cities.html                                    │
├──────────────────────────────────────────────────────────┤
│ <form method="POST" action="/cities/add">               │
│     <input name="city_id" value="12">                   │
│     <input name="city_name" value="Goa">                │
│     <input name="pin_code" value="403001">              │
│     <input name="state_name" value="Goa">               │
│     <button type="submit">Add City</button>             │
│ </form>                                                  │
└────────────────────┬─────────────────────────────────────┘
                     │ POST /cities/add
                     │ Form Data: city_id=12, city_name=Goa, ...
                     ↓
┌──────────────────────────────────────────────────────────┐
│ BACKEND: app.py                                          │
├──────────────────────────────────────────────────────────┤
│ @app.route('/cities/add', methods=['POST'])             │
│ def add_city():                                          │
│     # Get form data                                      │
│     city_id = request.form.get('city_id')               │
│     city_name = request.form.get('city_name')           │
│     pin_code = request.form.get('pin_code')             │
│     state_name = request.form.get('state_name')         │
│                                                          │
│     # Validate (19 checks!)                             │
│     if len(city_name) < 2:                              │
│         flash('City name too short!', 'danger')         │
│         return redirect(url_for('cities'))              │
│                                                          │
│     # Check duplicate                                    │
│     check = "SELECT * FROM cities WHERE city_name = %s" │
│     existing = execute_query(check, (city_name,), True) │
│     if existing:                                         │
│         flash('City already exists!', 'warning')        │
│         return redirect(url_for('cities'))              │
│                                                          │
│     # Insert into database                              │
│     query = "INSERT INTO cities VALUES (%s,%s,%s,%s)"   │
│     result = execute_query(query,                       │
│              (city_id, city_name, pin_code, state_name))│
│                                                          │
│     flash('✅ City added successfully!', 'success')     │
│     return redirect(url_for('cities'))                  │
└────────────────────┬─────────────────────────────────────┘
                     │ INSERT INTO cities ...
                     ↓
┌──────────────────────────────────────────────────────────┐
│ DATABASE: database.py                                    │
├──────────────────────────────────────────────────────────┤
│ def execute_query(query, params, fetch=False):          │
│     conn = get_db_connection()  # From pool             │
│     cursor = conn.cursor()                              │
│     cursor.execute(query, params)                       │
│     conn.commit()  # Save changes                       │
│     conn.close()   # Return to pool                     │
│     return True                                          │
└────────────────────┬─────────────────────────────────────┘
                     │ SQL Query
                     ↓
┌──────────────────────────────────────────────────────────┐
│ MySQL DATABASE                                           │
├──────────────────────────────────────────────────────────┤
│ cities table:                                            │
│ +────────+───────────+──────────+────────────+          │
│ | city_id| city_name | pin_code | state_name |          │
│ +────────+───────────+──────────+────────────+          │
│ |   1    | Mumbai    | 400001   | MH         |          │
│ |   2    | Delhi     | 110001   | DL         |          │
│ |  ...   | ...       | ...      | ...        |          │
│ |  12    | Goa       | 403001   | Goa        | ← NEW!   │
│ +────────+───────────+──────────+────────────+          │
└──────────────────────────────────────────────────────────┘
```

### **READ (Display Cities)**

```
User visits /cities
    ↓
Flask: cities() function runs
    ↓
Query: SELECT * FROM cities
    ↓
Database returns: [{'city_id': 1, 'city_name': 'Mumbai'}, ...]
    ↓
Flask: render_template('cities.html', cities=data)
    ↓
Jinja2 processes: {% for city in cities %} <tr>{{city.city_name}}</tr> {% endfor %}
    ↓
Browser displays table with all cities
```

### **UPDATE (Modify AQI)**

```
User clicks "AQI" button → Modal opens → Fills form → Clicks "Update AQI"
    ↓
POST /cities/update-aqi/1
    ↓
Flask: update_city_aqi(1) function runs
    ↓
Validate: Check AQI range 0-500, pollutants, date, etc.
    ↓
Check: SELECT * FROM pollutants WHERE city_id=1 AND date='2024-11-04'
    ↓
If exists: UPDATE pollutants SET pm25=75.5, ... WHERE city_id=1 AND date='2024-11-04'
If not: INSERT INTO pollutants VALUES (1, '2024-11-04', 75.5, ...)
    ↓
Also: UPDATE aqi SET aqi_value=250 WHERE city_id=1 AND date='2024-11-04'
    ↓
Flash message: "✅ AQI updated successfully!"
    ↓
Redirect to /cities → Page reloads with updated data
```

### **DELETE (Remove City)**

```
User clicks "Delete" button → Confirmation popup
    ↓
POST /cities/delete/5
    ↓
Flask: delete_city(5) function runs
    ↓
Query: DELETE FROM cities WHERE city_id = 5
    ↓
Database removes row
    ↓
Flash: "✅ City deleted!"
    ↓
Redirect → Page reloads without deleted city
```

---

## 9. Key Concepts to Explain to Teacher

### **1. Why Flask?**
- Lightweight Python web framework
- Easy to learn and use
- Perfect for small to medium projects
- Built-in development server
- Excellent for database-driven applications

### **2. Why MySQL?**
- Industry-standard relational database
- Excellent for structured data (cities, AQI, users)
- Supports complex queries with JOINs
- ACID compliance (data integrity)
- Free and open-source

### **3. Why Connection Pooling?**
- **Performance:** Reuses connections instead of creating new ones
- **Efficiency:** Reduces database load
- **Scalability:** Handles multiple concurrent users
- **Production-ready:** Industry best practice

### **4. Why Jinja2 Templates?**
- Separates HTML (structure) from Python (logic)
- Reusable components (base template, extends, includes)
- Secure (auto-escapes HTML to prevent XSS)
- Easy to maintain

### **5. Security Features:**
- Password hashing (Werkzeug)
- SQL injection prevention (parameterized queries)
- Session-based authentication
- Role-based access control (admin vs user)
- CSRF protection (Flask built-in)

### **6. Error Handling:**
- Try-catch blocks in Python
- Database rollback on error
- Custom 404 and 500 error pages
- User-friendly error messages
- Logging for debugging

---

## 10. Summary

### **The Connection:**

```
DATABASE (MySQL)
    ↑↓ SQL Queries
database.py (Connection Pool + Query Execution)
    ↑↓ Python Function Calls
app.py (Flask Routes + Business Logic)
    ↑↓ HTTP Requests/Responses + Template Rendering
templates/*.html (Jinja2 + HTML + JavaScript)
    ↑↓ User Interactions
USER BROWSER (Chrome, Firefox, etc.)
```

### **Data Flow:**
1. User interacts with **Frontend** (HTML/CSS/JS)
2. Browser sends HTTP request to **Backend** (Flask)
3. Flask processes request, validates data
4. Flask calls **Database** functions (database.py)
5. Database executes SQL queries on **MySQL**
6. MySQL returns results
7. Flask renders **Template** with data
8. Browser displays final **HTML page**

### **CRUD in Action:**
- **CREATE:** Form → POST → Validate → INSERT → Success
- **READ:** GET → SELECT → Render → Display
- **UPDATE:** Form → POST → Validate → UPDATE → Success
- **DELETE:** Confirm → POST → DELETE → Success

This architecture is **scalable**, **maintainable**, and follows **industry best practices**! 🚀

---

**Files to Reference During Presentation:**
1. `database.py` - Show connection pooling and execute_query
2. `app.py` - Show a complete route (e.g., cities, add_city, update_city_aqi)
3. `templates/cities.html` - Show Jinja2 syntax and form submission
4. `static/css/style.css` - Show styling
5. `static/js/main.js` - Show JavaScript interactions

Good luck with your presentation! 🎓
