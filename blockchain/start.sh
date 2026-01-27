#!/bin/sh
set -e

echo "=========================================="
echo "Starting Hardhat Blockchain Node"
echo "=========================================="

# Start Hardhat node in background
echo "Starting Hardhat node..."
npx hardhat node &
NODE_PID=$!

# Wait for node to be ready (retry up to 30 seconds)
echo "Waiting for node to start..."
COUNTER=0
MAX_TRIES=30
while [ $COUNTER -lt $MAX_TRIES ]; do
    if nc -z localhost 8545 2>/dev/null; then
        echo "Node is running on port 8545"
        break
    fi
    echo "Waiting... ($COUNTER/$MAX_TRIES)"
    sleep 1
    COUNTER=$((COUNTER + 1))
done

if [ $COUNTER -eq $MAX_TRIES ]; then
    echo "Error: Hardhat node failed to start within $MAX_TRIES seconds"
    exit 1
fi

# Deploy contract
echo "Deploying smart contract..."
npx hardhat run scripts/deploy.js --network localhost

echo "=========================================="
echo "Blockchain ready! Contract deployed."
echo "=========================================="

# Keep container running
wait $NODE_PID
