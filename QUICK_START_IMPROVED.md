# Construction AI Platform - Quick Start Guide (Improved)

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- npm

### 1. Install Dependencies
```bash
./install-dependencies.sh
```

This script will:
- ✅ Check system requirements
- ✅ Create Python virtual environment
- ✅ Install all Python dependencies
- ✅ Install all Node.js dependencies
- ✅ Set up the database
- ✅ Create necessary directories

### 2. Start the Platform
```bash
./start-platform.sh
```

This will start both backend and frontend services in separate terminal windows.

### 3. Access the Platform
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🏥 Health Check

Run the health check to verify everything is working:
```bash
./health-check.sh
```

This will check:
- ✅ System requirements (Python, Node.js, npm)
- ✅ Service status (Backend, Frontend)
- ✅ Project structure
- ✅ Dependencies installation

## 🛠️ Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
./stop-platform.sh
./start-platform.sh
```

#### 2. Dependencies Missing
```bash
./install-dependencies.sh
```

#### 3. Database Issues
```bash
cd backend
source venv/bin/activate
python -c "from app.core.database import engine; from app.models.models import Base; Base.metadata.create_all(bind=engine)"
```

#### 4. CORS Issues
The platform now includes comprehensive CORS configuration that should work with all common development setups.

#### 5. ML Dependencies Missing
The platform now gracefully handles missing ML dependencies and will work with basic functionality even if advanced ML features are not available.

## 🔧 Manual Setup (if needed)

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-minimal.txt
python -c "from app.core.database import engine; from app.models.models import Base; Base.metadata.create_all(bind=engine)"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 📊 Platform Features

### ✅ Fixed Issues
- **CORS Issues**: Comprehensive CORS configuration with fallback to allow all origins
- **Platform Stability**: Enhanced error handling, logging, and graceful degradation
- **Batch Analysis**: Improved batch processing with progress tracking and error handling
- **Enhanced Features**: All ML features now work with graceful fallbacks

### 🆕 New Features
- **Health Check Script**: Comprehensive platform monitoring
- **Dependency Installation Script**: Automated setup process
- **Improved Error Handling**: Better error messages and recovery
- **Enhanced Logging**: Detailed logging for debugging
- **Graceful Degradation**: Platform works even with missing ML dependencies

### 🔄 Improved Workflows
- **Batch Upload**: Better error handling and progress tracking
- **Cross-Drawing Analysis**: More robust reference detection
- **Cost Estimation**: Enhanced accuracy with fallback methods
- **Carbon Analysis**: Improved calculations with better error handling

## 📝 API Endpoints

### Core Endpoints
- `GET /health` - Platform health check
- `GET /` - Root endpoint with platform info

### Project Management
- `GET /api/v1/projects/` - List all projects
- `POST /api/v1/projects/` - Create new project
- `GET /api/v1/projects/{id}` - Get project details

### Drawing Management
- `POST /api/v1/drawings/upload/{project_id}/` - Upload drawing
- `GET /api/v1/drawings/project/{project_id}/` - Get project drawings

### Analysis
- `POST /api/v1/enhanced-analysis/drawing/{drawing_id}` - Analyze single drawing
- `POST /api/v1/enhanced-analysis/project/{project_id}/batch` - Batch analysis

## 🎯 Next Steps

1. **Upload Drawings**: Use the batch upload feature for multiple drawings
2. **Run Analysis**: Use enhanced analysis for cross-drawing references
3. **Generate Reports**: Create cost and carbon footprint reports
4. **Monitor Health**: Use the health check script regularly

## 📞 Support

If you encounter issues:
1. Run `./health-check.sh` to diagnose problems
2. Check the logs in the backend directory
3. Ensure all dependencies are installed with `./install-dependencies.sh`
4. Restart the platform with `./stop-platform.sh && ./start-platform.sh`

## 🔄 Updates

The platform now includes:
- ✅ Automatic dependency management
- ✅ Comprehensive error handling
- ✅ Graceful degradation for missing features
- ✅ Enhanced logging and monitoring
- ✅ Improved CORS configuration
- ✅ Better batch processing
- ✅ Robust startup scripts

All the identified bugs have been addressed and the platform should now run smoothly with minimal issues. 