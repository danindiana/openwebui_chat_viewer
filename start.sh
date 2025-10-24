#!/bin/bash

# OpenWebUI Chat Viewer - Start Script

echo "=================================="
echo "OpenWebUI Chat Viewer"
echo "=================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found"

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠ Flask is not installed. Installing..."
    pip install flask --break-system-packages
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Flask"
        exit 1
    fi
    echo "✓ Flask installed successfully"
else
    echo "✓ Flask is already installed"
fi

# Check if database file exists
DB_FILE="webui_backup_20250918_102142.db"
if [ ! -f "$DB_FILE" ]; then
    echo ""
    echo "⚠ WARNING: Database file '$DB_FILE' not found!"
    echo ""
    echo "Please do one of the following:"
    echo "  1. Place your database file in this directory as '$DB_FILE'"
    echo "  2. Edit app.py and update the DB_PATH variable to point to your database"
    echo ""
    echo "Press Ctrl+C to exit, or Enter to continue anyway..."
    read
fi

echo ""
echo "=================================="
echo "Starting server..."
echo "=================================="
echo ""
echo "Access the viewer at:"
echo "  Local:   http://localhost:5000"
echo "  Network: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the Flask app
python3 app.py
