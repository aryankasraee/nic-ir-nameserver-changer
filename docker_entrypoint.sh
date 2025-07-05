#!/bin/bash

# Docker entrypoint script for NIC.IR Nameserver Changer

echo "Starting NIC.IR Nameserver Changer..."

# Kill any existing Xvfb processes
pkill Xvfb 2>/dev/null || true
pkill x11vnc 2>/dev/null || true

# Remove any existing X lock files
rm -f /tmp/.X*-lock 2>/dev/null || true

# Start Xvfb for headless browser operation
echo "Starting virtual display..."
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset -dpi 96 &
XVFB_PID=$!
export DISPLAY=:99

# Wait for display to be ready
sleep 3

# Optional: Start VNC server for debugging
if [ "$ENABLE_VNC" = "true" ]; then
    echo "Starting VNC server..."
    x11vnc -display :99 -nopw -listen localhost -xkb -ncache 10 -ncache_cr -forever &
    VNC_PID=$!
fi

# Check if display is working
if ! xdpyinfo -display :99 >/dev/null 2>&1; then
    echo "Error: Display :99 is not working!"
    exit 1
fi

echo "Virtual display is ready"

# Check if domains.csv exists
if [ ! -f "/app/domains.csv" ]; then
    echo "Error: domains.csv not found!"
    echo "Please mount your domains.csv file to /app/domains.csv"
    exit 1
fi

# Check if credentials are provided
if [ -z "$NIC_IR_USERNAME" ] || [ -z "$NIC_IR_PASSWORD" ]; then
    echo "Error: NIC_IR_USERNAME and NIC_IR_PASSWORD environment variables must be set!"
    exit 1
fi

# Cleanup function
cleanup() {
    echo "Cleaning up..."
    [ ! -z "$VNC_PID" ] && kill $VNC_PID 2>/dev/null
    [ ! -z "$XVFB_PID" ] && kill $XVFB_PID 2>/dev/null
}

# Set trap for cleanup
trap cleanup EXIT

# Execute the main command
echo "Running nameserver changer script..."
exec "$@"