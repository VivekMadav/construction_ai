# Construction AI Platform

An AI-powered platform for quantity surveyors to automate construction cost estimation and carbon footprint analysis.

## Project Overview

This platform uses machine learning and computer vision to:
- Analyze construction drawings and BIM models
- Identify building elements and materials
- Calculate costs and carbon footprint
- Generate detailed quantity surveys and reports

## Tech Stack

### Backend
- **Python 3.11+** - Core programming language
- **FastAPI** - Modern, fast web framework
- **PostgreSQL** - Primary database
- **Redis** - Caching and session management
- **OpenCV** - Image processing
- **PyTorch** - Machine learning models
- **PaddleOCR** - Text extraction from drawings

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Hook Form** - Form handling
- **React Query** - Data fetching

### Infrastructure
- **Docker** - Containerization
- **GitHub Actions** - CI/CD
- **AWS/Azure** - Cloud hosting

## Project Structure

```
construction-ai-platform/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utility functions
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Next.js pages
│   │   ├── hooks/          # Custom hooks
│   │   └── utils/          # Frontend utilities
│   ├── tests/              # Frontend tests
│   └── package.json        # Node dependencies
├── ml/                     # Machine learning models
│   ├── models/             # Trained models
│   ├── training/           # Training scripts
│   └── data/               # Training data
├── docs/                   # Documentation
└── docker-compose.yml      # Development environment
```

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+

### Quick Start (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd construction-ai-platform
   ```

2. **Start the platform with one command**
   ```bash
   ./construction-ai start
   ```
   
   This will automatically:
   - Set up the Python virtual environment
   - Install all dependencies
   - Start the backend server
   - Start the frontend server
   - Open both in separate terminal windows

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Setup (Alternative)

If you prefer manual control:

```bash
# Start backend only
./start-backend.sh

# Start frontend only  
./start-frontend.sh

# Stop all services
./construction-ai stop

# Check status
./construction-ai status
```

## Development Guidelines

### Code Quality
- Follow PEP 8 for Python code
- Use TypeScript strict mode
- Write comprehensive tests
- Document all API endpoints
- Use conventional commits

### Testing Strategy
- Unit tests for all business logic
- Integration tests for API endpoints
- E2E tests for critical user flows
- Performance tests for ML models

### Security
- Input validation on all endpoints
- Authentication and authorization
- Rate limiting
- Data encryption
- Regular security audits

## MVP Features

### Phase 1 (Current)
- [x] Project setup and structure
- [ ] PDF upload and processing
- [ ] Basic element detection
- [ ] Cost calculation engine
- [ ] Simple web interface
- [ ] Report generation

### Phase 2 (Future)
- [ ] BIM model integration
- [ ] Advanced ML models
- [ ] Carbon footprint analysis
- [ ] Multi-project management
- [ ] User authentication

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests
4. Update documentation
5. Submit a pull request

## License

Proprietary - All rights reserved

## Contact

For questions or support, contact the development team. 