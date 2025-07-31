#!/bin/bash

echo "📦 Installing Construction AI Platform Dependencies"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Python package
install_python_package() {
    local package=$1
    local description=$2
    
    echo -n "Installing $description... "
    if pip install "$package" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${RED}❌${NC}"
        return 1
    fi
}

echo "🔍 Checking system requirements..."

# Check Python
if command_exists python3; then
    echo -e "${GREEN}✅ Python 3 is installed: $(python3 --version)${NC}"
else
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Check Node.js
if command_exists node; then
    echo -e "${GREEN}✅ Node.js is installed: $(node --version)${NC}"
else
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 16 or higher.${NC}"
    exit 1
fi

# Check npm
if command_exists npm; then
    echo -e "${GREEN}✅ npm is installed: $(npm --version)${NC}"
else
    echo -e "${RED}❌ npm is not installed. Please install npm.${NC}"
    exit 1
fi

echo ""
echo "📦 Installing Backend Dependencies..."

# Navigate to backend directory
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to create virtual environment${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${RED}❌ Failed to activate virtual environment${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install backend dependencies
echo "Installing Python dependencies..."
if pip install -r requirements-minimal.txt; then
    echo -e "${GREEN}✅ Backend dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Failed to install backend dependencies${NC}"
    exit 1
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p uploads
mkdir -p logs
mkdir -p ../ml/models

echo -e "${GREEN}✅ Backend setup complete${NC}"

echo ""
echo "📦 Installing Frontend Dependencies..."

# Navigate to frontend directory
cd ../frontend

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ package.json not found in frontend directory${NC}"
    exit 1
fi

# Install frontend dependencies
echo "Installing Node.js dependencies..."
if npm install; then
    echo -e "${GREEN}✅ Frontend dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Failed to install frontend dependencies${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Frontend setup complete${NC}"

echo ""
echo "🔧 Setting up database..."

# Navigate back to backend
cd ../backend

# Activate virtual environment again
source venv/bin/activate

# Create database tables
echo "Creating database tables..."
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

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database setup complete${NC}"
else
    echo -e "${RED}❌ Database setup failed${NC}"
    exit 1
fi

echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo "✅ All dependencies have been installed successfully"
echo ""
echo "🚀 To start the platform:"
echo "   ./start-platform.sh"
echo ""
echo "🏥 To check platform health:"
echo "   ./health-check.sh"
echo ""
echo "🛑 To stop the platform:"
echo "   ./stop-platform.sh"
echo ""
echo "📚 Documentation:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "" 