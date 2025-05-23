# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field # For data validation and request/response models
from typing import List, Dict, Optional
from textblob import TextBlob # For sentiment analysis
import re # For regular expressions (intent recognition)
import uuid # For generating unique ticket IDs

# --- Initialize FastAPI App ---
app = FastAPI(
    title="Customer Support Helper API",
    description="An API to assist with customer support tasks, including FAQ, ticket submission with sentiment analysis, and basic intent actions.",
    version="0.1.0",
)

# --- In-Memory Data Stores (for simplicity, replace with a database in a real application) ---
# 1. FAQ Data
faq_database: Dict[str, Dict[str, str]] = {
    "password_reset": {
        "keywords": ["password", "reset", "forgot", "change account"],
        "question": "How do I reset my password?",
        "answer": "You can reset your password by visiting the 'Account Settings' page and clicking on 'Forgot Password'. An email will be sent to you with instructions."
    },
    "shipping_info": {
        "keywords": ["shipping", "delivery", "track", "package", "how long", "ship"],
        "question": "How long does shipping take?",
        "answer": "Standard shipping usually takes 3-5 business days. Expedited shipping takes 1-2 business days. You will receive a tracking number once your order ships."
    },
    "return_policy": {
        "keywords": ["return", "refund", "exchange", "policy"],
        "question": "What is your return policy?",
        "answer": "You can return most new, unopened items within 30 days of delivery for a full refund. We'll also pay the return shipping costs if the return is a result of our error."
    },
    "payment_options": {
        "keywords": ["payment", "pay", "credit card", "paypal", "options"],
        "question": "What payment options do you accept?",
        "answer": "We accept Visa, MasterCard, American Express, and PayPal."
    }
}

# 2. Support Tickets
support_tickets_db: Dict[str, Dict] = {} # Stores tickets, key is ticket_id

# --- Pydantic Models (for Request and Response Data Validation) ---
class FAQQuery(BaseModel):
    query: str = Field(..., min_length=3, example="How to change my password?")

class FAQResponse(BaseModel):
    matched_question: Optional[str] = None
    answer: str

class TicketInput(BaseModel):
    user_email: str = Field(..., example="user@example.com")
    issue_description: str = Field(..., min_length=10, example="My order is late and I'm very unhappy!")

class TicketResponse(BaseModel):
    ticket_id: str
    user_email: str
    issue_description: str
    status: str = "submitted"
    sentiment: str # positive, negative, or neutral
    timestamp: str

class ActionQuery(BaseModel):
    query: str = Field(..., example="Track my order ORD12345")

class ActionResponse(BaseModel):
    intent: str
    entities: Dict[str, str] = {}
    message: str

# --- Helper Functions (AI-like features) ---

def get_sentiment(text: str) -> str:
    """
    Analyzes the sentiment of a given text.
    Returns 'positive', 'negative', or 'neutral'.
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"

def find_faq_answer(user_query: str) -> Optional[Dict[str, str]]:
    """
    Finds an FAQ answer based on keyword matching.
    """
    user_query_lower = user_query.lower()
    best_match_score = 0
    best_faq_id = None

    for faq_id, faq_item in faq_database.items():
        current_score = 0
        for keyword in faq_item["keywords"]:
            if keyword in user_query_lower:
                current_score += 1
        
        # Prioritize if more keywords match
        if current_score > best_match_score:
            best_match_score = current_score
            best_faq_id = faq_id
        # Basic tie-breaking: if same score, prefer shorter query matches (not implemented here for simplicity)

    if best_faq_id and best_match_score > 0: # Require at least one keyword match
        return faq_database[best_faq_id]
    return None

def recognize_intent_and_extract_entities(user_query: str) -> Dict:
    """
    Recognizes basic intents and extracts entities using regex.
    """
    user_query_lower = user_query.lower()
    
    # Intent: Track Order
    track_order_match = re.search(r"(track|status of|where is) my order\s*([A-Z0-9]+)", user_query, re.IGNORECASE)
    if track_order_match:
        order_id = track_order_match.group(2).upper()
        return {
            "intent": "track_order",
            "entities": {"order_id": order_id},
            "message": f"Fetching status for order {order_id}..." # Placeholder
        }

    # Intent: General Greeting
    greeting_match = re.search(r"\b(hello|hi|hey|good morning|good afternoon)\b", user_query_lower)
    if greeting_match:
        return {
            "intent": "greeting",
            "entities": {},
            "message": "Hello! How can I help you today?"
        }
        
    # Default/Unknown Intent
    return {
        "intent": "unknown",
        "entities": {},
        "message": "I'm not sure how to help with that. Can you try rephrasing or ask about FAQs, order tracking, or submitting a ticket?"
    }


# --- API Endpoints ---

@app.post("/support/faq", response_model=FAQResponse, tags=["FAQ Support"])
async def get_faq(query: FAQQuery):
    """
    Provides an answer to a frequently asked question based on the user's query.
    """
    faq_item = find_faq_answer(query.query)
    if faq_item:
        return FAQResponse(matched_question=faq_item["question"], answer=faq_item["answer"])
    else:
        return FAQResponse(answer="I'm sorry, I couldn't find an answer related to your query. Please try rephrasing or check our full FAQ page.")

@app.post("/support/ticket", response_model=TicketResponse, status_code=201, tags=["Ticket Support"])
async def submit_ticket(ticket_input: TicketInput):
    """
    Submits a new support ticket.
    The issue description will be analyzed for sentiment.
    """
    ticket_id = str(uuid.uuid4()) # Generate a unique ticket ID
    sentiment = get_sentiment(ticket_input.issue_description)
    
    from datetime import datetime
    timestamp = datetime.utcnow().isoformat() + "Z"

    new_ticket = {
        "ticket_id": ticket_id,
        "user_email": ticket_input.user_email,
        "issue_description": ticket_input.issue_description,
        "status": "submitted",
        "sentiment": sentiment,
        "timestamp": timestamp
    }
    support_tickets_db[ticket_id] = new_ticket
    
    return TicketResponse(**new_ticket)

@app.get("/support/tickets/{ticket_id}", response_model=TicketResponse, tags=["Ticket Support"])
async def get_ticket_status(ticket_id: str):
    """
    Retrieves the details and status of a specific support ticket.
    """
    if ticket_id not in support_tickets_db:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketResponse(**support_tickets_db[ticket_id])


@app.post("/support/action", response_model=ActionResponse, tags=["Intent Actions"])
async def perform_action(query: ActionQuery):
    """
    Recognizes user intent from a query and provides a relevant response or action.
    Currently supports 'track_order' and basic 'greeting'.
    """
    result = recognize_intent_and_extract_entities(query.query)
    
    # Mock action for track_order
    if result["intent"] == "track_order":
        order_id = result["entities"].get("order_id")
        # In a real app, you would query a database here
        result["message"] = f"Mocked: Order {order_id} is currently out for delivery. Estimated arrival: Tomorrow."
        
    return ActionResponse(**result)

# --- To run this API: ---
# 1. Save this code as main.py
# 2. Install dependencies: pip install fastapi uvicorn python-multipart textblob
#    (python-multipart is good to have for FastAPI, though not strictly used for JSON APIs here)
#    (Make sure to install TextBlob corpora: python -m textblob.download_corpora)
# 3. Run Uvicorn server: uvicorn main:app --reload
# 4. Access the interactive API docs at http://127.0.0.1:8000/docs

# Example of how to add a new FAQ:
# faq_database["new_feature_faq"] = {
#     "keywords": ["new feature", "latest update", "how to use x"],
#     "question": "How do I use the new X feature?",
#     "answer": "To use the new X feature, navigate to Y and click Z. More details are in our blog post."
# }
