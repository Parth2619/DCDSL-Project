"""
Database Connection Pool Module
Provides efficient database connection management with pooling and error handling
"""

import mysql.connector
from mysql.connector import pooling, Error
from config import Config
import logging
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create connection pool
try:
    db_config = Config.get_db_config()
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="dcds_pool",
        pool_size=10,  # Maintain 10 connections in the pool
        pool_reset_session=True,
        **db_config
    )
    logger.info("✅ Database connection pool created successfully")
except Error as e:
    logger.error(f"❌ Error creating connection pool: {e}")
    connection_pool = None


@contextmanager
def get_db_connection():
    """
    Context manager for database connections with automatic cleanup
    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM table")
    """
    connection = None
    try:
        if connection_pool:
            connection = connection_pool.get_connection()
            yield connection
        else:
            # Fallback to direct connection if pool failed
            connection = mysql.connector.connect(**Config.get_db_config())
            yield connection
    except Error as e:
        logger.error(f"❌ Database connection error: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection and connection.is_connected():
            connection.close()


def execute_query(query, params=None, fetch=False, fetchone=False):
    """
    Execute SQL query with improved error handling and connection management
    
    Args:
        query: SQL query string
        params: Tuple of parameters for parameterized query
        fetch: Return all results if True
        fetchone: Return single result if True
        
    Returns:
        Query results or lastrowid for INSERT operations
    """
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
            elif fetchone:
                result = cursor.fetchone()
            else:
                connection.commit()
                result = cursor.lastrowid
            
            cursor.close()
            return result
            
    except Error as e:
        logger.error(f"❌ Query execution error: {e}")
        logger.error(f"Query: {query}")
        logger.error(f"Params: {params}")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return None


def execute_transaction(queries_with_params):
    """
    Execute multiple queries in a single transaction
    Ensures all queries succeed or all fail (atomicity)
    
    Args:
        queries_with_params: List of tuples [(query1, params1), (query2, params2), ...]
        
    Returns:
        True if transaction successful, False otherwise
    """
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            
            # Execute all queries
            for query, params in queries_with_params:
                cursor.execute(query, params or ())
            
            # Commit transaction if all queries succeed
            connection.commit()
            cursor.close()
            logger.info("✅ Transaction committed successfully")
            return True
            
    except Error as e:
        logger.error(f"❌ Transaction failed, rolling back: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected transaction error: {e}")
        return False


def check_db_health():
    """
    Check database connection health
    Returns dict with status information
    """
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            
            return {
                "status": "healthy",
                "pool_size": connection_pool.pool_size if connection_pool else 0,
                "message": "Database connection is working"
            }
    except Exception as e:
        logger.error(f"❌ Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": str(e)
        }


def validate_data(data, rules):
    """
    Validate data before database operations
    
    Args:
        data: Dictionary of data to validate
        rules: Dictionary of validation rules
        
    Returns:
        Tuple (is_valid, error_message)
    """
    for field, rule in rules.items():
        if field not in data:
            return False, f"Missing required field: {field}"
        
        value = data[field]
        
        # Check required
        if rule.get('required') and not value:
            return False, f"{field} is required"
        
        # Check type
        if 'type' in rule and value is not None:
            expected_type = rule['type']
            if not isinstance(value, expected_type):
                return False, f"{field} must be of type {expected_type.__name__}"
        
        # Check min/max for numbers
        if isinstance(value, (int, float)):
            if 'min' in rule and value < rule['min']:
                return False, f"{field} must be at least {rule['min']}"
            if 'max' in rule and value > rule['max']:
                return False, f"{field} must be at most {rule['max']}"
        
        # Check length for strings
        if isinstance(value, str):
            if 'min_length' in rule and len(value) < rule['min_length']:
                return False, f"{field} must be at least {rule['min_length']} characters"
            if 'max_length' in rule and len(value) > rule['max_length']:
                return False, f"{field} must be at most {rule['max_length']} characters"
    
    return True, None
