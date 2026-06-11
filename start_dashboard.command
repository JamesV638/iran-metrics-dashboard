#!/bin/bash
# Iran Metrics Dashboard - Quick Start
# Double-click this file to start the dashboard

cd "$(dirname "$0")"

echo "=================================="
echo "Iran Metrics Dashboard"
echo "=================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed."
    echo "Please install Python 3 from https://python.org"
    read -p "Press Enter to exit..."
    exit 1
fi

# Install dependencies if needed
echo "Checking dependencies..."
pip3 install yfinance requests --quiet 2>/dev/null

# Fetch latest data
echo "Fetching latest market data..."
python3 fetch_data.py

echo ""
echo "Starting local server..."
echo "Dashboard will open in your browser at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Open browser after a short delay
(sleep 2 && open "http://localhost:8000") &

# Start simple HTTP server
python3 -m http.server 8000
