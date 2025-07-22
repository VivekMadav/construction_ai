#!/bin/bash

echo "🛑 Stopping Construction AI Platform..."

# Kill processes on ports 8000 and 3000
echo "🔧 Stopping Backend (port 8000)..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "   No backend process found"

echo "🎨 Stopping Frontend (port 3000)..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || echo "   No frontend process found"

echo ""
echo "✅ All services stopped!"
echo ""
echo "💡 To start the platform again, run: ./construction-ai start" 