from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException, Form
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import base64
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'finaura_db')]

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Models
class UserProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    finaura_score: float = 0.0
    total_bills: int = 0
    total_transactions: float = 0.0
    achievements: List[str] = []
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Bill(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    image_data: Optional[str] = None
    extracted_data: dict
    amount: float
    vendor: str
    date: str
    category: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ScoreExplanation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    score: float
    factors: List[dict]
    recommendations: List[str]
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    role: str  # user or assistant
    content: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Achievement(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    description: str
    icon: str
    points: int
    unlocked: bool = False
    unlocked_at: Optional[str] = None

class VaultAccessLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    accessor: str
    purpose: str
    granted: bool
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Helper function to analyze bills with AI
async def analyze_bill_image(image_base64: str) -> dict:
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY', '')
        chat = LlmChat(
            api_key=api_key,
            session_id=f"bill-analysis-{uuid.uuid4()}",
            system_message="You are a financial document analyzer. Extract bill/invoice details accurately."
        ).with_model("openai", "gpt-4o")
        
        image_content = ImageContent(image_base64=image_base64)
        
        prompt = """Analyze this bill/invoice image and extract the following information in JSON format:
        {
            "vendor": "vendor name",
            "amount": total amount as number,
            "date": "date in YYYY-MM-DD format",
            "category": "category like groceries, utilities, shopping, food, etc",
            "items": ["list of items if visible"],
            "payment_method": "cash/card/upi if visible"
        }
        
        Respond ONLY with valid JSON, no additional text."""
        
        user_message = UserMessage(
            text=prompt,
            file_contents=[image_content]
        )
        
        response = await chat.send_message(user_message)
        
        # Parse JSON from response
        try:
            data = json.loads(response)
        except:
            # If not valid JSON, try to extract JSON from text
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("Could not parse JSON from response")
        
        return data
    except Exception as e:
        logging.error(f"Error analyzing bill: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze bill: {str(e)}")

# Calculate FinAura Score
async def calculate_finaura_score(user_id: str) -> dict:
    try:
        # Get user's bills
        bills = await db.bills.find({"user_id": user_id}).to_list(1000)
        
        if len(bills) == 0:
            return {
                "score": 50.0,
                "factors": [
                    {"name": "Payment History", "value": 0, "impact": "No data"},
                    {"name": "Bill Consistency", "value": 0, "impact": "No data"},
                    {"name": "Financial Activity", "value": 0, "impact": "No data"}
                ],
                "recommendations": [
                    "Start uploading bills to build your financial profile",
                    "Regular bill payments improve your score",
                    "Diverse payment categories strengthen your profile"
                ]
            }
        
        # Calculate score based on multiple factors
        total_amount = sum(bill.get('amount', 0) for bill in bills)
        num_bills = len(bills)
        
        # Categories diversity
        categories = set(bill.get('category', '') for bill in bills)
        category_score = min(len(categories) * 10, 30)
        
        # Bill frequency (consistency)
        frequency_score = min(num_bills * 5, 40)
        
        # Amount consistency
        avg_amount = total_amount / num_bills if num_bills > 0 else 0
        amount_score = min(30, (avg_amount / 100) * 10) if avg_amount > 0 else 10
        
        # Total score (0-100)
        score = category_score + frequency_score + amount_score
        score = max(30, min(100, score))  # Keep between 30-100
        
        factors = [
            {
                "name": "Bill Payment History",
                "value": num_bills,
                "impact": "Positive" if num_bills > 5 else "Moderate",
                "score": frequency_score
            },
            {
                "name": "Category Diversity",
                "value": len(categories),
                "impact": "Positive" if len(categories) > 3 else "Needs Improvement",
                "score": category_score
            },
            {
                "name": "Financial Activity Level",
                "value": f"₹{total_amount:.2f}",
                "impact": "Active" if total_amount > 1000 else "Growing",
                "score": amount_score
            }
        ]
        
        recommendations = []
        if num_bills < 5:
            recommendations.append("Upload more bills to establish a stronger payment history")
        if len(categories) < 3:
            recommendations.append("Diversify your payment categories to improve your score")
        if score < 70:
            recommendations.append("Keep uploading bills regularly to boost your FinAura Score")
        else:
            recommendations.append("Great job! Your financial behavior is excellent")
        
        return {
            "score": round(score, 1),
            "factors": factors,
            "recommendations": recommendations
        }
    except Exception as e:
        logging.error(f"Error calculating score: {str(e)}")
        return {
            "score": 50.0,
            "factors": [],
            "recommendations": ["Error calculating score. Please try again."]
        }

# Routes
@api_router.get("/")
async def root():
    return {"message": "FinAura API is running", "status": "active"}

# User routes
@api_router.post("/user/create")
async def create_user(name: str, email: str):
    user = UserProfile(name=name, email=email)
    doc = user.model_dump()
    await db.users.insert_one(doc)
    return user

@api_router.get("/user/{user_id}")
async def get_user(user_id: str):
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@api_router.get("/user/{user_id}/score")
async def get_user_score(user_id: str):
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    score_data = await calculate_finaura_score(user_id)
    
    # Update user's score in database
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"finaura_score": score_data["score"]}}
    )
    
    return score_data

# Bill routes
@api_router.post("/bills/upload")
async def upload_bill(user_id: str = Form(...), file: UploadFile = File(...)):
    try:
        # Read image file
        contents = await file.read()
        image_base64 = base64.b64encode(contents).decode('utf-8')
        
        # Analyze with AI
        extracted_data = await analyze_bill_image(image_base64)
        
        # Create bill record
        bill = Bill(
            user_id=user_id,
            extracted_data=extracted_data,
            amount=extracted_data.get('amount', 0),
            vendor=extracted_data.get('vendor', 'Unknown'),
            date=extracted_data.get('date', datetime.now(timezone.utc).strftime('%Y-%m-%d')),
            category=extracted_data.get('category', 'Other')
        )
        
        doc = bill.model_dump()
        await db.bills.insert_one(doc)
        
        # Update user stats
        await db.users.update_one(
            {"id": user_id},
            {
                "$inc": {"total_bills": 1, "total_transactions": extracted_data.get('amount', 0)}
            }
        )
        
        # Check for achievements
        await check_and_unlock_achievements(user_id)
        
        return {"success": True, "bill": bill, "extracted_data": extracted_data}
    except Exception as e:
        logging.error(f"Error uploading bill: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/bills/{user_id}")
async def get_user_bills(user_id: str):
    bills = await db.bills.find({"user_id": user_id}, {"_id": 0}).to_list(1000)
    return bills

# Chat bot routes
@api_router.post("/chat/message")
async def chat_message(session_id: str, message: str, user_id: str):
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY', '')
        
        # Get chat history
        history = await db.chat_messages.find({"session_id": session_id}, {"_id": 0}).sort("created_at", 1).to_list(100)
        
        # Create chat with context
        system_message = """You are FinAura Bot, a helpful AI assistant for the FinAura finance app. 
        You help users navigate the app, understand their FinAura Score, manage bills, and improve their financial health.
        Be friendly, concise, and provide actionable advice. Guide users on:
        - How to upload bills
        - Understanding their credit score
        - Unlocking achievements
        - Managing their financial data vault
        - Financial literacy tips
        """
        
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=system_message
        ).with_model("openai", "gpt-4o")
        
        user_message = UserMessage(text=message)
        response = await chat.send_message(user_message)
        
        # Save messages to database
        user_msg = ChatMessage(session_id=session_id, role="user", content=message)
        bot_msg = ChatMessage(session_id=session_id, role="assistant", content=response)
        
        await db.chat_messages.insert_one(user_msg.model_dump())
        await db.chat_messages.insert_one(bot_msg.model_dump())
        
        return {"response": response, "session_id": session_id}
    except Exception as e:
        logging.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    messages = await db.chat_messages.find({"session_id": session_id}, {"_id": 0}).sort("created_at", 1).to_list(1000)
    return messages

# Achievements routes
async def check_and_unlock_achievements(user_id: str):
    user = await db.users.find_one({"id": user_id})
    if not user:
        return
    
    bills_count = user.get('total_bills', 0)
    achievements_to_unlock = []
    
    # Define achievements
    achievement_rules = [
        {"title": "First Step", "description": "Upload your first bill", "icon": "trophy", "points": 10, "threshold": 1},
        {"title": "Getting Started", "description": "Upload 5 bills", "icon": "star", "points": 25, "threshold": 5},
        {"title": "Financial Tracker", "description": "Upload 10 bills", "icon": "medal", "points": 50, "threshold": 10},
        {"title": "Finance Master", "description": "Upload 20 bills", "icon": "crown", "points": 100, "threshold": 20},
    ]
    
    for rule in achievement_rules:
        if bills_count >= rule['threshold']:
            # Check if already unlocked
            existing = await db.achievements.find_one({"user_id": user_id, "title": rule['title']})
            if not existing:
                achievement = Achievement(
                    user_id=user_id,
                    title=rule['title'],
                    description=rule['description'],
                    icon=rule['icon'],
                    points=rule['points'],
                    unlocked=True,
                    unlocked_at=datetime.now(timezone.utc).isoformat()
                )
                await db.achievements.insert_one(achievement.model_dump())
                achievements_to_unlock.append(achievement)

@api_router.get("/achievements/{user_id}")
async def get_achievements(user_id: str):
    achievements = await db.achievements.find({"user_id": user_id}, {"_id": 0}).to_list(1000)
    return achievements

# Vault routes (mocked blockchain)
@api_router.post("/vault/grant-access")
async def grant_vault_access(user_id: str, accessor: str, purpose: str):
    log = VaultAccessLog(
        user_id=user_id,
        accessor=accessor,
        purpose=purpose,
        granted=True
    )
    await db.vault_logs.insert_one(log.model_dump())
    return {"success": True, "message": "Access granted via blockchain smart contract", "log": log}

@api_router.get("/vault/logs/{user_id}")
async def get_vault_logs(user_id: str):
    logs = await db.vault_logs.find({"user_id": user_id}, {"_id": 0}).to_list(1000)
    return logs

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()