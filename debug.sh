#!/bin/bash

echo "Starting NIC.IR Nameserver Changer in DEBUG mode..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found!"
    exit 1
fi

# Enable VNC in environment
export ENABLE_VNC=true

# Start services including VNC
docker compose --profile debug up --build

echo "Debug session started!"
echo "Access noVNC at: http://localhost:6080"
echo "VNC password: nicir123"
