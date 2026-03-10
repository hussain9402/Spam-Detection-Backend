from fastapi import APIRouter
from app.services.firebase_handler import FirebaseHandler

# Create router for message management endpoints
router = APIRouter(prefix="/messages", tags=["Message Management"])

fb_handler = FirebaseHandler()

@router.get("/unprocessed")
def get_unprocessed_messages(limit: int = 10):
    """View unprocessed messages in Firebase"""
    messages = fb_handler.get_unprocessed_messages(limit=limit)
    return {
        "count": len(messages),
        "messages": messages
    }

@router.post("/test")
def add_test_message(text: str, user_id: str = "test_user"):
    """Add a test message to Firebase"""
    msg_id = fb_handler.add_test_message(text, user_id)
    return {
        "message": "Test message added",
        "message_id": msg_id,
        "text": text
    }

