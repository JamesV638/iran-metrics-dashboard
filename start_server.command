#!/bin/bash
# Iran Dashboard Server - runs in background
# Add this to Login Items: System Settings > General > Login Items

cd ~/Documents/iran-metrics-dashboard

# Kill any existing server
lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null

# Start server in background
nohup python3 -m http.server 8000 > logs/server.log 2>&1 &

echo "Server started on http://localhost:8000"
sleep 2
