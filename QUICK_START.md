# Construction AI Platform - Quick Start Guide

## 🚀 Get Started in 5 Minutes

This guide will help you get the Construction AI Platform up and running for your demo or development.

## Prerequisites

Before you begin, make sure you have the following installed:

- **Docker & Docker Compose** - [Install Docker](https://docs.docker.com/get-docker/)
- **Node.js 18+** - [Install Node.js](https://nodejs.org/)
- **Python 3.11+** - [Install Python](https://www.python.org/downloads/)

## Option 1: Quick Setup (Recommended)

1. **Clone and Setup**
   ```bash
   # Run the setup script
   ./setup.sh
   ```

2. **Start the Application**
   ```bash
   # Start all services with Docker
   docker-compose up
   ```

3. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Option 2: Manual Setup

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### 3. Database Setup

```bash
# Start PostgreSQL and Redis with Docker
docker-compose up -d postgres redis

# Wait for database to be ready, then create tables
cd backend
source venv/bin/activate
python -c "
from app.core.database import engine
from app.models.models import Base
Base.metadata.create_all(bind=engine)
print('Database tables created successfully')
"
```

## 🎯 Demo Walkthrough

### 1. Create a New Project
1. Open http://localhost:3000
2. Click "New Project" button
3. Fill in project details:
   - Name: "Demo Office Building"
   - Description: "3-story commercial office building"
   - Client: "Demo Client Ltd"
   - Type: "Commercial"
   - Location: "London, UK"
4. Click "Create Project"

### 2. Upload a Drawing
1. In your project, click "Upload Drawing"
2. Select a PDF construction drawing
3. Wait for processing to complete
4. View detected elements

### 3. Review Results
1. Check the detected elements (walls, doors, windows, columns)
2. View confidence scores for each detection
3. See the cost breakdown
4. Generate a cost report

## 📁 Project Structure

```
construction-ai-platform/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Next.js pages
│   │   └── styles/         # CSS styles
│   └── package.json        # Node dependencies
├── ml/                     # Machine learning models
├── docs/                   # Documentation
├── docker-compose.yml      # Docker setup
└── setup.sh               # Setup script
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
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
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📊 API Endpoints

### Projects
- `GET /api/v1/projects` - List all projects
- `POST /api/v1/projects` - Create new project
- `GET /api/v1/projects/{id}` - Get project details
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Drawings
- `POST /api/v1/drawings/upload/{project_id}` - Upload drawing
- `GET /api/v1/drawings/project/{project_id}` - Get project drawings
- `GET /api/v1/drawings/{id}` - Get drawing details
- `DELETE /api/v1/drawings/{id}` - Delete drawing

### Analysis
- `GET /api/v1/analysis/project/{project_id}/costs` - Calculate project costs
- `GET /api/v1/analysis/materials/suggestions/{element_type}` - Get material suggestions

### Reports
- `POST /api/v1/reports/project/{project_id}/generate` - Generate cost report
- `GET /api/v1/reports/project/{project_id}` - Get project reports

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using the port
   lsof -i :8000
   lsof -i :3000
   
   # Kill the process or change ports
   ```

2. **Database connection failed**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps
   
   # Restart database
   docker-compose restart postgres
   ```

3. **Dependencies not found**
   ```bash
   # Reinstall Python dependencies
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Reinstall Node dependencies
   cd frontend
   npm install
   ```

4. **Permission denied**
   ```bash
   # Make setup script executable
   chmod +x setup.sh
   ```

### Logs

View logs for debugging:

```bash
# Backend logs
docker-compose logs backend

# Frontend logs
docker-compose logs frontend

# Database logs
docker-compose logs postgres
```

## 📞 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Review the logs for error messages
3. Ensure all prerequisites are installed
4. Try the manual setup if Docker isn't working

## 🚀 Next Steps

After getting the platform running:

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Test with sample data**: Upload a construction drawing
3. **Review the code**: Understand the implementation
4. **Customize**: Modify for your specific needs
5. **Deploy**: Prepare for production use

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Docker Documentation](https://docs.docker.com/) 