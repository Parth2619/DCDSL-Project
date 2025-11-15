"""
Configuration file for MySQL Database Connection
Database: dcds_project (Air Quality and Environmental Data System)
"""

import os
from datetime import timedelta

class Config:
    """Application configuration class"""
    
    # Flask Secret Key (Change this in production!)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dcds-project-secret-key-2025'
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_TYPE = 'filesystem'
    
    # MySQL Database Configuration
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',           # Change to your MySQL username
        'password': '2630',           # Change to your MySQL password
        'database': 'dcds_project',
        'charset': 'utf8mb4',
        'autocommit': True
    }
    
    # Application Settings
    RECORDS_PER_PAGE = 10
    
    # OpenWeatherMap API Configuration
    # Get your free API key from: https://openweathermap.org/api
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY') or 'b8c0fc7b75cbbbaab9bf63fe4e49e7fd'  # Free demo key - replace with your own
    OPENWEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    
    # File Upload Configuration
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'pdf'}
    
    # User Roles
    ADMIN_ROLE = 'admin'
    USER_ROLE = 'user'
    
    @staticmethod
    def get_db_config():
        """Returns database configuration dictionary"""
        return Config.DB_CONFIG
