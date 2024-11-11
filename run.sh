#!/bin/bash

# Function to clean up background processes
cleanup() {
    echo "Terminating background processes..."
    pkill -P $$
    exit 0
}

# Trap the EXIT signal to run the cleanup function
trap cleanup EXIT

python app.py &
ssh -R 80:localhost:5000 serveo.net