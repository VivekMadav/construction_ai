#!/bin/bash

# Construction AI Platform Setup Script
echo "🚀 Setting up Construction AI Platform..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads
mkdir -p ml/models
mkdir -p ml/data

# Set up environment variables
echo "🔧 Setting up environment variables..."
if [ ! -f .env ]; then
    cat > .env << EOF
# Database
DATABASE_URL=postgresql://qs_user:qs_password@localhost:5432/qs_ai_db
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-change-this-in-production
DEBUG=true

# File uploads
UPLOAD_DIR=uploads
MAX_FILE_SIZE=52428800

# ML Models
MODEL_DIR=ml/models
CONFIDENCE_THRESHOLD=0.7
EOF
    echo "✅ Created .env file"
else
    echo "ℹ️  .env file already exists"
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Created Python virtual environment"
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Python dependencies installed"
cd ..

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
echo "✅ Node.js dependencies installed"
cd ..

# Start Docker services
echo "🐳 Starting Docker services..."
docker-compose up -d postgres redis
echo "✅ Docker services started"

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run database migrations (if using Alembic)
echo "🗄️  Setting up database..."
cd backend
source venv/bin/activate
python -c "
from app.core.database import engine
from app.models.models import Base
Base.metadata.create_all(bind=engine)
print('✅ Database tables created')
"
cd ..

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start the backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "2. Start the frontend: cd frontend && npm run dev"
echo "3. Or use Docker: docker-compose up"
echo ""
echo "Access the application:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo "" 