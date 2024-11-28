#!/bin/bash

# Function to clean up background processes and reset ufw rules
cleanup() {
    echo "Terminating background processes..."
    pkill -P $$  # Kill all background processes started by this script

    # Remove firewall rule for the specific port
    echo "Reverting ufw rules..."
    sudo ufw delete allow $LOCAL_PORT > /dev/null 2>&1

    # Ensure SSH (port 8822) remains open
    sudo ufw allow 8822 > /dev/null 2>&1

    exit 0
}

# Trap the EXIT signal to run the cleanup function
trap cleanup EXIT

# Define allowed ports
ALLOWED_PORTS="5000"
LOCAL_PORT=${1:-5000}

# Check if the provided port is allowed
if [[ ! $ALLOWED_PORTS =~ (^|[[:space:]])$LOCAL_PORT($|[[:space:]]) ]]; then
    echo "Error: Port $LOCAL_PORT is not in the allowed list."
    exit 1
fi

# Add ufw rule for the port
echo "Configuring firewall to allow traffic on port $LOCAL_PORT..."
sudo ufw allow $LOCAL_PORT > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo "Failed to configure ufw. Make sure it's installed and configured correctly."
    exit 1
fi

# Ensure SSH (port 8822) remains open
echo "Ensuring SSH access on port 8822 is allowed..."
sudo ufw allow 8822 > /dev/null 2>&1

# Ensure ufw is enabled
if ! sudo ufw status | grep -q "Status: active"; then
    echo "Enabling ufw..."
    sudo ufw --force enable > /dev/null 2>&1
    if [[ $? -ne 0 ]]; then
        echo "Failed to enable ufw. Exiting..."
        exit 1
    fi
fi

# Start the Flask app in the background
echo "Starting Flask app on port $LOCAL_PORT..."
python app.py &

# Start the Serveo tunnel
echo "Starting Serveo tunnel for port $LOCAL_PORT..."
ssh -R lindalnlightshow:80:127.0.0.1:$LOCAL_PORT serveo.net