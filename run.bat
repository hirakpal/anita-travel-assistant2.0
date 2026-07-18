@echo off
REM ANITA Travel Assistant - Windows Launch Script

echo ==========================================
echo 🚀 ANITA Travel Assistant Launcher
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✓ Python found: %PYTHON_VERSION%

REM Check if virtual environment exists
if not exist "venv" (
    echo.
    echo 📦 Creating virtual environment...
    python -m venv venv
    if %errorlevel% equ 0 (
        echo ✓ Virtual environment created
    ) else (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo.
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo.
echo 📥 Installing dependencies...
pip install -q -r requirements.txt
if %errorlevel% equ 0 (
    echo ✓ Dependencies installed
) else (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Check for environment configuration
echo.
if not exist ".env" (
    if exist ".env.example" (
        echo ⚠️  .env file not found. Creating from template...
        copy .env.example .env
        echo ⚠️  Please edit .env with your API keys
        echo.
        set /p CONTINUE="Press Enter to continue or Ctrl+C to edit .env first..."
    )
)

REM Display configuration
echo.
echo ==========================================
echo 📋 Configuration
echo ==========================================
if defined APP_MODE (echo Mode: %APP_MODE%) else (echo Mode: demo)
if defined DEBUG_MODE (echo Debug: %DEBUG_MODE%) else (echo Debug: false)
echo.

REM Launch Streamlit app
echo ==========================================
echo 🌐 Launching ANITA Travel Assistant
echo ==========================================
echo.
echo Opening application at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run Streamlit
if defined LOG_LEVEL (
    streamlit run streamlit_ui.py --logger.level=%LOG_LEVEL%
) else (
    streamlit run streamlit_ui.py --logger.level=info
)

pause
