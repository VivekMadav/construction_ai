#!/bin/bash

echo "🚀 Starting Construction AI Backend..."

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if we're in the virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Install dependencies if needed
echo "📥 Checking dependencies..."
if [ ! -f "venv/lib/python*/site-packages/fastapi" ] || [ ! -f "venv/lib/python*/site-packages/uvicorn" ]; then
    echo "📦 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements-minimal.txt
    
    # Check if installation was successful
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed successfully"
else
    echo "✅ Dependencies already installed"
fi

# Create uploads directory if it doesn't exist
echo "📁 Setting up directories..."
mkdir -p uploads
mkdir -p logs

# Create database tables with error handling
echo "🗄️ Setting up database..."
python -c "
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))

try:
    from app.core.database import engine
    from app.models.models import Base
    Base.metadata.create_all(bind=engine)
    print('✅ Database tables created successfully')
except Exception as e:
    print(f'❌ Database setup failed: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Database setup failed"
    exit 1
fi

# Check if ports are available
echo "🔍 Checking port availability..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8000 is already in use. Stopping existing process..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "   No process to kill"
    sleep 2
fi

# Start the server with improved logging
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "📊 Health Check: http://localhost:8000/health"
echo "Press Ctrl+C to stop the server"
echo ""

# Start with improved error handling
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level info 