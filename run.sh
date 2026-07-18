#!/bin/bash

# ANITA Travel Assistant - Launch Script
# This script sets up the environment and launches the Streamlit app

echo "=========================================="
echo "🚀 ANITA Travel Assistant Launcher"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check for environment configuration
echo ""
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "⚠️  .env file not found. Creating from template..."
        cp .env.example .env
        echo "⚠️  Please edit .env with your API keys"
        echo ""
        read -p "Press Enter to continue or Ctrl+C to edit .env first..."
    fi
fi

# Load environment variables
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

# Display configuration
echo ""
echo "=========================================="
echo "📋 Configuration"
echo "=========================================="
echo "Mode: ${APP_MODE:-demo}"
echo "Debug: ${DEBUG_MODE:-false}"
echo ""

# Launch Streamlit app
echo "=========================================="
echo "🌐 Launching ANITA Travel Assistant"
echo "=========================================="
echo ""
echo "Opening application at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run Streamlit
streamlit run streamlit_ui.py --logger.level=${LOG_LEVEL:-info}
