# InvestAI Project Structure

## 📁 Complete Directory Structure

```
investai/
├── README.md                           # Project overview and documentation
├── PROJECT_STRUCTURE.md               # This file - detailed project structure
├── .gitignore                         # Git ignore rules
├── docker-compose.yml                 # Docker services configuration
├── setup.sh                          # Unix/Linux setup script
├── setup.bat                         # Windows setup script
│
├── backend/                           # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application entry point
│   │   │
│   │   ├── core/                      # Core configurations
│   │   │   ├── __init__.py
│   │   │   ├── config.py              # Application settings
│   │   │   ├── database.py            # Database connection and utilities
│   │   │   └── security.py            # Authentication and security
│   │   │
│   │   ├── models/                    # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py                # User and preferences models
│   │   │   ├── portfolio.py           # Portfolio, holdings, transactions
│   │   │   ├── goals.py               # Financial goals and milestones
│   │   │   └── market_data.py         # Market data, stocks, mutual funds
│   │   │
│   │   ├── schemas/                   # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                # Authentication schemas
│   │   │   ├── user.py                # User schemas
│   │   │   ├── portfolio.py           # Portfolio schemas
│   │   │   ├── goals.py               # Goals schemas
│   │   │   └── market_data.py         # Market data schemas
│   │   │
│   │   ├── api/                       # API routes
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── api.py             # Main API router
│   │   │       └── endpoints/
│   │   │           ├── __init__.py
│   │   │           ├── auth.py        # Authentication endpoints
│   │   │           ├── users.py       # User management endpoints
│   │   │           ├── portfolios.py  # Portfolio management endpoints
│   │   │           ├── market_data.py # Market data endpoints
│   │   │           ├── goals.py       # Financial goals endpoints
│   │   │           └── ai_analysis.py # AI analysis endpoints
│   │   │
│   │   ├── services/                  # Business logic services
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py        # Authentication service
│   │   │   ├── portfolio_service.py   # Portfolio management service
│   │   │   ├── market_service.py      # Market data service
│   │   │   ├── goal_service.py        # Goals management service
│   │   │   ├── tax_service.py         # Tax calculation service
│   │   │   └── notification_service.py # Notification service
│   │   │
│   │   ├── ai/                        # AI and ML components
│   │   │   ├── __init__.py
│   │   │   ├── agents/                # CrewAI agents
│   │   │   │   ├── __init__.py
│   │   │   │   ├── analyst_agent.py   # Fundamental analysis agent
│   │   │   │   ├── advisor_agent.py   # Investment advisor agent
│   │   │   │   ├── risk_agent.py      # Risk assessment agent
│   │   │   │   └── tax_agent.py       # Tax planning agent
│   │   │   ├── tools/                 # AI tools and utilities
│   │   │   │   ├── __init__.py
│   │   │   │   ├── market_tools.py    # Market data tools
│   │   │   │   ├── analysis_tools.py  # Analysis tools
│   │   │   │   └── calculation_tools.py # Financial calculation tools
│   │   │   └── crew.py                # CrewAI crew configuration
│   │   │
│   │   └── utils/                     # Utility functions
│   │       ├── __init__.py
│   │       ├── helpers.py             # General helper functions
│   │       ├── validators.py          # Data validation utilities
│   │       ├── formatters.py          # Data formatting utilities
│   │       └── constants.py           # Application constants
│   │
│   ├── tests/                         # Backend tests
│   │   ├── __init__.py
│   │   ├── conftest.py                # Test configuration
│   │   ├── test_auth.py               # Authentication tests
│   │   ├── test_portfolios.py         # Portfolio tests
│   │   ├── test_market_data.py        # Market data tests
│   │   └── test_ai_analysis.py        # AI analysis tests
│   │
│   ├── alembic/                       # Database migrations
│   │   ├── versions/                  # Migration files
│   │   ├── env.py                     # Alembic environment
│   │   └── script.py.mako             # Migration template
│   │
│   ├── scripts/                       # Utility scripts
│   │   ├── create_sample_data.py      # Sample data creation
│   │   ├── update_market_data.py      # Market data update script
│   │   └── backup_database.py         # Database backup script
│   │
│   ├── logs/                          # Application logs
│   ├── requirements.txt               # Python dependencies
│   ├── .env.example                   # Environment variables example
│   ├── Dockerfile                     # Docker configuration
│   ├── alembic.ini                    # Alembic configuration
│   └── pytest.ini                     # Pytest configuration
│
├── frontend/                          # Next.js Frontend
│   ├── src/
│   │   ├── app/                       # Next.js 13+ App Router
│   │   │   ├── layout.tsx             # Root layout
│   │   │   ├── page.tsx               # Home page
│   │   │   ├── globals.css            # Global styles
│   │   │   ├── providers.tsx          # Context providers
│   │   │   │
│   │   │   ├── (auth)/                # Authentication pages
│   │   │   │   ├── login/
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── register/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── forgot-password/
│   │   │   │       └── page.tsx
│   │   │   │
│   │   │   ├── dashboard/             # Dashboard pages
│   │   │   │   ├── layout.tsx         # Dashboard layout
│   │   │   │   ├── overview/
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── portfolio/
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── goals/
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── tax-planning/
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── insurance/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── settings/
│   │   │   │       └── page.tsx
│   │   │   │
│   │   │   └── api/                   # API routes (if needed)
│   │   │       └── health/
│   │   │           └── route.ts
│   │   │
│   │   ├── components/                # React components
│   │   │   ├── ui/                    # Base UI components
│   │   │   │   ├── button.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── modal.tsx
│   │   │   │   └── chart.tsx
│   │   │   │
│   │   │   ├── auth/                  # Authentication components
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   ├── RegisterForm.tsx
│   │   │   │   └── ProtectedRoute.tsx
│   │   │   │
│   │   │   ├── dashboard/             # Dashboard components
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── OverviewCards.tsx
│   │   │   │   └── RecentTransactions.tsx
│   │   │   │
│   │   │   ├── portfolio/             # Portfolio components
│   │   │   │   ├── PortfolioSummary.tsx
│   │   │   │   ├── HoldingsList.tsx
│   │   │   │   ├── AssetAllocation.tsx
│   │   │   │   └── PerformanceChart.tsx
│   │   │   │
│   │   │   ├── goals/                 # Goals components
│   │   │   │   ├── GoalsList.tsx
│   │   │   │   ├── GoalCard.tsx
│   │   │   │   ├── CreateGoalForm.tsx
│   │   │   │   └── ProgressTracker.tsx
│   │   │   │
│   │   │   └── common/                # Common components
│   │   │       ├── Layout.tsx
│   │   │       ├── Loading.tsx
│   │   │       ├── ErrorBoundary.tsx
│   │   │       └── Notification.tsx
│   │   │
│   │   ├── hooks/                     # Custom React hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── usePortfolio.ts
│   │   │   ├── useMarketData.ts
│   │   │   ├── useGoals.ts
│   │   │   └── useLocalStorage.ts
│   │   │
│   │   ├── lib/                       # Utility libraries
│   │   │   ├── api.ts                 # API client
│   │   │   ├── auth.ts                # Authentication utilities
│   │   │   ├── utils.ts               # General utilities
│   │   │   ├── validations.ts         # Form validations
│   │   │   └── constants.ts           # Application constants
│   │   │
│   │   ├── types/                     # TypeScript type definitions
│   │   │   ├── auth.ts
│   │   │   ├── user.ts
│   │   │   ├── portfolio.ts
│   │   │   ├── goals.ts
│   │   │   └── api.ts
│   │   │
│   │   └── styles/                    # Additional styles
│   │       ├── components.css
│   │       └── utilities.css
│   │
│   ├── public/                        # Static assets
│   │   ├── favicon.ico
│   │   ├── logo.png
│   │   ├── og-image.png
│   │   └── icons/
│   │
│   ├── __tests__/                     # Frontend tests
│   │   ├── components/
│   │   ├── pages/
│   │   └── utils/
│   │
│   ├── package.json                   # Node.js dependencies
│   ├── package-lock.json              # Dependency lock file
│   ├── next.config.js                 # Next.js configuration
│   ├── tailwind.config.js             # Tailwind CSS configuration
│   ├── postcss.config.js              # PostCSS configuration
│   ├── tsconfig.json                  # TypeScript configuration
│   ├── .env.example                   # Environment variables example
│   ├── Dockerfile                     # Docker configuration
│   └── jest.config.js                 # Jest testing configuration
│
├── database/                          # Database related files
│   ├── init.sql                       # Database initialization script
│   ├── migrations/                    # Manual migration scripts
│   └── seeds/                         # Seed data files
│
├── docs/                              # Documentation
│   ├── api/                           # API documentation
│   ├── deployment/                    # Deployment guides
│   ├── development/                   # Development guides
│   └── user/                          # User documentation
│
├── nginx/                             # Nginx configuration (for production)
│   ├── nginx.conf
│   └── ssl/
│
└── scripts/                           # Project-level scripts
    ├── deploy.sh                      # Deployment script
    ├── backup.sh                      # Backup script
    └── monitoring.sh                  # Monitoring setup script
```

## 🔧 Key Components Implemented

### Backend (FastAPI)
- ✅ **Core Configuration**: Settings, database, security
- ✅ **Database Models**: Users, portfolios, goals, market data
- ✅ **Authentication**: JWT-based auth with security utilities
- ✅ **API Structure**: RESTful endpoints with proper routing
- ✅ **Pydantic Schemas**: Data validation and serialization
- 🔄 **AI Integration**: CrewAI framework setup (to be implemented)
- 🔄 **Services**: Business logic layer (to be implemented)

### Frontend (Next.js)
- ✅ **Project Setup**: Next.js 14 with TypeScript
- ✅ **Styling**: Tailwind CSS with custom design system
- ✅ **Configuration**: Environment setup and build configuration
- 🔄 **Components**: UI components and pages (to be implemented)
- 🔄 **State Management**: React Query integration (to be implemented)
- 🔄 **Authentication**: Auth context and protected routes (to be implemented)

### Infrastructure
- ✅ **Docker**: Multi-service setup with PostgreSQL and Redis
- ✅ **Database**: PostgreSQL with initialization scripts
- ✅ **Environment**: Configuration templates for all environments
- ✅ **Setup Scripts**: Automated setup for Windows and Unix systems

## 🚀 Getting Started

1. **Clone and Setup**:
   ```bash
   # Windows
   setup.bat
   
   # Unix/Linux/Mac
   ./setup.sh
   ```

2. **Manual Setup** (if scripts don't work):
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   
   # Database (with Docker)
   docker-compose up -d postgres redis
   ```

3. **Start Development Servers**:
   ```bash
   # Backend (Terminal 1)
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   
   # Frontend (Terminal 2)
   cd frontend
   npm run dev
   ```

## 📋 Next Development Steps

1. **Complete Database Schema** (Current task)
2. **Implement AI Integration** with CrewAI and Gemini
3. **Build Core Portfolio Management** features
4. **Integrate Market Data APIs** (NSE/BSE, Yahoo Finance)
5. **Develop Frontend Components** and pages
6. **Implement Authentication Flow**
7. **Add Testing Suite**
8. **Setup Deployment Pipeline**

## 🔗 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database Admin**: http://localhost:5050 (if using Docker)
- **Redis Commander**: http://localhost:8081 (if using Docker)

This structure provides a solid foundation for building the InvestAI application with proper separation of concerns, scalability, and maintainability.
