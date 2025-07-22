#!/bin/bash

echo "🚀 Starting Construction AI Platform..."
echo ""

# Make scripts executable
chmod +x start-backend.sh
chmod +x start-frontend.sh

# Function to check if a port is in use
check_port() {
    lsof -i :$1 > /dev/null 2>&1
}

# Check if ports are already in use
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use. Backend might already be running."
fi

if check_port 3000; then
    echo "⚠️  Port 3000 is already in use. Frontend might already be running."
fi

echo ""
echo "📋 Starting services..."
echo ""

# Start backend in a new terminal window (macOS)
if command -v osascript > /dev/null; then
    echo "🔧 Starting Backend..."
    osascript -e "tell application \"Terminal\" to do script \"cd '$(pwd)' && ./start-backend.sh\""
    
    # Wait a moment for backend to start
    sleep 3
    
    echo "🎨 Starting Frontend..."
    osascript -e "tell application \"Terminal\" to do script \"cd '$(pwd)' && ./start-frontend.sh\""
    
    echo ""
    echo "✅ Construction AI Platform is starting up!"
    echo ""
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo ""
    echo "💡 Both servers are running in separate terminal windows."
    echo "   Close those windows to stop the servers."
    
else
    echo "❌ This script requires macOS Terminal.app"
    echo "   Please run the following commands manually:"
    echo ""
    echo "   Terminal 1: ./start-backend.sh"
    echo "   Terminal 2: ./start-frontend.sh"
fi 