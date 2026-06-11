#!/bin/bash
# Setup daily automation for Iran Metrics Dashboard
# This script creates a macOS LaunchAgent to run data fetching every hour

DASHBOARD_DIR="$HOME/Desktop/iran-metrics-dashboard"
PLIST_PATH="$HOME/Library/LaunchAgents/com.iranmetrics.datafetch.plist"

echo "=================================="
echo "Iran Metrics Dashboard - Automation Setup"
echo "=================================="
echo ""

# Create the LaunchAgents directory if it doesn't exist
mkdir -p "$HOME/Library/LaunchAgents"

# Create the plist file
cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.iranmetrics.datafetch</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>${DASHBOARD_DIR}/fetch_data.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>${DASHBOARD_DIR}</string>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${DASHBOARD_DIR}/logs/fetch.log</string>
    <key>StandardErrorPath</key>
    <string>${DASHBOARD_DIR}/logs/fetch_error.log</string>
</dict>
</plist>
EOF

# Create logs directory
mkdir -p "$DASHBOARD_DIR/logs"

# Load the LaunchAgent
launchctl unload "$PLIST_PATH" 2>/dev/null
launchctl load "$PLIST_PATH"

echo "Automation setup complete!"
echo ""
echo "Configuration:"
echo "  - Data fetches every hour automatically"
echo "  - Logs saved to: $DASHBOARD_DIR/logs/"
echo ""
echo "To stop automation:"
echo "  launchctl unload $PLIST_PATH"
echo ""
echo "To manually trigger a fetch:"
echo "  python3 $DASHBOARD_DIR/fetch_data.py"
echo ""

read -p "Press Enter to close..."
