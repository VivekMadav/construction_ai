#!/bin/bash

echo "🏥 Construction AI Platform Health Check"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${GREEN}✅ Port $1 is in use${NC}"
        return 0
    else
        echo -e "${RED}❌ Port $1 is not in use${NC}"
        return 1
    fi
}

# Function to check if a service is responding
check_service() {
    local url=$1
    local name=$2
    if curl -s --max-time 5 "$url" > /dev/null; then
        echo -e "${GREEN}✅ $name is responding${NC}"
        return 0
    else
        echo -e "${RED}❌ $name is not responding${NC}"
        return 1
    fi
}

# Check if we're in the right directory
if [ ! -f "start-platform.sh" ]; then
    echo -e "${RED}❌ Please run this script from the project root directory${NC}"
    exit 1
fi

echo "🔍 Checking system requirements..."

# Check Python
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✅ Python 3 is installed: $(python3 --version)${NC}"
else
    echo -e "${RED}❌ Python 3 is not installed${NC}"
fi

# Check Node.js
if command -v node &> /dev/null; then
    echo -e "${GREEN}✅ Node.js is installed: $(node --version)${NC}"
else
    echo -e "${RED}❌ Node.js is not installed${NC}"
fi

# Check npm
if command -v npm &> /dev/null; then
    echo -e "${GREEN}✅ npm is installed: $(npm --version)${NC}"
else
    echo -e "${RED}❌ npm is not installed${NC}"
fi

echo ""
echo "🔍 Checking service status..."

# Check backend port
backend_running=false
if check_port 8000; then
    backend_running=true
    # Check if backend is responding
    if check_service "http://localhost:8000/health" "Backend API"; then
        echo -e "${GREEN}✅ Backend is healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend is running but not responding to health check${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Backend is not running${NC}"
fi

# Check frontend port
frontend_running=false
if check_port 3000; then
    frontend_running=true
    # Check if frontend is responding
    if check_service "http://localhost:3000" "Frontend"; then
        echo -e "${GREEN}✅ Frontend is healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend is running but not responding${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Frontend is not running${NC}"
fi

echo ""
echo "🔍 Checking project structure..."

# Check backend directory
if [ -d "backend" ]; then
    echo -e "${GREEN}✅ Backend directory exists${NC}"
    
    # Check virtual environment
    if [ -d "backend/venv" ]; then
        echo -e "${GREEN}✅ Backend virtual environment exists${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend virtual environment not found${NC}"
    fi
    
    # Check requirements file
    if [ -f "backend/requirements-minimal.txt" ]; then
        echo -e "${GREEN}✅ Backend requirements file exists${NC}"
    else
        echo -e "${RED}❌ Backend requirements file not found${NC}"
    fi
else
    echo -e "${RED}❌ Backend directory not found${NC}"
fi

# Check frontend directory
if [ -d "frontend" ]; then
    echo -e "${GREEN}✅ Frontend directory exists${NC}"
    
    # Check package.json
    if [ -f "frontend/package.json" ]; then
        echo -e "${GREEN}✅ Frontend package.json exists${NC}"
    else
        echo -e "${RED}❌ Frontend package.json not found${NC}"
    fi
    
    # Check node_modules
    if [ -d "frontend/node_modules" ]; then
        echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend dependencies not installed${NC}"
    fi
else
    echo -e "${RED}❌ Frontend directory not found${NC}"
fi

# Check uploads directory
if [ -d "uploads" ]; then
    echo -e "${GREEN}✅ Uploads directory exists${NC}"
else
    echo -e "${YELLOW}⚠️  Uploads directory not found${NC}"
fi

echo ""
echo "📊 Summary:"

if [ "$backend_running" = true ] && [ "$frontend_running" = true ]; then
    echo -e "${GREEN}✅ Platform is running${NC}"
    echo ""
    echo "🌐 Access URLs:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo "   Health Check: http://localhost:8000/health"
elif [ "$backend_running" = true ]; then
    echo -e "${YELLOW}⚠️  Backend is running but frontend is not${NC}"
    echo "   Run: ./start-frontend.sh"
elif [ "$frontend_running" = true ]; then
    echo -e "${YELLOW}⚠️  Frontend is running but backend is not${NC}"
    echo "   Run: ./start-backend.sh"
else
    echo -e "${RED}❌ Platform is not running${NC}"
    echo "   Run: ./start-platform.sh"
fi

echo ""
echo "🔧 Troubleshooting:"
echo "   - If services are not running, try: ./start-platform.sh"
echo "   - If dependencies are missing, try: ./start-backend.sh && ./start-frontend.sh"
echo "   - If ports are in use, try: ./stop-platform.sh"
echo "" 