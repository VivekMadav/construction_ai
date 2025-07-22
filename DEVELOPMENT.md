# Construction AI Platform - Development Guide

## 🚀 Quick Start

### Option 1: One-Click Start (Recommended)
```bash
./start-platform.sh
```
This will:
- Start the backend server in a new terminal window
- Start the frontend server in another terminal window
- Open both services automatically

### Option 2: Manual Start
```bash
# Terminal 1 - Backend
./start-backend.sh

# Terminal 2 - Frontend  
./start-frontend.sh
```

### Stop All Services
```bash
./stop-platform.sh
```

## 🌐 Access Points

Once running, you can access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
Construction AI/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── venv/               # Python virtual environment
│   └── requirements-minimal.txt
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── pages/          # Next.js pages
│   │   └── styles/         # CSS styles
│   └── package.json
├── start-backend.sh        # Backend startup script
├── start-frontend.sh       # Frontend startup script
├── start-platform.sh       # Master startup script
└── stop-platform.sh        # Stop all services
```

## 🔧 Development Workflow

### Daily Development
1. **Start the platform**: `./construction-ai start`
2. **Make your changes** to code
3. **View changes** - both servers auto-reload
4. **Stop when done**: `./construction-ai stop`

### Backend Development
- **Location**: `backend/app/`
- **Auto-reload**: Yes (uvicorn --reload)
- **Database**: SQLite (`backend/construction_ai.db`)
- **API Testing**: http://localhost:8000/docs

### Frontend Development
- **Location**: `frontend/src/`
- **Auto-reload**: Yes (Next.js hot reload)
- **Styling**: Tailwind CSS
- **Testing**: http://localhost:3000

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :8000
lsof -i :3000

# Kill the process
kill -9 <PID>
```

### Dependencies Issues
```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements-minimal.txt

# Frontend
cd frontend
npm install
```

### Database Issues
```bash
cd backend
source venv/bin/activate
python -c "
from app.core.database import engine
from app.models.models import Base
Base.metadata.create_all(bind=engine)
print('Database reset successfully')
"
```

## 📚 Learning Path

### Week 1: Foundation
- [x] Project setup and scripts
- [ ] Backend API structure
- [ ] Frontend components
- [ ] Database models

### Week 2: Advanced Backend
- [ ] PDF processing
- [ ] ML integration
- [ ] Testing

### Week 3: Frontend Enhancement
- [ ] Advanced components
- [ ] State management
- [ ] User experience

## 💡 Tips

1. **Keep both terminals open** - you'll see logs and errors
2. **Use the API docs** - http://localhost:8000/docs for testing
3. **Check the browser console** - for frontend errors
4. **Database changes** - restart backend if you modify models
5. **Hot reload** - most changes don't require restarting servers 