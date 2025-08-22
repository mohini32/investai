#!/bin/bash

# InvestAI Project Setup Script
# This script sets up the complete development environment for InvestAI

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3.9+ is required but not found"
        exit 1
    fi
    
    # Check Node.js
    if command_exists node; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
    else
        print_error "Node.js 18+ is required but not found"
        exit 1
    fi
    
    # Check Docker
    if command_exists docker; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        print_success "Docker $DOCKER_VERSION found"
    else
        print_warning "Docker not found. You'll need to set up databases manually"
    fi
    
    # Check Docker Compose
    if command_exists docker-compose; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
        print_success "Docker Compose $COMPOSE_VERSION found"
    else
        print_warning "Docker Compose not found. You'll need to set up services manually"
    fi
}

# Function to setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate || source venv/Scripts/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating backend .env file..."
        cp .env.example .env
        print_warning "Please update the .env file with your configuration"
    fi
    
    # Create logs directory
    mkdir -p logs
    
    print_success "Backend setup completed"
    cd ..
}

# Function to setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env.local" ]; then
        print_status "Creating frontend .env.local file..."
        cp .env.example .env.local
        print_warning "Please update the .env.local file with your configuration"
    fi
    
    print_success "Frontend setup completed"
    cd ..
}

# Function to setup database with Docker
setup_database() {
    if command_exists docker && command_exists docker-compose; then
        print_status "Setting up database with Docker..."
        
        # Start only database services
        docker-compose up -d postgres redis
        
        # Wait for database to be ready
        print_status "Waiting for database to be ready..."
        sleep 10
        
        # Check if database is running
        if docker-compose ps postgres | grep -q "Up"; then
            print_success "Database is running"
        else
            print_error "Failed to start database"
            exit 1
        fi
        
        print_success "Database setup completed"
    else
        print_warning "Docker not available. Please set up PostgreSQL and Redis manually"
        print_warning "PostgreSQL: Create database 'investai_db'"
        print_warning "Redis: Start Redis server on port 6379"
    fi
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    cd backend
    source venv/bin/activate || source venv/Scripts/activate
    
    # Run Alembic migrations (when implemented)
    # alembic upgrade head
    
    # For now, just create tables using SQLAlchemy
    python -c "
from app.core.database import engine, Base
from app.models import *
Base.metadata.create_all(bind=engine)
print('Database tables created successfully')
"
    
    print_success "Database migrations completed"
    cd ..
}

# Function to create sample data
create_sample_data() {
    print_status "Creating sample data..."
    
    cd backend
    source venv/bin/activate || source venv/Scripts/activate
    
    # Create sample data script (to be implemented)
    # python scripts/create_sample_data.py
    
    print_success "Sample data created"
    cd ..
}

# Function to test setup
test_setup() {
    print_status "Testing setup..."
    
    # Test backend
    cd backend
    source venv/bin/activate || source venv/Scripts/activate
    
    print_status "Testing backend server..."
    timeout 10s uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    sleep 5
    
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        print_success "Backend server is working"
    else
        print_warning "Backend server test failed"
    fi
    
    kill $BACKEND_PID 2>/dev/null || true
    cd ..
    
    # Test frontend
    cd frontend
    print_status "Testing frontend build..."
    if npm run build >/dev/null 2>&1; then
        print_success "Frontend build successful"
    else
        print_warning "Frontend build failed"
    fi
    cd ..
}

# Function to display next steps
show_next_steps() {
    print_success "Setup completed successfully!"
    echo
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. Update configuration files:"
    echo "   - backend/.env (database, API keys, etc.)"
    echo "   - frontend/.env.local (API URL, etc.)"
    echo
    echo "2. Start the development servers:"
    echo "   Backend:  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
    echo "   Frontend: cd frontend && npm run dev"
    echo
    echo "3. Access the application:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo
    echo "4. Optional services (if using Docker):"
    echo "   PgAdmin: http://localhost:5050 (admin@investai.com / admin123)"
    echo "   Redis Commander: http://localhost:8081"
    echo
    echo -e "${GREEN}Happy coding! 🚀${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    InvestAI Setup Script                    ║"
    echo "║          AI-Powered Financial Advisor & Planner             ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    check_requirements
    setup_backend
    setup_frontend
    setup_database
    run_migrations
    # create_sample_data  # Uncomment when implemented
    test_setup
    show_next_steps
}

# Run main function
main "$@"
