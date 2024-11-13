#!/bin/bash

# Function to clean up background processes
cleanup() {
    echo "Terminating background processes..."
    pkill -P $$
    exit 0
}

# Only allow specific ports
ALLOWED_PORTS="5000"
LOCAL_PORT=\${1:-5000}

if [[ ! \$ALLOWED_PORTS =~ \$LOCAL_PORT ]]; then
    echo "Error: Port \$LOCAL_PORT is not in allowed list"
    exit 1
fi

# Trap the EXIT signal to run the cleanup function
trap cleanup EXIT

python app.py &
# ssh -R 80:localhost:5000 serveo.net

ssh -o ExitOnForwardFailure=yes \
    -o StrictHostKeyChecking=yes \
    -o UserKnownHostsFile=/home/tunnel_user/.ssh/known_hosts \
    -R "80:localhost:\$LOCAL_PORT" \
    serveo.net