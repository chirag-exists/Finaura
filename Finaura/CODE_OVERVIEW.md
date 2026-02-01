# FinAura Code Overview

## 📁 Project Structure

```
/app/
├── backend/
│   ├── server.py          # Main FastAPI application
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.js        # Main React application
│   │   ├── App.css       # Global styles
│   │   └── components/ui/ # Shadcn UI components
│   ├── package.json      # Node dependencies
│   └── .env              # Frontend environment variables
└── README.md             # Project documentation
```

## 🔧 Backend Code (`/app/backend/server.py`)

### Key Components

#### 1. **AI Bill Analysis Function**
```python
async def analyze_bill_image(image_base64: str) -> dict:
    # Uses OpenAI GPT-4 Vision to extract bill data
    api_key = os.environ.get('EMERGENT_LLM_KEY', '')
    chat = LlmChat(
        api_key=api_key,
        session_id=f"bill-analysis-{uuid.uuid4()}",
        system_message="You are a financial document analyzer."
    ).with_model("openai", "gpt-4o")
    
    image_content = ImageContent(image_base64=image_base64)
    
    prompt = """Extract: vendor, amount, date, category, items, payment_method"""
    
    response = await chat.send_message(UserMessage(
        text=prompt,
        file_contents=[image_content]
    ))
    
    return json.loads(response)
```

**What it does:**
- Converts uploaded bill image to base64
- Sends to OpenAI GPT-4 Vision model
- Extracts structured data (vendor, amount, date, category)
- Returns JSON with extracted information

---

#### 2. **FinAura Score Calculation**
```python
async def calculate_finaura_score(user_id: str) -> dict:
    bills = await db.bills.find({"user_id": user_id}).to_list(1000)
    
    # Calculate based on 3 factors:
    # 1. Bill frequency (40%)
    frequency_score = min(num_bills * 5, 40)
    
    # 2. Category diversity (30%)
    categories = set(bill.get('category', '') for bill in bills)
    category_score = min(len(categories) * 10, 30)
    
    # 3. Financial activity (30%)
    amount_score = min(30, (avg_amount / 100) * 10)
    
    total_score = frequency_score + category_score + amount_score
    
    return {
        "score": round(total_score, 1),
        "factors": [...],  # Detailed breakdown
        "recommendations": [...]  # Personalized advice
    }
```

**Score Algorithm:**
- **0-100 scale**
- Considers bill upload frequency (consistency)
- Rewards category diversity (groceries, utilities, etc.)
- Factors in total spending amount
- Provides explainable factors for transparency

---

#### 3. **API Endpoints**

##### User Management
```python
@api_router.post("/user/create")
async def create_user(name: str, email: str):
    user = UserProfile(name=name, email=email)
    await db.users.insert_one(user.model_dump())
    return user

@api_router.get("/user/{user_id}/score")
async def get_user_score(user_id: str):
    score_data = await calculate_finaura_score(user_id)
    # Update user's score in database
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"finaura_score": score_data["score"]}}
    )
    return score_data
```

##### Bill Upload
```python
@api_router.post("/bills/upload")
async def upload_bill(user_id: str = Form(...), file: UploadFile = File(...)):
    contents = await file.read()
    image_base64 = base64.b64encode(contents).decode('utf-8')
    
    # AI analysis
    extracted_data = await analyze_bill_image(image_base64)
    
    # Save to database
    bill = Bill(user_id=user_id, extracted_data=extracted_data, ...)
    await db.bills.insert_one(bill.model_dump())
    
    # Update stats and check achievements
    await db.users.update_one({"id": user_id}, {"$inc": {"total_bills": 1}})
    await check_and_unlock_achievements(user_id)
    
    return {"success": True, "bill": bill}
```

##### AI Chatbot
```python
@api_router.post("/chat/message")
async def chat_message(session_id: str, message: str, user_id: str):
    api_key = os.environ.get('EMERGENT_LLM_KEY', '')
    
    chat = LlmChat(
        api_key=api_key,
        session_id=session_id,
        system_message="You are FinAura Bot..."
    ).with_model("openai", "gpt-4o")
    
    response = await chat.send_message(UserMessage(text=message))
    
    # Save conversation
    await db.chat_messages.insert_one({
        "session_id": session_id,
        "role": "user",
        "content": message
    })
    await db.chat_messages.insert_one({
        "session_id": session_id,
        "role": "assistant",
        "content": response
    })
    
    return {"response": response}
```

---

#### 4. **Gamification System**
```python
async def check_and_unlock_achievements(user_id: str):
    user = await db.users.find_one({"id": user_id})
    bills_count = user.get('total_bills', 0)
    
    achievement_rules = [
        {"title": "First Step", "threshold": 1, "points": 10},
        {"title": "Getting Started", "threshold": 5, "points": 25},
        {"title": "Financial Tracker", "threshold": 10, "points": 50},
        {"title": "Finance Master", "threshold": 20, "points": 100},
    ]
    
    for rule in achievement_rules:
        if bills_count >= rule['threshold']:
            # Check if not already unlocked
            existing = await db.achievements.find_one({
                "user_id": user_id,
                "title": rule['title']
            })
            if not existing:
                achievement = Achievement(
                    user_id=user_id,
                    title=rule['title'],
                    unlocked=True,
                    ...
                )
                await db.achievements.insert_one(achievement.model_dump())
```

---

## 🎨 Frontend Code (`/app/frontend/src/App.js`)

### Key Components

#### 1. **Landing Page Component**
```javascript
const LandingPage = () => {
  const navigate = useNavigate();
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50">
      {/* Hero Section */}
      <section className="container mx-auto px-6 py-20 text-center">
        <h2 className="text-6xl md:text-7xl font-bold mb-6">
          <span className="bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 bg-clip-text text-transparent">
            Your Financial Aura,
          </span>
          <br />
          <span className="text-slate-800">Powered by AI</span>
        </h2>
        <Button onClick={() => navigate('/app')}>
          Start Your Journey
        </Button>
      </section>
      
      {/* Features Section */}
      <section>
        <Card>
          <CardTitle>AI Credit Scoring</CardTitle>
          <CardDescription>Get your FinAura Score...</CardDescription>
        </Card>
        {/* More feature cards */}
      </section>
    </div>
  );
};
```

**Design Features:**
- Gradient backgrounds (emerald/teal theme)
- Card-based layout with hover effects
- Responsive grid system
- Modern typography with Inter font

---

#### 2. **Dashboard Component**
```javascript
const Dashboard = () => {
  const [userId, setUserId] = useState('demo-user-123');
  const [score, setScore] = useState(null);
  const [bills, setBills] = useState([]);
  const [achievements, setAchievements] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  
  // Initialize user on mount
  useEffect(() => {
    initializeUser();
  }, []);
  
  const loadUserData = async () => {
    const [scoreRes, billsRes, achievementsRes] = await Promise.all([
      axios.get(`${API}/user/${userId}/score`),
      axios.get(`${API}/bills/${userId}`),
      axios.get(`${API}/achievements/${userId}`)
    ]);
    setScore(scoreRes.data);
    setBills(billsRes.data);
    setAchievements(achievementsRes.data);
  };
  
  return (
    <Tabs value={activeTab} onValueChange={setActiveTab}>
      <TabsList>
        <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
        <TabsTrigger value="upload">Upload Bill</TabsTrigger>
        <TabsTrigger value="bills">My Bills</TabsTrigger>
        <TabsTrigger value="achievements">Achievements</TabsTrigger>
        <TabsTrigger value="bot">AI Assistant</TabsTrigger>
      </TabsList>
      
      {/* Tab content for each section */}
    </Tabs>
  );
};
```

---

#### 3. **Bill Upload Handler**
```javascript
const handleFileUpload = async (e) => {
  const file = e.target.files?.[0];
  if (!file) return;
  
  setUploading(true);
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    
    const response = await axios.post(`${API}/bills/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    toast.success('Bill uploaded and analyzed successfully!');
    loadUserData(); // Refresh dashboard
  } catch (error) {
    toast.error('Error uploading bill: ' + error.message);
  } finally {
    setUploading(false);
  }
};
```

**Flow:**
1. User selects image file
2. Create FormData with file and user_id
3. POST to `/api/bills/upload`
4. Backend analyzes with AI
5. Display success toast
6. Reload dashboard data

---

#### 4. **AI Chat Interface**
```javascript
const sendChatMessage = async () => {
  if (!chatInput.trim()) return;
  
  // Add user message to UI
  const userMessage = { role: 'user', content: chatInput };
  setChatMessages([...chatMessages, userMessage]);
  setChatInput('');
  
  try {
    // Send to backend
    const response = await axios.post(
      `${API}/chat/message?session_id=${sessionId}&message=${encodeURIComponent(chatInput)}&user_id=${userId}`
    );
    
    // Add bot response to UI
    const botMessage = { role: 'assistant', content: response.data.response };
    setChatMessages(prev => [...prev, botMessage]);
  } catch (error) {
    toast.error('Error sending message');
  }
};

// Render chat
{chatMessages.map((msg, idx) => (
  <div key={idx} className={msg.role === 'user' ? 'justify-end' : 'justify-start'}>
    <div className={msg.role === 'user' 
      ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white' 
      : 'bg-white border border-slate-200'}>
      {msg.content}
    </div>
  </div>
))}
```

---

#### 5. **Score Visualization**
```javascript
<Card className="bg-gradient-to-br from-emerald-500 to-teal-600 text-white">
  <CardHeader>
    <CardTitle>Your FinAura Score</CardTitle>
  </CardHeader>
  <CardContent>
    <div className="text-7xl font-bold">{score?.score || 50}</div>
    <Progress value={score?.score || 50} className="h-3 bg-white/30" />
    <p>Out of 100</p>
  </CardContent>
</Card>

{/* Score Factors */}
{score?.factors.map((factor, idx) => (
  <div key={idx}>
    <span>{factor.name}</span>
    <Badge variant={factor.impact === 'Positive' ? 'default' : 'secondary'}>
      {factor.impact}
    </Badge>
    <Progress value={factor.score || 0} />
    <p>Value: {factor.value}</p>
  </div>
))}
```

---

## 🗄️ Database Schema (MongoDB)

### Collections

#### 1. **users**
```javascript
{
  id: "uuid",
  name: "string",
  email: "string",
  finaura_score: 0.0,
  total_bills: 0,
  total_transactions: 0.0,
  achievements: [],
  created_at: "ISO timestamp"
}
```

#### 2. **bills**
```javascript
{
  id: "uuid",
  user_id: "uuid",
  extracted_data: {
    vendor: "string",
    amount: 0,
    date: "YYYY-MM-DD",
    category: "string",
    items: [],
    payment_method: "string"
  },
  amount: 0,
  vendor: "string",
  date: "YYYY-MM-DD",
  category: "string",
  created_at: "ISO timestamp"
}
```

#### 3. **achievements**
```javascript
{
  id: "uuid",
  user_id: "uuid",
  title: "string",
  description: "string",
  icon: "string",
  points: 0,
  unlocked: true,
  unlocked_at: "ISO timestamp"
}
```

#### 4. **chat_messages**
```javascript
{
  id: "uuid",
  session_id: "string",
  role: "user|assistant",
  content: "string",
  created_at: "ISO timestamp"
}
```

#### 5. **vault_logs** (Blockchain simulation)
```javascript
{
  id: "uuid",
  user_id: "uuid",
  accessor: "string",
  purpose: "string",
  granted: true,
  timestamp: "ISO timestamp"
}
```

---

## 🔑 Environment Variables

### Backend (`.env`)
```bash
MONGO_URL=mongodb://localhost:27017
DB_NAME=finaura_db
CORS_ORIGINS=*
EMERGENT_LLM_KEY=sk-emergent-1A16d6858F06305876
```

### Frontend (`.env`)
```bash
REACT_APP_BACKEND_URL=https://finance-lens-5.preview.emergentagent.com
WDS_SOCKET_PORT=443
```

---

## 🤖 AI Integration Details

### Using emergentintegrations Library

```python
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent

# For text chat (GPT-4o)
chat = LlmChat(
    api_key=os.environ.get('EMERGENT_LLM_KEY'),
    session_id="unique-session-id",
    system_message="System prompt here"
).with_model("openai", "gpt-4o")

response = await chat.send_message(UserMessage(text="Your message"))

# For image analysis (GPT-4 Vision)
chat = LlmChat(
    api_key=os.environ.get('EMERGENT_LLM_KEY'),
    session_id="bill-analysis-123",
    system_message="You are a financial document analyzer"
).with_model("openai", "gpt-4o")

image_content = ImageContent(image_base64=base64_string)
response = await chat.send_message(UserMessage(
    text="Extract bill details",
    file_contents=[image_content]
))
```

**Models Used:**
- **GPT-4o**: Conversational AI for chatbot
- **GPT-4 Vision**: Bill image analysis and data extraction

**Universal Key:**
- Single key works across OpenAI, Anthropic, and Google models
- Managed by Emergent platform
- Credits deducted from user's balance

---

## 🎨 UI Component Usage

### Shadcn Components Used
```javascript
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Toaster } from '@/components/ui/sonner';
import { toast } from 'sonner';
```

**Styling Approach:**
- Tailwind CSS utility classes
- Custom gradient color scheme (emerald/teal)
- Modern Inter font
- Responsive design with mobile-first approach
- Smooth transitions and hover effects
- Card-based layouts with shadows

---

## 📊 Data Flow

### Bill Upload Flow
```
User selects image
    ↓
Frontend: FormData with file + user_id
    ↓
POST /api/bills/upload
    ↓
Backend: Convert to base64
    ↓
OpenAI GPT-4 Vision: Analyze image
    ↓
Extract: vendor, amount, date, category
    ↓
Save to MongoDB bills collection
    ↓
Update user statistics
    ↓
Check and unlock achievements
    ↓
Return success response
    ↓
Frontend: Show toast, reload dashboard
```

### Score Calculation Flow
```
GET /api/user/{user_id}/score
    ↓
Fetch all user's bills from MongoDB
    ↓
Calculate 3 factors:
  - Frequency score (40%)
  - Category diversity (30%)
  - Activity level (30%)
    ↓
Generate recommendations based on score
    ↓
Update user's score in database
    ↓
Return score + factors + recommendations
    ↓
Frontend: Display visual breakdown
```

### Chat Flow
```
User types message
    ↓
POST /api/chat/message
    ↓
Create LlmChat with OpenAI GPT-4o
    ↓
Send message with system context
    ↓
Receive AI response
    ↓
Save user message + bot response to MongoDB
    ↓
Return response to frontend
    ↓
Display in chat interface
```

---

## 🚀 Key Features Implementation

### 1. Explainable AI (XAI)
- Score broken down into 3 transparent factors
- Each factor shows value, impact, and contribution
- Visual progress bars for each component
- Personalized recommendations

### 2. Gamification
- Achievement system with 4 tiers
- Auto-unlock based on milestones
- Points system (10-100 per achievement)
- Visual cards with emojis

### 3. Blockchain Vault (Mocked)
- Access logging system
- Grant/revoke permissions
- Audit trail
- Ready for real blockchain integration

---

## 🔧 Testing

### Backend Testing
```bash
# Test API endpoints
curl https://finance-lens-5.preview.emergentagent.com/api/
curl https://finance-lens-5.preview.emergentagent.com/api/user/{user_id}/score
```

### Frontend Testing
- Screenshot tool for visual verification
- Manual testing of all tabs and features
- AI chat interaction testing
- File upload testing

---

## 📦 Dependencies

### Backend
```
fastapi==0.110.1
uvicorn==0.25.0
motor==3.3.1 (async MongoDB)
pymongo==4.5.0
pydantic>=2.6.4
python-dotenv>=1.0.1
emergentintegrations (custom)
openai==1.99.9
```

### Frontend
```
react@19.0.0
react-router-dom@7.5.1
axios@1.8.4
tailwindcss@3.4.17
@radix-ui/* (Shadcn components)
sonner@2.0.3 (toasts)
```

---

This code overview shows the complete implementation of FinAura with all AI-powered features, modern UI, and scalable architecture! 🚀
