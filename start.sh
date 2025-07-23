#!/bin/bash
# Laura Memory Service - Start Script

set -e

echo "🚀 Starting Laura Memory Service..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it with your configuration."
    exit 1
fi

# Source environment variables
source .env

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if running in Docker or locally
if [ "$DOCKER_ENV" = "true" ]; then
    echo "🐳 Running in Docker mode"
    python server.py
else
    echo "💻 Running in local mode"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    
    # Start server
    echo "✅ Starting Laura Memory Service on port 5001..."
    python server.py
fi