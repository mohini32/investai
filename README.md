<<<<<<< HEAD
# InvestAI - AI-Powered Financial Advisor & Investment Planner

## 🚀 Overview

InvestAI is a comprehensive AI-powered financial planning assistant specifically designed for the Indian market. It provides personalized investment recommendations, portfolio management, tax optimization, and insurance guidance using advanced multi-agent AI architecture.

## 🎯 Key Features

### MVP Features
- **Portfolio Analysis & Tracking** - Real-time P&L, asset allocation, performance monitoring
- **AI-Powered Investment Recommendations** - Stock and mutual fund suggestions based on user profile
- **Fundamental Analysis Engine** - Financial ratios, business moat analysis, buy/hold/sell recommendations
- **Goal-Based Planning** - Retirement, education, emergency fund calculators with progress tracking
- **Tax Planning Tools** - Section 80C optimization, capital gains calculator, tax-saving suggestions
- **Basic Insurance Advisory** - Term and health insurance coverage recommendations
- **User Risk Profiling** - Questionnaire-based risk assessment and personalized advice
- **Real-time Market Data** - Live stock prices, mutual fund NAVs, market news integration

## 🛠️ Technology Stack

- **Backend:** FastAPI (Python)
- **Frontend:** Next.js (TypeScript)
- **Database:** PostgreSQL
- **AI Framework:** CrewAI + Google Gemini API
- **Caching:** Redis
- **Deployment:** Vercel (Frontend) + Railway (Backend)

## 📁 Project Structure

```
investai/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configurations
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   ├── ai/             # AI agents and analysis
│   │   └── utils/          # Utility functions
│   ├── tests/              # Backend tests
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Docker configuration
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Next.js pages
│   │   ├── hooks/          # Custom React hooks
│   │   ├── utils/          # Utility functions
│   │   └── types/          # TypeScript types
│   ├── public/             # Static assets
│   ├── package.json        # Node.js dependencies
│   └── next.config.js      # Next.js configuration
├── database/               # Database migrations and seeds
├── docs/                   # Documentation
├── docker-compose.yml      # Local development setup
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Database Setup
```bash
# Create PostgreSQL database
createdb investai_db

# Run migrations (to be implemented)
cd backend
alembic upgrade head
```

## 🔧 Environment Variables

Create `.env` files in both backend and frontend directories:

### Backend (.env)
```
DATABASE_URL=postgresql://username:password@localhost/investai_db
REDIS_URL=redis://localhost:6379
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_secret_key
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 Development Roadmap

- [x] Project setup and structure
- [ ] Database schema design
- [ ] AI integration with CrewAI
- [ ] Core portfolio management
- [ ] Market data integration
- [ ] Fundamental analysis engine
- [ ] User authentication
- [ ] Goal-based planning
- [ ] Tax planning tools
- [ ] Insurance advisory
- [ ] Frontend dashboard
- [ ] Testing suite
- [ ] Deployment setup

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for Indian investors**
=======
# investai
AI-powered investment analysis platform with real-time market data, portfolio optimization, and intelligent trading recommendations
>>>>>>> fd5b225aafb2d67969ef4cea0a6cc16bcdd61498
