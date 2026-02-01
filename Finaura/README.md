# FinAura - AI-Powered Financial Scoring Platform

FinAura is an innovative finance application that revolutionizes credit scoring using AI-driven analysis. Upload bills, track financial behavior, and unlock your true financial potential with blockchain-secured data.

## 🌟 Features

### Core Features
- **AI Credit Scoring**: Get your personalized FinAura Score (0-100) based on behavioral data and payment patterns
- **Smart Bill Scanning**: Upload or capture bills with AI-powered data extraction using OpenAI GPT-4 Vision
- **Explainable AI (XAI)**: Understand exactly why your score changes with transparent factor breakdowns
- **FinAura AI Assistant**: Conversational AI bot powered by GPT-4o to help with navigation and financial advice
- **Gamification**: Unlock achievements and earn rewards as you build your financial profile
- **Blockchain Data Vault**: Secure, blockchain-simulated storage of your financial identity

### Dashboard Features
- Real-time FinAura Score visualization
- Score breakdown with detailed factors
- Personalized recommendations
- Bill history and transaction tracking
- Achievement tracking system
- AI-powered chat assistant

## 🏗️ Tech Stack

### Frontend
- **React 19** with React Router for navigation
- **Tailwind CSS** for modern, responsive styling
- **Shadcn UI** components for beautiful, accessible UI
- **Axios** for API communication
- **Sonner** for toast notifications

### Backend
- **FastAPI** (Python) for high-performance API
- **Motor** (AsyncIO MongoDB driver) for database operations
- **OpenAI GPT-4o & GPT-4 Vision** via Emergent LLM integration
- **Pydantic** for data validation

### Database
- **MongoDB** for flexible document storage

### AI Integration
- **emergentintegrations** library for unified LLM access
- OpenAI GPT-4 Vision for bill image analysis
- OpenAI GPT-4o for conversational AI assistant
- Emergent Universal Key for seamless AI access

## 📊 How It Works

1. **Data Gathering**
   - Upload bill images through web interface
   - AI extracts vendor, amount, date, category automatically
   - Store transaction history securely

2. **AI Credit Score Generation**
   - ML algorithm calculates FinAura Score (0-100)
   - Considers payment history, category diversity, financial activity
   - Explainable AI provides transparency

3. **Blockchain Vault (Mocked)**
   - Secure, decentralized storage simulation
   - User-controlled access via smart contracts
   - Audit trail of all data access

4. **Gamification & Literacy**
   - Achievement system for financial milestones
   - AI assistant for guidance and education
   - Progress tracking

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB
- Emergent LLM Key (provided)

### Installation

1. **Backend Setup**
```bash
cd /app/backend
pip install -r requirements.txt
```

2. **Frontend Setup**
```bash
cd /app/frontend
yarn install
```

3. **Environment Variables**

Backend `.env`:
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=finaura_db
CORS_ORIGINS=*
EMERGENT_LLM_KEY=sk-emergent-1A16d6858F06305876
```

Frontend `.env`:
```
REACT_APP_BACKEND_URL=https://your-backend-url.com
```

### Running the Application

The application is managed by supervisor:

```bash
# Start all services
sudo supervisorctl start all

# Restart services after changes
sudo supervisorctl restart backend
sudo supervisorctl restart frontend

# Check status
sudo supervisorctl status
```

## 📱 Application Structure

### Frontend Routes
- `/` - Landing page with features overview
- `/app` - Main dashboard with tabs:
  - Dashboard - Score overview and insights
  - Upload Bill - Bill image upload interface
  - My Bills - Bill history
  - Achievements - Gamification rewards
  - AI Assistant - Chat with FinAura Bot

### Backend API Endpoints

#### User Management
- `POST /api/user/create` - Create new user
- `GET /api/user/{user_id}` - Get user profile
- `GET /api/user/{user_id}/score` - Get FinAura Score with explanation

#### Bill Management
- `POST /api/bills/upload` - Upload and analyze bill image
- `GET /api/bills/{user_id}` - Get user's bill history

#### AI Chat
- `POST /api/chat/message` - Send message to AI assistant
- `GET /api/chat/history/{session_id}` - Get chat history

#### Achievements
- `GET /api/achievements/{user_id}` - Get user achievements

#### Blockchain Vault (Mocked)
- `POST /api/vault/grant-access` - Grant data vault access
- `GET /api/vault/logs/{user_id}` - Get access logs

## 🎯 Score Calculation

The FinAura Score (0-100) is calculated based on:

1. **Bill Payment History (40%)**: Number and consistency of uploaded bills
2. **Category Diversity (30%)**: Variety of payment categories (groceries, utilities, etc.)
3. **Financial Activity Level (30%)**: Total transaction amounts and patterns

### Score Factors
- Payment History: Number of bills uploaded
- Category Diversity: Number of unique payment categories
- Financial Activity: Total spending amount

### Recommendations Engine
AI-powered recommendations based on:
- Current score level
- Missing data points
- Areas for improvement

## 🔐 Security Features

- Blockchain-simulated data vault
- User-controlled access permissions
- Audit trail for all data access
- Smart contract simulation for lender access

## 🎮 Gamification System

### Achievements
- **First Step**: Upload your first bill (10 points)
- **Getting Started**: Upload 5 bills (25 points)
- **Financial Tracker**: Upload 10 bills (50 points)
- **Finance Master**: Upload 20 bills (100 points)

Achievements unlock automatically as users reach milestones.

## 🤖 AI Integration

### Bill Analysis
- Powered by OpenAI GPT-4 Vision
- Extracts: vendor, amount, date, category, items, payment method
- Automatic categorization

### AI Assistant
- Powered by OpenAI GPT-4o
- Helps with app navigation
- Provides financial advice
- Explains FinAura Score factors
- Supports financial literacy

## 📈 Future Enhancements

- Real blockchain integration (Polygon/Hyperledger)
- Voice guidance in multiple languages
- Mobile app (Flutter)
- Integration with UPI/payment providers
- Loan repayment history tracking
- Microfinance integration
- Advanced ML scoring models
- Social credit features
- Financial literacy courses

## 🛠️ Development

### Adding New Features

1. **Backend**: Add routes in `/app/backend/server.py`
2. **Frontend**: Add components in `/app/frontend/src/`
3. **Database**: MongoDB collections auto-create on first use

### Testing

Frontend testing:
```bash
cd /app/frontend
yarn test
```

Backend testing:
```bash
cd /app/backend
pytest
```

## 📝 API Documentation

Once running, visit:
- API Docs: `https://your-backend-url.com/docs`
- ReDoc: `https://your-backend-url.com/redoc`

## 🤝 Contributing

This is a demonstration MVP. For production use:
1. Add authentication/authorization
2. Implement real blockchain integration
3. Add comprehensive error handling
4. Scale database for production
5. Add rate limiting and security measures
6. Implement data encryption at rest

## 📄 License

Built with Emergent AI Platform

## 🙏 Acknowledgments

- OpenAI for GPT models
- Emergent for LLM integration platform
- Shadcn for beautiful UI components
- FastAPI community
- React community

---

**Built with ❤️ using Emergent AI Platform**
