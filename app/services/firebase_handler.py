# app/services/firebase_handler.py
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
        self.chats_collection = "chats"
        self.messages_subcollection = "messages"
    
    def get_unprocessed_messages(self, limit=10):
        """
        Get messages that haven't been processed yet.
        A message is "unprocessed" if:
        - It doesn't have a 'processed' field, OR
        - It has 'processed' field set to False
        """
        try:
            # Get all conversations
            all_conversations = self.db.collection(self.chats_collection).stream()
            unprocessed_messages = []
            
            for conversation in all_conversations:
                conversation_id = conversation.id
                
                # Get ALL messages from this conversation (no filter yet)
                all_messages = self.db.collection(f"{self.chats_collection}/{conversation_id}/{self.messages_subcollection}")\
                                     .limit(limit - len(unprocessed_messages))\
                                     .stream()
                
                for msg in all_messages:
                    data = msg.to_dict()
                    
                    # Check if this message needs processing
                    # It needs processing if: no 'processed' field OR processed == False
                    needs_processing = data.get('processed', False) == False
                    
                    if needs_processing:
                        data['id'] = msg.id
                        data['conversation_id'] = conversation_id
                        unprocessed_messages.append(data)
                        
                        if len(unprocessed_messages) >= limit:
                            break
                
                if len(unprocessed_messages) >= limit:
                    break
            
            return unprocessed_messages
            
        except Exception as e:
            print(f"Error fetching messages: {e}")
            return []
    
    def update_message_status(self, conversation_id, message_id, spam_status, confidence=0.0, extracted_text=None):
        """
        Update message with spam detection result.
        This ADDS the 'processed' and 'spam_status' fields to the message.
        
        NEW: Also saves extracted_text for images and audio messages.
        """
        try:
            # Get reference to the message
            message_ref = self.db.collection(f"{self.chats_collection}/{conversation_id}/{self.messages_subcollection}")\
                                .document(message_id)
            
            # Prepare update data
            update_data = {
                "processed": True,
                "spam_status": spam_status,
                "spam_confidence": confidence,
                "processed_at": datetime.now()
            }
            
            # 🔧 NEW: Add extracted text if provided (for images and audio)
            if extracted_text:
                update_data["extracted_text"] = extracted_text
                update_data["extracted_at"] = datetime.now()
                print(f"   📝 Extracted text saved: {extracted_text[:100]}...")
            
            # Update with new fields
            message_ref.update(update_data)
            print(f"✅ Updated message {message_id} - Spam: {spam_status}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating message {message_id}: {e}")
            return False
    
    def mark_message_as_processed(self, conversation_id, message_id, spam_status, extracted_text=None):
        """
        Simple way to add processed flag to a message that doesn't have it.
        """
        try:
            message_ref = self.db.collection(f"{self.chats_collection}/{conversation_id}/{self.messages_subcollection}")\
                                .document(message_id)
            
            # Prepare update data
            update_data = {
                "processed": True,
                "spam_status": spam_status,
                "processed_at": datetime.now()
            }
            
            # 🔧 NEW: Add extracted text if provided
            if extracted_text:
                update_data["extracted_text"] = extracted_text
                update_data["extracted_at"] = datetime.now()
            
            message_ref.update(update_data)
            print(f"✅ Marked message {message_id} as processed")
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def add_test_message(self, conversation_id, text, sender_number="test_user", msg_type="text"):
        """
        Helper to add test messages (simulates mobile app)
        """
        try:
            doc_ref = self.db.collection(f"{self.chats_collection}/{conversation_id}/{self.messages_subcollection}").document()
            doc_ref.set({
                "content": text,
                "senderNumber": sender_number,
                "timestamp": datetime.now(),
                "type": msg_type
                # Note: NO 'processed' field - this will be treated as unprocessed
            })
            print(f"✅ Test message added to {conversation_id}")
            return doc_ref.id
        except Exception as e:
            print(f"Error adding test message: {e}")
            return None