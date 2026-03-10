from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime
from pathlib import Path

# Go up one level from services folder to reach root where firebase-key.json is
cred_path = Path(__file__).parent.parent.parent / "firebase-key.json"
cred = credentials.Certificate(str(cred_path))
initialize_app(cred)
db = firestore.client()

class FirebaseHandler:
    def __init__(self):
        self.db = db
        self.messages_collection = "messages"
    
    def get_unprocessed_messages(self, limit=10):
        """Get messages that haven't been processed yet"""
        try:
            messages = self.db.collection(self.messages_collection)\
                             .where("processed", "==", False)\
                             .limit(limit)\
                             .stream()
            
            result = []
            for msg in messages:
                data = msg.to_dict()
                data['id'] = msg.id  # Add the document ID
                result.append(data)
            
            return result
        except Exception as e:
            print(f"Error fetching messages: {e}")
            return []
    
    def update_message_status(self, message_id, spam_status, confidence=0.0):
        """Update message with spam detection result"""
        try:
            self.db.collection(self.messages_collection)\
                   .document(message_id)\
                   .update({
                       "processed": True,
                       "spam_status": spam_status,
                       "processed_at": datetime.now()
                   })
            return True
        except Exception as e:
            print(f"Error updating message {message_id}: {e}")
            return False
    
    def add_test_message(self, text, user_id="test_user"):
        """Helper to add test messages"""
        try:
            doc_ref = self.db.collection(self.messages_collection).document()
            doc_ref.set({
                "user_id": user_id,
                "text": text,
                "media_type": "text",
                "timestamp": datetime.now(),
                "processed": False,
                "spam_status": None
            })
            return doc_ref.id
        except Exception as e:
            print(f"Error adding test message: {e}")
            return None