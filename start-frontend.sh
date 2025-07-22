#!/bin/bash

echo "🎨 Starting Construction AI Frontend..."

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Start the development server
echo "🌐 Starting Next.js server on http://localhost:3000"
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev 