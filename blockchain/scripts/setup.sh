#!/bin/bash

# Blockchain Setup Script for Document Verification System
# This script sets up and starts the local Hardhat blockchain node

echo "🚀 Document Verification System - Blockchain Setup"
echo "=================================================="
echo ""

# Navigate to blockchain directory
cd "$(dirname "$0")/.."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo ""

# Install dependencies
echo "📦 Installing blockchain dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"
echo ""

# Compile smart contracts
echo "🔨 Compiling smart contracts..."
npm run compile

if [ $? -ne 0 ]; then
    echo "❌ Failed to compile contracts"
    exit 1
fi

echo "✅ Smart contracts compiled successfully"
echo ""

# Start Hardhat node in background
echo "⛓️  Starting local Hardhat blockchain..."
npm run node &
HARDHAT_PID=$!

echo "✅ Blockchain node started (PID: $HARDHAT_PID)"
echo "🌐 RPC URL: http://localhost:8545"
echo ""

# Wait for node to be ready
echo "⏳ Waiting for blockchain node to be ready..."
sleep 5

# Deploy contracts
echo "🚀 Deploying smart contracts..."
npm run deploy

if [ $? -ne 0 ]; then
    echo "❌ Failed to deploy contracts"
    kill $HARDHAT_PID
    exit 1
fi

echo ""
echo "🎉 Blockchain setup completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "  1. Blockchain is running at http://localhost:8545"
echo "  2. Contract is deployed and ready to use"
echo "  3. Start your backend: cd backend && python app/main.py"
echo "  4. Start your frontend: cd frontend && npm start"
echo ""
echo "⚠️  To stop the blockchain, run: kill $HARDHAT_PID"
echo ""

# Keep script running
wait $HARDHAT_PID
