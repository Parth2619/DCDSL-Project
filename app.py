"""
DCDS Project - Air Quality and Environmental Data Collection System
Full Stack Web Application with Flask
Author: Generated for Academic Project
Date: November 2025
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import mysql.connector
from mysql.connector import Error
from config import Config
from datetime import datetime
import csv
import io
import json
import requests
import logging

# Import improved database module
from database import (
    get_db_connection, 
    execute_query, 
    execute_transaction, 
    check_db_health, 
    validate_data
)

app = Flask(__name__)
app.config.from_object(Config)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== Custom Template Filters ====================

@app.template_filter('datetime')
def format_datetime(value):
    """Format datetime for display in templates"""
    if value == 'now':
        return datetime.now().strftime('%B %d, %Y %I:%M %p')
    return value

# ==================== Database Helper Functions ====================

def get_db_connection():
    """Establish and return MySQL database connection"""
    try:
        connection = mysql.connector.connect(**Config.get_db_config())
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def execute_query(query, params=None, fetch=False):
    """Execute SQL query with parameters (prevents SQL injection)"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch:
            result = cursor.fetchall()
        else:
            connection.commit()
            result = cursor.lastrowid
        
        cursor.close()
        connection.close()
        return result
    except Error as e:
        print(f"Query execution error: {e}")
        return None

def log_audit(user_id, action, table_name, record_id, details):
    """Log user actions for audit trail"""
    try:
        query = """
            INSERT INTO audit_log (user_id, action, table_name, record_id, details)
            VALUES (%s, %s, %s, %s, %s)
        """
        execute_query(query, (user_id, action, table_name, record_id, details))
    except Exception as e:
        # Silently fail if audit_log table doesn't exist
        logger.warning(f"Audit logging failed (table may not exist): {e}")
        pass

# ==================== Authentication Decorators ====================

def login_required(f):
    """Decorator to protect routes - auto-login if not logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Auto-login as admin
            query = "SELECT * FROM users WHERE username = %s AND is_active = TRUE"
            user = execute_query(query, ('admin',), fetch=True)
            
            if user and len(user) > 0:
                user = user[0]
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                session['full_name'] = user['full_name']
                session['role'] = user['role']
                session['city_id'] = user['city_id']
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to protect routes - auto-login as admin if needed"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Auto-login as admin
            query = "SELECT * FROM users WHERE username = %s AND is_active = TRUE"
            user = execute_query(query, ('admin',), fetch=True)
            
            if user and len(user) > 0:
                user = user[0]
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                session['full_name'] = user['full_name']
                session['role'] = user['role']
                session['city_id'] = user['city_id']
        return f(*args, **kwargs)
    return decorated_function

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 Not Found errors"""
    logger.warning(f"404 error: {request.url}")
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors"""
    logger.error(f"500 error: {error}")
    return render_template('errors/500.html'), 500

@app.errorhandler(Exception)
def handle_exception(error):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {error}", exc_info=True)
    return render_template('errors/500.html'), 500

# ==================== Health Check Endpoint ====================

@app.route('/health-check')
def health_check():
    """Database health check endpoint for monitoring"""
    health_status = check_db_health()
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code


# ==================== Authentication Routes ====================

@app.route('/')
def index():
    """Landing page - auto-login as admin and redirect to dashboard"""
    # Auto-login as admin user
    if 'user_id' not in session:
        # Get admin user from database
        query = "SELECT * FROM users WHERE username = %s AND is_active = TRUE"
        user = execute_query(query, ('admin',), fetch=True)
        
        if user and len(user) > 0:
            user = user[0]
            # Set session variables
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            session['city_id'] = user['city_id']
            
            # Update last login
            execute_query("UPDATE users SET last_login = NOW() WHERE user_id = %s", (user['user_id'],))
    
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Validate input
        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('login.html')
        
        # Check user credentials
        query = "SELECT * FROM users WHERE username = %s AND is_active = TRUE"
        user = execute_query(query, (username,), fetch=True)
        
        if user and len(user) > 0:
            user = user[0]
            # Verify password
            if check_password_hash(user['password_hash'], password):
                # Set session variables
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                session['full_name'] = user['full_name']
                session['role'] = user['role']
                session['city_id'] = user['city_id']
                
                # Update last login
                execute_query("UPDATE users SET last_login = NOW() WHERE user_id = %s", (user['user_id'],))
                
                flash(f'Welcome back, {user["full_name"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid password.', 'danger')
        else:
            flash('Username not found.', 'danger')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        city_id = request.form.get('city_id')
        
        # Validation
        if not all([username, email, password, confirm_password, full_name]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('signup'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('signup'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('signup'))
        
        # Check if username or email already exists
        check_query = "SELECT user_id FROM users WHERE username = %s OR email = %s"
        existing = execute_query(check_query, (username, email), fetch=True)
        
        if existing:
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('signup'))
        
        # Hash password and insert user
        password_hash = generate_password_hash(password)
        insert_query = """
            INSERT INTO users (username, email, password_hash, full_name, role, city_id)
            VALUES (%s, %s, %s, %s, 'user', %s)
        """
        result = execute_query(insert_query, (username, email, password_hash, full_name, city_id))
        
        if result:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed. Please try again.', 'danger')
    
    # Get cities for dropdown
    cities = execute_query("SELECT city_id, city_name, state_name FROM cities ORDER BY city_name", fetch=True)
    return render_template('signup.html', cities=cities)

@app.route('/logout')
@login_required
def logout():
    """Logout user and clear session"""
    username = session.get('username', 'User')
    session.clear()
    flash(f'Goodbye {username}! You have been logged out.', 'info')
    return redirect(url_for('login'))

# ==================== Dashboard Routes ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with statistics and charts"""
    user_role = session.get('role')
    user_city_id = session.get('city_id')
    
    # Get statistics
    stats = {}
    
    # Total cities
    stats['total_cities'] = execute_query("SELECT COUNT(*) as count FROM cities", fetch=True)[0]['count']
    
    # Total stations
    stats['total_stations'] = execute_query("SELECT COUNT(*) as count FROM stations", fetch=True)[0]['count']
    
    # Total AQI records
    stats['total_aqi_records'] = execute_query("SELECT COUNT(*) as count FROM aqi", fetch=True)[0]['count']
    
    # Total users (admin only)
    if user_role == 'admin':
        stats['total_users'] = execute_query("SELECT COUNT(*) as count FROM users", fetch=True)[0]['count']
    
    # Average AQI by city
    if user_role == 'admin':
        aqi_by_city_query = """
            SELECT c.city_name, AVG(a.aqi_value) as avg_aqi
            FROM aqi a
            JOIN cities c ON a.city_id = c.city_id
            GROUP BY c.city_name
            ORDER BY avg_aqi DESC
            LIMIT 10
        """
    else:
        aqi_by_city_query = """
            SELECT c.city_name, AVG(a.aqi_value) as avg_aqi
            FROM aqi a
            JOIN cities c ON a.city_id = c.city_id
            WHERE a.city_id = %s
            GROUP BY c.city_name
        """
        params = (user_city_id,) if user_city_id else None
    
    stats['aqi_by_city'] = execute_query(aqi_by_city_query, 
                                         (user_city_id,) if user_role == 'user' and user_city_id else None, 
                                         fetch=True)
    
    # Vehicle distribution
    vehicle_query = """
        SELECT vehicle_id, SUM(vehicle_count) as total_count
        FROM vehicle_info
        GROUP BY vehicle_id
    """
    stats['vehicle_distribution'] = execute_query(vehicle_query, fetch=True)
    
    # Recent activities (last 10)
    if user_role == 'admin':
        activity_query = """
            SELECT al.*, u.username, u.full_name
            FROM audit_log al
            JOIN users u ON al.user_id = u.user_id
            ORDER BY al.timestamp DESC
            LIMIT 10
        """
        stats['recent_activities'] = execute_query(activity_query, fetch=True)
    else:
        activity_query = """
            SELECT al.*, u.username, u.full_name
            FROM audit_log al
            JOIN users u ON al.user_id = u.user_id
            WHERE al.user_id = %s
            ORDER BY al.timestamp DESC
            LIMIT 10
        """
        stats['recent_activities'] = execute_query(activity_query, (session['user_id'],), fetch=True)
    
    # Health impact stats
    health_query = """
        SELECT c.city_name, h.respiratory_cases, h.lung_cancer_cases, h.asthma_cases
        FROM health_impact h
        JOIN cities c ON h.city_id = c.city_id
        ORDER BY h.respiratory_cases DESC
        LIMIT 5
    """
    stats['health_impact'] = execute_query(health_query, fetch=True)
    
    return render_template('dashboard.html', stats=stats, role=user_role)

# ==================== CRUD Routes for Cities ====================

@app.route('/cities')
@login_required
def cities():
    """View all cities with AQI and Health Impact data"""
    # Get sorting and filter parameters
    aqi_sort = request.args.get('aqi_sort', 'aqi_desc')  # Default: highest AQI first
    health_sort = request.args.get('health_sort', 'cases_desc')  # Default: most cases first
    health_limit = int(request.args.get('health_limit', 5))  # Default: Top 5
    
    # Cities basic data
    query = """
        SELECT c.*, 
               COUNT(DISTINCT s.station_id) as station_count,
               COUNT(DISTINCT a.aqi_id) as aqi_count
        FROM cities c
        LEFT JOIN stations s ON c.city_id = s.city_id
        LEFT JOIN aqi a ON c.city_id = a.city_id
        GROUP BY c.city_id
        ORDER BY c.city_name
    """
    cities_data = execute_query(query, fetch=True)
    
    # Average AQI by City with sorting
    aqi_order = {
        'aqi_desc': 'avg_aqi DESC',
        'aqi_asc': 'avg_aqi ASC',
        'city_asc': 'c.city_name ASC',
        'city_desc': 'c.city_name DESC'
    }.get(aqi_sort, 'avg_aqi DESC')
    
    aqi_query = f"""
        SELECT c.city_name, 
               ROUND(AVG(a.aqi_value), 2) as avg_aqi,
               COUNT(a.aqi_id) as reading_count
        FROM cities c
        LEFT JOIN aqi a ON c.city_id = a.city_id
        GROUP BY c.city_id, c.city_name
        HAVING avg_aqi IS NOT NULL
        ORDER BY {aqi_order}
        LIMIT 10
    """
    aqi_data = execute_query(aqi_query, fetch=True)
    
    # Health Impact with sorting and configurable limit
    health_order = {
        'cases_desc': 'total_cases DESC',
        'cases_asc': 'total_cases ASC',
        'city_asc': 'c.city_name ASC',
        'city_desc': 'c.city_name DESC',
        'respiratory_desc': 'h.respiratory_cases DESC',
        'lung_cancer_desc': 'h.lung_cancer_cases DESC'
    }.get(health_sort, 'total_cases DESC')
    
    health_query = f"""
        SELECT c.city_name, 
               h.respiratory_cases, 
               h.lung_cancer_cases, 
               h.asthma_cases,
               (h.respiratory_cases + h.lung_cancer_cases + h.asthma_cases) as total_cases
        FROM health_impact h
        JOIN cities c ON h.city_id = c.city_id
        ORDER BY {health_order}
        LIMIT {health_limit}
    """
    health_data = execute_query(health_query, fetch=True)
    

    # DEBUG: Log the AQI data being sent to template
    logger.info(f"AQI Data being sent to template: {len(aqi_data)} cities")
    if aqi_data:
        for city in aqi_data:
            logger.info(f"  {city['city_name']}: {city['avg_aqi']}")
    else:
        logger.warning("No AQI data found!")

    return render_template('cities.html', 
                         cities=cities_data, 
                         aqi_data=aqi_data,
                         health_data=health_data,
                         aqi_sort=aqi_sort,
                         health_sort=health_sort,
                         health_limit=health_limit,
                         role=session.get('role'))

@app.route('/cities/add', methods=['POST'])
@admin_required
def add_city():
    """Add new city with validation"""
    try:
        city_id = request.form.get('city_id')
        city_name = request.form.get('city_name')
        pin_code = request.form.get('pin_code')
        state_name = request.form.get('state_name')

        # Validation 1: Check for required fields
        if not all([city_id, city_name, pin_code, state_name]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('cities'))

        # Validation 2: Check for duplicate city name (case-insensitive)
        check_duplicate = "SELECT city_id, city_name FROM cities WHERE LOWER(city_name) = LOWER(%s)"
        duplicate = execute_query(check_duplicate, (city_name,), fetch=True)
        
        if duplicate:
            flash(f'City "{city_name}" already exists in the database! Please use a different name.', 'warning')
            return redirect(url_for('cities'))

        # Validation 3: Check for duplicate city_id
        check_id = "SELECT city_id FROM cities WHERE city_id = %s"
        id_exists = execute_query(check_id, (city_id,), fetch=True)
        
        if id_exists:
            flash(f'City ID {city_id} is already in use! Please use a different ID.', 'warning')
            return redirect(url_for('cities'))

        # Validation 4: Validate pin code format (should be numeric and 6 digits)
        if not pin_code.isdigit() or len(pin_code) != 6:
            flash('Pin code must be a 6-digit number!', 'danger')
            return redirect(url_for('cities'))

        # Validation 5: Validate state name (alphabetic characters and spaces only)
        if not all(c.isalpha() or c.isspace() for c in state_name):
            flash('State name can only contain letters and spaces!', 'danger')
            return redirect(url_for('cities'))

        # Validation 6: Validate city name length
        if len(city_name.strip()) < 2:
            flash('City name must be at least 2 characters long!', 'danger')
            return redirect(url_for('cities'))

        # Insert city into database
        query = "INSERT INTO cities (city_id, city_name, pin_code, state_name) VALUES (%s, %s, %s, %s)"
        result = execute_query(query, (city_id, city_name.strip(), pin_code, state_name.strip()))

        if result:
            log_audit(session['user_id'], 'INSERT', 'cities', city_id, f'Added city: {city_name}')
            flash(f'✅ City "{city_name}" added successfully!', 'success')
        else:
            flash('Failed to add city. Please try again.', 'danger')

    except Exception as e:
        logger.error(f"Error adding city: {e}")
        flash(f'Error adding city: {str(e)}', 'danger')

    return redirect(url_for('cities'))

@app.route('/cities/update/<int:city_id>', methods=['POST'])
@admin_required
def update_city(city_id):
    """Update city information"""
    city_name = request.form.get('city_name')
    pin_code = request.form.get('pin_code')
    state_name = request.form.get('state_name')
    
    query = "UPDATE cities SET city_name = %s, pin_code = %s, state_name = %s WHERE city_id = %s"
    execute_query(query, (city_name, pin_code, state_name, city_id))
    
    log_audit(session['user_id'], 'UPDATE', 'cities', city_id, f'Updated city: {city_name}')
    flash(f'City {city_name} updated successfully!', 'success')
    return redirect(url_for('cities'))

@app.route('/cities/delete/<int:city_id>', methods=['POST'])
@admin_required
def delete_city(city_id):
    """Delete city"""
    query = "DELETE FROM cities WHERE city_id = %s"
    execute_query(query, (city_id,))
    
    log_audit(session['user_id'], 'DELETE', 'cities', city_id, f'Deleted city ID: {city_id}')
    flash('City deleted successfully!', 'success')
    return redirect(url_for('cities'))

@app.route('/cities/update-aqi/<int:city_id>', methods=['POST'])
@admin_required
def update_city_aqi(city_id):
    """Update AQI values for a city with comprehensive validation"""
    try:
        # Get form data
        aqi_value = request.form.get('aqi_value')
        date = request.form.get('date')
        pm25 = request.form.get('pm25') or None
        pm10 = request.form.get('pm10') or None
        no2 = request.form.get('no2') or None
        so2 = request.form.get('so2') or None
        co = request.form.get('co') or None
        o3 = request.form.get('o3') or None

        # Validation 1: Check required fields
        if not aqi_value or not date:
            flash('❌ AQI value and date are required!', 'danger')
            return redirect(url_for('cities'))

        # Validation 2: Validate AQI value range (0-500)
        try:
            aqi_val = float(aqi_value)
            if aqi_val < 0 or aqi_val > 500:
                flash('❌ AQI value must be between 0 and 500! Please enter a realistic value.', 'danger')
                return redirect(url_for('cities'))
        except ValueError:
            flash('❌ AQI value must be a valid number!', 'danger')
            return redirect(url_for('cities'))

        # Validation 3: Validate pollutant values (realistic ranges)
        pollutant_checks = {
            'PM2.5': (pm25, 0, 1000, 'µg/m³'),  # PM2.5 rarely exceeds 1000 µg/m³
            'PM10': (pm10, 0, 2000, 'µg/m³'),    # PM10 rarely exceeds 2000 µg/m³
            'NO2': (no2, 0, 500, 'µg/m³'),       # NO2 rarely exceeds 500 µg/m³
            'SO2': (so2, 0, 500, 'µg/m³'),       # SO2 rarely exceeds 500 µg/m³
            'CO': (co, 0, 100, 'mg/m³'),         # CO rarely exceeds 100 mg/m³
            'O3': (o3, 0, 500, 'µg/m³')          # O3 rarely exceeds 500 µg/m³
        }

        for pollutant_name, (value, min_val, max_val, unit) in pollutant_checks.items():
            if value:
                try:
                    val = float(value)
                    if val < min_val or val > max_val:
                        flash(f'❌ {pollutant_name} value ({val} {unit}) is unrealistic! '
                              f'Valid range: {min_val}-{max_val} {unit}', 'danger')
                        return redirect(url_for('cities'))
                    # Additional check for negative values
                    if val < 0:
                        flash(f'❌ {pollutant_name} value cannot be negative!', 'danger')
                        return redirect(url_for('cities'))
                except ValueError:
                    flash(f'❌ {pollutant_name} must be a valid number!', 'danger')
                    return redirect(url_for('cities'))

        # Validation 4: Validate date format and range
        from datetime import datetime, timedelta
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            today = datetime.now()
            # Check if date is not more than 1 year in the future
            if date_obj > today + timedelta(days=365):
                flash('❌ Date cannot be more than 1 year in the future!', 'danger')
                return redirect(url_for('cities'))
            # Check if date is not more than 10 years in the past
            if date_obj < today - timedelta(days=3650):
                flash('❌ Date cannot be more than 10 years in the past!', 'danger')
                return redirect(url_for('cities'))
        except ValueError:
            flash('❌ Invalid date format! Please use YYYY-MM-DD format.', 'danger')
            return redirect(url_for('cities'))

        # Validation 5: Check if city exists
        city_check = "SELECT city_name FROM cities WHERE city_id = %s"
        city_result = execute_query(city_check, (city_id,), fetch=True)
        
        if not city_result:
            flash(f'❌ City with ID {city_id} does not exist!', 'danger')
            return redirect(url_for('cities'))
        
        city_name = city_result[0]['city_name']

        # Check if pollutants record exists for this city and date
        check_query = "SELECT * FROM pollutants WHERE city_id = %s AND date = %s"
        existing = execute_query(check_query, (city_id, date), fetch=True)

        if existing:
            # Update existing record
            update_query = """
                UPDATE pollutants
                SET pm25 = %s, pm10 = %s, no2 = %s, so2 = %s, co = %s, o3 = %s
                WHERE city_id = %s AND date = %s
            """
            execute_query(update_query, (pm25, pm10, no2, so2, co, o3, city_id, date))

            # Update AQI value in aqi table
            aqi_update_query = """
                UPDATE aqi
                SET aqi_value = %s
                WHERE city_id = %s AND date = %s
            """
            execute_query(aqi_update_query, (aqi_value, city_id, date))

            log_audit(session['user_id'], 'UPDATE', 'pollutants', city_id,
                     f'Updated AQI for {city_name} on {date}')
            flash(f'✅ AQI values for "{city_name}" on {date} updated successfully! (AQI: {aqi_value})', 'success')
        else:
            # Insert new record into pollutants
            insert_pollutants = """
                INSERT INTO pollutants (city_id, date, pm25, pm10, no2, so2, co, o3)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            execute_query(insert_pollutants, (city_id, date, pm25, pm10, no2, so2, co, o3))

            # Insert into aqi table
            insert_aqi = """
                INSERT INTO aqi (city_id, date, aqi_value)
                VALUES (%s, %s, %s)
            """
            execute_query(insert_aqi, (city_id, date, aqi_value))

            log_audit(session['user_id'], 'INSERT', 'pollutants', city_id,
                     f'Added AQI for {city_name} on {date}')
            flash(f'✅ AQI values for "{city_name}" on {date} added successfully! (AQI: {aqi_value})', 'success')

        return redirect(url_for('cities'))

    except Exception as e:
        logger.error(f"Error updating AQI: {e}")
        flash(f'❌ Error updating AQI values: {str(e)}. Please try again.', 'danger')
        return redirect(url_for('cities'))



@app.route('/stations')
@login_required
def stations():
    """View all monitoring stations"""
    role = session.get('role')
    city_id = session.get('city_id')
    
    if role == 'admin':
        query = """
            SELECT s.*, c.city_name, c.state_name
            FROM stations s
            JOIN cities c ON s.city_id = c.city_id
            ORDER BY c.city_name, s.station_name
        """
        stations_data = execute_query(query, fetch=True)
    else:
        query = """
            SELECT s.*, c.city_name, c.state_name
            FROM stations s
            JOIN cities c ON s.city_id = c.city_id
            WHERE s.city_id = %s
            ORDER BY s.station_name
        """
        stations_data = execute_query(query, (city_id,), fetch=True)
    
    cities_data = execute_query("SELECT * FROM cities ORDER BY city_name", fetch=True)
    return render_template('stations.html', stations=stations_data, cities=cities_data, role=role)

@app.route('/stations/add', methods=['POST'])
@admin_required
def add_station():
    """Add new monitoring station"""
    station_id = request.form.get('station_id')
    city_id = request.form.get('city_id')
    station_name = request.form.get('station_name')
    station_type = request.form.get('station_type')
    managed_by = request.form.get('managed_by')
    
    query = """
        INSERT INTO stations (station_id, city_id, station_name, station_type, managed_by)
        VALUES (%s, %s, %s, %s, %s)
    """
    result = execute_query(query, (station_id, city_id, station_name, station_type, managed_by))
    
    if result:
        log_audit(session['user_id'], 'INSERT', 'stations', station_id, f'Added station: {station_name}')
        flash(f'Station {station_name} added successfully!', 'success')
    else:
        flash('Failed to add station.', 'danger')
    
    return redirect(url_for('stations'))

@app.route('/stations/update/<int:station_id>', methods=['POST'])
@admin_required
def update_station(station_id):
    """Update station information"""
    city_id = request.form.get('city_id')
    station_name = request.form.get('station_name')
    station_type = request.form.get('station_type')
    managed_by = request.form.get('managed_by')
    
    query = """
        UPDATE stations 
        SET city_id = %s, station_name = %s, station_type = %s, managed_by = %s
        WHERE station_id = %s
    """
    execute_query(query, (city_id, station_name, station_type, managed_by, station_id))
    
    log_audit(session['user_id'], 'UPDATE', 'stations', station_id, f'Updated station: {station_name}')
    flash(f'Station {station_name} updated successfully!', 'success')
    return redirect(url_for('stations'))

@app.route('/stations/delete/<int:station_id>', methods=['POST'])
@admin_required
def delete_station(station_id):
    """Delete station"""
    query = "DELETE FROM stations WHERE station_id = %s"
    execute_query(query, (station_id,))
    
    log_audit(session['user_id'], 'DELETE', 'stations', station_id, f'Deleted station ID: {station_id}')
    flash('Station deleted successfully!', 'success')
    return redirect(url_for('stations'))

# ==================== AQI Management Routes ====================

@app.route('/aqi')
@login_required
def aqi_records():
    """View AQI records"""
    role = session.get('role')
    city_id = session.get('city_id')
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    if role == 'admin':
        query = """
            SELECT a.*, c.city_name, s.station_name
            FROM aqi a
            JOIN cities c ON a.city_id = c.city_id
            JOIN stations s ON a.station_id = s.station_id
            ORDER BY a.measurement_date DESC
            LIMIT %s OFFSET %s
        """
        aqi_data = execute_query(query, (per_page, offset), fetch=True)
        count_query = "SELECT COUNT(*) as count FROM aqi"
        total = execute_query(count_query, fetch=True)[0]['count']
    else:
        query = """
            SELECT a.*, c.city_name, s.station_name
            FROM aqi a
            JOIN cities c ON a.city_id = c.city_id
            JOIN stations s ON a.station_id = s.station_id
            WHERE a.city_id = %s
            ORDER BY a.measurement_date DESC
            LIMIT %s OFFSET %s
        """
        aqi_data = execute_query(query, (city_id, per_page, offset), fetch=True)
        count_query = "SELECT COUNT(*) as count FROM aqi WHERE city_id = %s"
        total = execute_query(count_query, (city_id,), fetch=True)[0]['count']
    
    total_pages = (total + per_page - 1) // per_page
    
    cities_data = execute_query("SELECT * FROM cities ORDER BY city_name", fetch=True)
    stations_data = execute_query("SELECT * FROM stations ORDER BY station_name", fetch=True)
    
    return render_template('aqi.html', 
                         aqi_records=aqi_data, 
                         cities=cities_data, 
                         stations=stations_data,
                         role=role,
                         page=page,
                         total_pages=total_pages)

# ==================== User Management (Admin Only) ====================

@app.route('/users')
@admin_required
def users():
    """View all users"""
    query = """
        SELECT u.*, c.city_name
        FROM users u
        LEFT JOIN cities c ON u.city_id = c.city_id
        ORDER BY u.created_at DESC
    """
    users_data = execute_query(query, fetch=True)
    return render_template('users.html', users=users_data)

@app.route('/users/toggle/<int:user_id>', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Activate/Deactivate user"""
    query = "UPDATE users SET is_active = NOT is_active WHERE user_id = %s"
    execute_query(query, (user_id,))
    
    log_audit(session['user_id'], 'UPDATE', 'users', user_id, f'Toggled user status')
    flash('User status updated!', 'success')
    return redirect(url_for('users'))

@app.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete user"""
    if user_id == session['user_id']:
        flash('Cannot delete your own account!', 'danger')
        return redirect(url_for('users'))
    
    query = "DELETE FROM users WHERE user_id = %s"
    execute_query(query, (user_id,))
    
    log_audit(session['user_id'], 'DELETE', 'users', user_id, f'Deleted user')
    flash('User deleted successfully!', 'success')
    return redirect(url_for('users'))

# ==================== Reports and Analytics ====================

@app.route('/reports')
@login_required
def reports():
    """Reports and analytics page"""
    role = session.get('role')
    city_id = session.get('city_id')
    
    # AQI trends
    if role == 'admin':
        aqi_trend_query = """
            SELECT DATE_FORMAT(measurement_date, '%Y-%m') as month, 
                   AVG(aqi_value) as avg_aqi
            FROM aqi
            WHERE measurement_date >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
            GROUP BY month
            ORDER BY month
        """
        aqi_trends = execute_query(aqi_trend_query, fetch=True)
    else:
        aqi_trend_query = """
            SELECT DATE_FORMAT(measurement_date, '%Y-%m') as month, 
                   AVG(aqi_value) as avg_aqi
            FROM aqi
            WHERE city_id = %s AND measurement_date >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
            GROUP BY month
            ORDER BY month
        """
        aqi_trends = execute_query(aqi_trend_query, (city_id,), fetch=True)
    
    # Emission by city
    emission_query = """
        SELECT c.city_name, e.total_co2_emission, e.total_pm25_emission
        FROM emissions_by_city e
        JOIN cities c ON e.city_id = c.city_id
        ORDER BY e.total_co2_emission DESC
        LIMIT 10
    """
    emissions = execute_query(emission_query, fetch=True)
    
    return render_template('reports.html', 
                         aqi_trends=aqi_trends, 
                         emissions=emissions,
                         role=role)

@app.route('/export/csv/<table_name>')
@login_required
def export_csv(table_name):
    """Export table data to CSV"""
    allowed_tables = ['cities', 'stations', 'aqi', 'vehicle_info', 'emissions_by_city']
    
    if table_name not in allowed_tables:
        flash('Invalid table name', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get data
    query = f"SELECT * FROM {table_name} LIMIT 1000"
    data = execute_query(query, fetch=True)
    
    if not data:
        flash('No data to export', 'warning')
        return redirect(url_for('dashboard'))
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    
    # Convert to bytes
    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    output.close()
    
    log_audit(session['user_id'], 'EXPORT', table_name, None, f'Exported {table_name} to CSV')
    
    return send_file(
        mem,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{table_name}_{datetime.now().strftime("%Y%m%d")}.csv'
    )

# ==================== API Endpoints for Charts ====================

@app.route('/api/dashboard_stats')
@login_required
def api_dashboard_stats():
    """API endpoint for dashboard statistics"""
    role = session.get('role')
    city_id = session.get('city_id')
    
    stats = {}
    
    # AQI by city
    if role == 'admin':
        aqi_query = """
            SELECT c.city_name, AVG(a.aqi_value) as avg_aqi
            FROM aqi a
            JOIN cities c ON a.city_id = c.city_id
            GROUP BY c.city_name
            ORDER BY avg_aqi DESC
            LIMIT 10
        """
        stats['aqi_by_city'] = execute_query(aqi_query, fetch=True)
    else:
        aqi_query = """
            SELECT c.city_name, AVG(a.aqi_value) as avg_aqi
            FROM aqi a
            JOIN cities c ON a.city_id = c.city_id
            WHERE a.city_id = %s
            GROUP BY c.city_name
        """
        stats['aqi_by_city'] = execute_query(aqi_query, (city_id,), fetch=True)
    
    # Vehicle distribution
    vehicle_query = """
        SELECT vehicle_id, SUM(vehicle_count) as total_count
        FROM vehicle_info
        GROUP BY vehicle_id
    """
    stats['vehicles'] = execute_query(vehicle_query, fetch=True)
    
    return jsonify(stats)

@app.route('/api/aqi_trends')
@login_required
def api_aqi_trends():
    """API endpoint for AQI trends"""
    role = session.get('role')
    city_id = session.get('city_id')
    
    if role == 'admin':
        query = """
            SELECT DATE_FORMAT(measurement_date, '%Y-%m') as month, 
                   AVG(aqi_value) as avg_aqi
            FROM aqi
            WHERE measurement_date >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
            GROUP BY month
            ORDER BY month
        """
        trends = execute_query(query, fetch=True)
    else:
        query = """
            SELECT DATE_FORMAT(measurement_date, '%Y-%m') as month, 
                   AVG(aqi_value) as avg_aqi
            FROM aqi
            WHERE city_id = %s AND measurement_date >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
            GROUP BY month
            ORDER BY month
        """
        trends = execute_query(query, (city_id,), fetch=True)
    
    return jsonify(trends)

# ==================== Profile Management ====================

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    query = """
        SELECT u.*, c.city_name, c.state_name
        FROM users u
        LEFT JOIN cities c ON u.city_id = c.city_id
        WHERE u.user_id = %s
    """
    user_data = execute_query(query, (session['user_id'],), fetch=True)[0]
    cities = execute_query("SELECT * FROM cities ORDER BY city_name", fetch=True)
    return render_template('profile.html', user=user_data, cities=cities)

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    city_id = request.form.get('city_id')
    
    query = """
        UPDATE users 
        SET full_name = %s, email = %s, city_id = %s
        WHERE user_id = %s
    """
    execute_query(query, (full_name, email, city_id, session['user_id']))
    
    session['full_name'] = full_name
    session['city_id'] = int(city_id) if city_id else None
    
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/profile/change_password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Get current password hash
    query = "SELECT password_hash FROM users WHERE user_id = %s"
    user = execute_query(query, (session['user_id'],), fetch=True)[0]
    
    if not check_password_hash(user['password_hash'], current_password):
        flash('Current password is incorrect!', 'danger')
        return redirect(url_for('profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match!', 'danger')
        return redirect(url_for('profile'))
    
    if len(new_password) < 6:
        flash('Password must be at least 6 characters!', 'danger')
        return redirect(url_for('profile'))
    
    # Update password
    new_hash = generate_password_hash(new_password)
    update_query = "UPDATE users SET password_hash = %s WHERE user_id = %s"
    execute_query(update_query, (new_hash, session['user_id']))
    
    log_audit(session['user_id'], 'UPDATE', 'users', session['user_id'], 'Changed password')
    flash('Password changed successfully!', 'success')
    return redirect(url_for('profile'))

# ==================== Analytics/Environment Route ====================

@app.route('/analytics')
@login_required
def analytics():
    """Analytics page with environmental data"""
    
    # Get selected city from query parameter
    selected_city = request.args.get('city_id', 'all')
    
    # Get all cities for dropdown
    cities_query = "SELECT city_id, city_name FROM cities ORDER BY city_name"
    cities_list = execute_query(cities_query, fetch=True)
    
    # Build WHERE clause for filtering
    city_filter = ""
    city_params = ()
    if selected_city != 'all':
        city_filter = "WHERE c.city_id = %s"
        city_params = (selected_city,)
    
    # Vehicle Distribution with city names
    vehicle_query = f"""
        SELECT vi.*, c.city_name
        FROM vehicle_info vi
        JOIN cities c ON vi.city_id = c.city_id
        {city_filter}
        ORDER BY c.city_name, vi.vehicle_id
    """
    vehicle_data = execute_query(vehicle_query, city_params, fetch=True)
    
    # Emissions by City
    emissions_query = f"""
        SELECT e.*, c.city_name
        FROM emissions_by_city e
        JOIN cities c ON e.city_id = c.city_id
        {city_filter}
        ORDER BY e.total_pollution DESC
    """
    emissions_data = execute_query(emissions_query, city_params, fetch=True)
    
    # Population Data
    population_query = f"""
        SELECT p.*, c.city_name
        FROM population p
        JOIN cities c ON p.city_id = c.city_id
        {city_filter}
        ORDER BY p.total_population DESC
    """
    population_data = execute_query(population_query, city_params, fetch=True)
    
    # Public Transport
    transport_query = f"""
        SELECT pt.*, c.city_name
        FROM public_transport pt
        JOIN cities c ON pt.city_id = c.city_id
        {city_filter}
        ORDER BY c.city_name
    """
    transport_data = execute_query(transport_query, city_params, fetch=True)
    
    # Sources of Energy
    energy_query = f"""
        SELECT se.*, c.city_name
        FROM sources_of_energy se
        JOIN cities c ON se.city_id = c.city_id
        {city_filter}
        ORDER BY c.city_name
    """
    energy_data = execute_query(energy_query, city_params, fetch=True)
    
    # Waste Management
    waste_query = f"""
        SELECT wm.*, c.city_name
        FROM waste_management wm
        JOIN cities c ON wm.city_id = c.city_id
        {city_filter}
        ORDER BY wm.solid_waste DESC
    """
    waste_data = execute_query(waste_query, city_params, fetch=True)
    
    return render_template('analytics.html',
                         vehicle_data=vehicle_data,
                         emissions_data=emissions_data,
                         population_data=population_data,
                         transport_data=transport_data,
                         energy_data=energy_data,
                         waste_data=waste_data,
                         cities_list=cities_list,
                         selected_city=selected_city)

# ==================== API Routes ====================

def get_aqi_health_impact(aqi_value):
    """Get AQI category, health impact message, and color based on AQI value"""
    if aqi_value <= 50:
        return {
            'category': 'Good',
            'message': 'Air quality is satisfactory, and air pollution poses little or no risk.',
            'color': 'success',
            'text_color': 'text-success'
        }
    elif aqi_value <= 100:
        return {
            'category': 'Moderate',
            'message': 'Air quality is acceptable. However, there may be a risk for some people.',
            'color': 'info',
            'text_color': 'text-info'
        }
    elif aqi_value <= 150:
        return {
            'category': 'Unhealthy for Sensitive Groups',
            'message': 'Members of sensitive groups may experience health effects.',
            'color': 'warning',
            'text_color': 'text-warning'
        }
    elif aqi_value <= 200:
        return {
            'category': 'Unhealthy',
            'message': 'Everyone may begin to experience health effects; sensitive groups at greater risk.',
            'color': 'orange',
            'text_color': 'text-warning'
        }
    elif aqi_value <= 300:
        return {
            'category': 'Very Unhealthy',
            'message': 'Health alert: everyone may experience more serious health effects.',
            'color': 'danger',
            'text_color': 'text-danger'
        }
    else:
        return {
            'category': 'Hazardous',
            'message': 'Health warning: everyone may experience serious health effects.',
            'color': 'danger',
            'text_color': 'text-danger'
        }

def fetch_openweather_data(city_name):
    """Fetch live weather and AQI data from OpenWeatherMap API"""
    try:
        # Get coordinates first
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name},IN&limit=1&appid={Config.OPENWEATHER_API_KEY}"
        geo_response = requests.get(geo_url, timeout=5)
        
        if geo_response.status_code != 200:
            return None
        
        geo_data = geo_response.json()
        if not geo_data:
            return None
        
        lat = geo_data[0]['lat']
        lon = geo_data[0]['lon']
        
        # Fetch weather data
        weather_url = f"{Config.OPENWEATHER_BASE_URL}/weather?lat={lat}&lon={lon}&appid={Config.OPENWEATHER_API_KEY}&units=metric"
        weather_response = requests.get(weather_url, timeout=5)
        
        # Fetch air pollution data
        pollution_url = f"{Config.OPENWEATHER_BASE_URL}/air_pollution?lat={lat}&lon={lon}&appid={Config.OPENWEATHER_API_KEY}"
        pollution_response = requests.get(pollution_url, timeout=5)
        
        if weather_response.status_code != 200 or pollution_response.status_code != 200:
            return None
        
        weather_data = weather_response.json()
        pollution_data = pollution_response.json()
        
        # Extract relevant data
        result = {
            'temperature': round(weather_data['main']['temp'], 1),
            'humidity': weather_data['main']['humidity'],
            'wind_speed': round(weather_data['wind']['speed'] * 3.6, 1),  # Convert m/s to km/h
            'precipitation': round(weather_data.get('rain', {}).get('1h', 0), 1),
            'live_aqi': pollution_data['list'][0]['main']['aqi'] * 50,  # Convert to US AQI scale
            'pm25': round(pollution_data['list'][0]['components']['pm2_5'], 2),
            'pm10': round(pollution_data['list'][0]['components']['pm10'], 2),
            'no2': round(pollution_data['list'][0]['components']['no2'], 2),
            'so2': round(pollution_data['list'][0]['components']['so2'], 2),
            'co': round(pollution_data['list'][0]['components']['co'] / 1000, 2),  # Convert to mg/m³
            'o3': round(pollution_data['list'][0]['components']['o3'], 2)
        }
        
        return result
    
    except Exception as e:
        print(f"OpenWeatherMap API Error: {e}")
        return None

@app.route('/api/city-search')
@login_required
def city_search_api():
    """API endpoint to search city and get live data"""
    city_name = request.args.get('city', '')
    
    if not city_name:
        return jsonify({'error': 'City name is required'}), 400
    
    try:
        # Get city info with station names
        city_query = """
            SELECT c.*, 
                   COUNT(DISTINCT s.station_id) as station_count,
                   COUNT(DISTINCT a.aqi_id) as reading_count,
                   GROUP_CONCAT(DISTINCT s.station_name SEPARATOR ', ') as station_names
            FROM cities c
            LEFT JOIN stations s ON c.city_id = s.city_id
            LEFT JOIN aqi a ON c.city_id = a.city_id
            WHERE c.city_name LIKE %s
            GROUP BY c.city_id
            LIMIT 1
        """
        city_data = execute_query(city_query, (f'%{city_name}%',), fetch=True)
        
        if not city_data or len(city_data) == 0:
            return jsonify({'error': f'City "{city_name}" not found'}), 404
        
        city = city_data[0]
        
        # Get latest AQI reading with pollutants
        aqi_query = """
            SELECT a.aqi_value, a.date,
                   p.pm25, p.pm10, p.no2, p.so2, p.co, p.o3
            FROM aqi a
            LEFT JOIN pollutants p ON a.city_id = p.city_id AND a.date = p.date
            WHERE a.city_id = %s
            ORDER BY a.date DESC
            LIMIT 1
        """
        aqi_data = execute_query(aqi_query, (city['city_id'],), fetch=True)
        
        # Get monthly AQI trends for 2024 - simplified query
        trends_query = """
            SELECT 
                MONTH(date) as month,
                ROUND(AVG(aqi_value), 2) as avg_aqi,
                MAX(aqi_value) as max_aqi,
                MIN(aqi_value) as min_aqi
            FROM aqi
            WHERE city_id = %s AND YEAR(date) = 2024
            GROUP BY MONTH(date)
            ORDER BY MONTH(date)
        """
        trends_data = execute_query(trends_query, (city['city_id'],), fetch=True)
        
        # Get dates for max and min AQI values for each month
        max_min_dates = {}
        if trends_data:
            for row in trends_data:
                month = row['month']
                max_aqi = row['max_aqi']
                min_aqi = row['min_aqi']
                
                # Get date of max AQI for this month
                max_date_query = """
                    SELECT DATE(date) as date 
                    FROM aqi 
                    WHERE city_id = %s AND YEAR(date) = 2024 AND MONTH(date) = %s AND aqi_value = %s
                    LIMIT 1
                """
                max_date_result = execute_query(max_date_query, (city['city_id'], month, max_aqi), fetch=True)
                
                # Get date of min AQI for this month
                min_date_query = """
                    SELECT DATE(date) as date 
                    FROM aqi 
                    WHERE city_id = %s AND YEAR(date) = 2024 AND MONTH(date) = %s AND aqi_value = %s
                    LIMIT 1
                """
                min_date_result = execute_query(min_date_query, (city['city_id'], month, min_aqi), fetch=True)
                
                max_min_dates[month] = {
                    'max_date': str(max_date_result[0]['date']) if max_date_result and len(max_date_result) > 0 else '',
                    'min_date': str(min_date_result[0]['date']) if min_date_result and len(min_date_result) > 0 else ''
                }
        
        # Prepare trends data
        trends = {
            'months': [],
            'avg_aqi': [],
            'max_aqi': [],
            'min_aqi': [],
            'max_dates': [],
            'min_dates': []
        }
        
        if trends_data:
            for row in trends_data:
                month = row['month']
                trends['months'].append(month)
                trends['avg_aqi'].append(float(row['avg_aqi']) if row['avg_aqi'] else 0)
                trends['max_aqi'].append(int(row['max_aqi']) if row['max_aqi'] else 0)
                trends['min_aqi'].append(int(row['min_aqi']) if row['min_aqi'] else 0)
                trends['max_dates'].append(max_min_dates.get(month, {}).get('max_date', ''))
                trends['min_dates'].append(max_min_dates.get(month, {}).get('min_date', ''))
        
        # Fetch live data from OpenWeatherMap API
        live_data = fetch_openweather_data(city['city_name'])
        
        # Prepare response - prioritize live API data, fallback to database
        response = {
            'city_name': city['city_name'],
            'state_name': city['state_name'],
            'city_id': city['city_id'],
            'station_names': city['station_names'] if city['station_names'] else 'No stations',
            'station_count': city['station_count'],
            'total_readings': city['reading_count'],
            'trends': trends
        }
        
        # Use live API data if available, otherwise fallback to database
        if live_data:
            response.update({
                'live_aqi': live_data['live_aqi'],
                'pm25': live_data['pm25'],
                'pm10': live_data['pm10'],
                'no2': live_data['no2'],
                'so2': live_data['so2'],
                'co': live_data['co'],
                'o3': live_data['o3'],
                'temperature': live_data['temperature'],
                'humidity': live_data['humidity'],
                'wind_speed': live_data['wind_speed'],
                'precipitation': live_data['precipitation'],
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_source': 'Live API'
            })
        else:
            # Fallback to database data
            import random
            response.update({
                'live_aqi': int(aqi_data[0]['aqi_value']) if aqi_data and len(aqi_data) > 0 else 0,
                'pm25': round(float(aqi_data[0]['pm25']), 2) if aqi_data and len(aqi_data) > 0 and aqi_data[0]['pm25'] else 0,
                'pm10': round(float(aqi_data[0]['pm10']), 2) if aqi_data and len(aqi_data) > 0 and aqi_data[0]['pm10'] else 0,
                'no2': round(float(aqi_data[0]['no2']), 2) if aqi_data and len(aqi_data) > 0 and aqi_data[0]['no2'] else 0,
                'so2': round(float(aqi_data[0]['so2']), 2) if aqi_data and len(aqi_data) > 0 and aqi_data[0]['so2'] else 0,
                'co': round(float(aqi_data[0]['co']), 2) if aqi_data and len(aqi_data) > 0 and aqi_data[0]['co'] else 0,
                'o3': round(float(aqi_data[0]['o3']), 2) if aqi_data and len(aqi_data) > 0 and aqi_data[0]['o3'] else 0,
                'temperature': random.randint(20, 35),
                'humidity': random.randint(50, 80),
                'wind_speed': random.randint(5, 25),
                'precipitation': round(random.uniform(0, 10), 1),
                'last_updated': str(aqi_data[0]['date']) if aqi_data and len(aqi_data) > 0 else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_source': 'Database'
            })
        
        # Add AQI health impact information
        aqi_value = response.get('live_aqi', 0)
        health_impact = get_aqi_health_impact(aqi_value)
        response['health_impact'] = health_impact
        
        # Add debug logging for trends data
        print(f"DEBUG - Trends data for {city['city_name']}: {trends}")
        print(f"DEBUG - Response trends: {response.get('trends', {})}")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in city search API: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch city data', 'details': str(e)}), 500

# ==================== Error Handlers ====================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

# ==================== Main ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
