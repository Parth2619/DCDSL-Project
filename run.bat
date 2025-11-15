@echo off
REM ===================================
REM DCDS Project - Windows Launcher
REM ===================================

echo.
echo ========================================
echo   DCDS Project - Air Quality System
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    echo [SUCCESS] Virtual environment created!
    echo.
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
echo [INFO] Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
    echo [SUCCESS] Dependencies installed!
    echo.
) else (
    echo [SUCCESS] Dependencies already installed!
    echo.
)

REM Display information
echo ========================================
echo   Starting Flask Application
echo ========================================
echo.
echo [INFO] Server will start on: http://localhost:5000
echo [INFO] Press CTRL+C to stop the server
echo.
echo ========================================
echo   Default Login Credentials:
echo ========================================
echo   Admin:
echo     Username: admin
echo     Password: admin123
echo.
echo   User:
echo     Username: user1
echo     Password: user123
echo ========================================
echo.

REM Run the Flask application
python app.py

REM If the app exits, pause so user can see any errors
pause
