-- Users Table for Authentication and Role-Based Access Control
-- Add this to your dcds_project database

USE dcds_project;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    city_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

-- Create audit log table for tracking changes
CREATE TABLE IF NOT EXISTS audit_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,  -- INSERT, UPDATE, DELETE
    table_name VARCHAR(50) NOT NULL,
    record_id VARCHAR(50),
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Insert default admin user (password: admin123)
-- Password hash is for 'admin123' using werkzeug security
-- Note: We'll create proper password hashes using the application
INSERT INTO users (username, email, password_hash, full_name, role, city_id) VALUES
('admin', 'admin@dcds.com', 'pbkdf2:sha256:600000$placeholder$hash', 'System Administrator', 'admin', NULL),
('user1', 'user1@dcds.com', 'pbkdf2:sha256:600000$placeholder$hash', 'Demo User', 'user', NULL);

-- Note: After running this script, you should reset these passwords using the application
-- Default credentials:
-- Admin: username=admin, password=admin123
-- User: username=user1, password=user123

-- Grant necessary privileges (run as root)
-- GRANT ALL PRIVILEGES ON dcds_project.* TO 'your_username'@'localhost';
-- FLUSH PRIVILEGES;
