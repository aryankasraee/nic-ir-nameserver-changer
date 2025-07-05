#!/bin/bash

echo "Starting NIC.IR Nameserver Changer..."

# Check if .env file exists and credentials are set
if [ ! -f ".env" ]; then
    echo "Error: .env file not found!"
    exit 1
fi

# Source .env file
source .env

if [ "$NIC_IR_USERNAME" = "your_username_here" ] || [ "$NIC_IR_PASSWORD" = "your_password_here" ]; then
    echo "Error: Please set your NIC.IR credentials in .env file!"
    exit 1
fi

# Build and run the container
docker compose up --build

echo "Script completed! Check results directory for output."
