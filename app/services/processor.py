import time
import threading
import logging
import requests
import os
from app.services.firebase_handler import FirebaseHandler
from app.services.spam_service import predict_spam
from app.services.ocr_service import extract_text_from_image
from app.services.speech_service import speech_to_text
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MessageProcessor:
    def __init__(self):
        self.firebase = FirebaseHandler()
        self.is_running = False
        self.processed_count = 0
        self.error_count = 0
        self.last_run_time = None
        logger.info("MessageProcessor initialized")
    
    def download_file(self, media_url, max_retries=3):
        """Download file from Firebase Storage URL with retries"""
        if not media_url:
            logger.error("No URL provided")
            return None
            
        for attempt in range(max_retries):
            try:
                logger.debug(f"Downloading from URL (attempt {attempt + 1})")
                response = requests.get(media_url, timeout=60)
                
                if response.status_code == 200:
                    logger.debug(f"Download successful: {len(response.content)} bytes")
                    return response.content
                else:
                    logger.warning(f"Download failed with status {response.status_code}")
                    
            except requests.Timeout:
                logger.warning(f"Timeout downloading file (attempt {attempt + 1})")
            except requests.ConnectionError:
                logger.warning(f"Connection error downloading file (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Unexpected download error: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        
        logger.error(f"Failed to download after {max_retries} attempts")
        return None
    
    def process_text_message(self, message_data):
        """Process a text message"""
        try:
            text = message_data.get('content', '') or message_data.get('text', '')
            if not text:
                logger.warning(f"Empty text message: {message_data.get('id')}")
                return None, None  # 🔧 Return tuple (result, extracted_text)
            
            logger.debug(f"Processing text: {text[:50]}...")
            result = predict_spam(text)
            logger.info(f"Text prediction: {result}")
            return result, None  # 🔧 Return result and no extracted text (text is already in content)
            
        except Exception as e:
            logger.error(f"Error processing text message: {e}")
            return None, None
    
    def process_image_message(self, message_data):
        """Process an image message"""
        try:
            logger.info("🖼️ IMAGE MESSAGE DETECTED")
            
            # Look for URL in 'content' (Firebase)
            media_url = message_data.get('content', '')
            logger.info(f"📷 Image URL: {media_url[:100] if media_url else 'NOT FOUND'}...")
            
            if not media_url:
                logger.warning("No media URL found for image message")
                return None, None
            
            # Check if URL is from Firebase Storage
            if 'firebasestorage' in media_url:
                logger.info("✅ Firebase Storage URL detected")
            else:
                logger.warning("⚠️ URL is not from Firebase Storage")
            
            logger.info(f"Downloading image...")
            image_bytes = self.download_file(media_url)
            if not image_bytes:
                logger.error("Failed to download image")
                return None, None
            
            logger.info(f"✅ Image downloaded: {len(image_bytes)} bytes")
            
            # Extract text using OCR
            logger.info("Running OCR on image...")
            extracted_text = extract_text_from_image(image_bytes)
            
            if not extracted_text:
                logger.warning("No text extracted from image")
                return None, None
            
            logger.info(f"✅ OCR extracted: {extracted_text[:100]}...")
            result = predict_spam(extracted_text)
            logger.info(f"🎯 Image spam prediction: {result}")
            
            # 🔧 Return both result AND extracted text
            return result, extracted_text
            
        except Exception as e:
            logger.error(f"Error processing image message: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None, None
    
    def process_audio_message(self, message_data):
        """Process an audio/voice message"""
        try:
            logger.info("🎤 AUDIO/VOICE MESSAGE DETECTED")
            
            # Look for URL in 'content' (Firebase)
            media_url = message_data.get('content', '')
            logger.info(f"🎵 Audio URL: {media_url[:100] if media_url else 'NOT FOUND'}...")
            
            if not media_url:
                logger.warning("No media URL found for audio message")
                return None, None
            
            # Get duration if available
            duration = message_data.get('duration', 'unknown')
            logger.info(f"⏱️ Duration: {duration} seconds")
            
            logger.info(f"Downloading audio...")
            audio_bytes = self.download_file(media_url)
            if not audio_bytes:
                logger.error("Failed to download audio")
                return None, None
            
            logger.info(f"✅ Audio downloaded: {len(audio_bytes)} bytes")
            
            # Convert speech to text
            logger.info("Running speech-to-text on audio...")
            extracted_text = speech_to_text(audio_bytes)
            
            if not extracted_text:
                logger.warning("No text extracted from audio")
                return None, None
            
            logger.info(f"✅ Transcribed: {extracted_text[:100]}...")
            result = predict_spam(extracted_text)
            logger.info(f"🎯 Audio spam prediction: {result}")
            
            # 🔧 Return both result AND extracted text
            return result, extracted_text
            
        except Exception as e:
            logger.error(f"Error processing audio message: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None, None
    
    def process_single_message(self, message_data):
        """Process one message based on its type"""
        message_id = message_data.get('id')
        conversation_id = message_data.get('conversation_id')
        
        # Get the type field
        media_type_raw = message_data.get('type', '')
        logger.info(f"\n{'='*60}")
        logger.info(f"📨 MESSAGE ID: {message_id}")
        logger.info(f"📋 RAW TYPE: '{media_type_raw}'")
        logger.info(f"📋 CONVERSATION ID: {conversation_id}")
        
        # 🔧 Variables to store results
        result = None
        extracted_text = None
        
        # Check if it's an image
        if media_type_raw == 'image':
            logger.info("✅ THIS IS AN IMAGE MESSAGE!")
            result, extracted_text = self.process_image_message(message_data)  # 🔧 Get both
            
        # Check if it's voice/audio
        elif media_type_raw == 'voice':
            logger.info("✅ THIS IS A VOICE MESSAGE!")
            result, extracted_text = self.process_audio_message(message_data)  # 🔧 Get both
            
        # Check if it's text
        elif media_type_raw == 'text':
            logger.info("✅ THIS IS A TEXT MESSAGE!")
            result, extracted_text = self.process_text_message(message_data)  # 🔧 Get both
            
        else:
            logger.warning(f"⚠️ UNKNOWN MESSAGE TYPE: {media_type_raw}")
            logger.info(f"Available fields: {list(message_data.keys())}")
            self.error_count += 1
            return False
        
        # Update Firebase with result AND extracted text
        if result:
            logger.info(f"✅ Spam detection result: {result}")
            if extracted_text:
                logger.info(f"📝 Extracted text will be saved: {extracted_text[:100]}...")
            
            # 🔧 Pass extracted_text to Firebase
            success = self.firebase.update_message_status(
                conversation_id=conversation_id,
                message_id=message_id,
                spam_status=result,
                confidence=0.95,
                extracted_text=extracted_text  # 🔧 This is the key change!
            )
            
            if success:
                self.processed_count += 1
                logger.info(f"✅✅ Message {message_id} successfully processed!")
                if extracted_text:
                    logger.info(f"   📝 Extracted text saved to Firebase ✓")
                return True
            else:
                logger.error(f"Failed to update Firebase for {message_id}")
                self.error_count += 1
                return False
        else:
            logger.warning(f"Could not process message {message_id}")
            self.error_count += 1
            return False
    
    def process_batch(self, batch_size=5):
        """Process a batch of unprocessed messages"""
        self.last_run_time = datetime.now()
        logger.info(f"\n🔍 Checking for new messages...")
        
        try:
            messages = self.firebase.get_unprocessed_messages(limit=batch_size)
            
            if not messages:
                logger.debug("No new messages to process")
                return 0
            
            logger.info(f"📊 Found {len(messages)} new message(s)")
            
            # Log each message's type
            for i, msg in enumerate(messages, 1):
                logger.info(f"  Message {i}: ID={msg.get('id')}, Type={msg.get('type')}")
            
            processed = 0
            for msg in messages:
                if self.process_single_message(msg):
                    processed += 1
            
            logger.info(f"📊 Batch complete: {processed}/{len(messages)} processed")
            return processed
            
        except Exception as e:
            logger.error(f"Error in process_batch: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return 0
    
    def start_continuous_processing(self, interval=10, batch_size=5):
        """Start continuous processing in a background thread"""
        if self.is_running:
            logger.warning("Processor is already running")
            return None
        
        self.is_running = True
        logger.info(f"Starting continuous processor (interval: {interval}s, batch size: {batch_size})")
        
        def run():
            logger.info("Processor thread started")
            while self.is_running:
                try:
                    self.process_batch(batch_size)
                except Exception as e:
                    logger.error(f"Error in processing loop: {e}")
                    self.error_count += 1
                time.sleep(interval)
            logger.info("Processor thread stopped")
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return thread
    
    def stop_processing(self):
        """Stop the continuous processor"""
        self.is_running = False
        logger.info("Stop signal sent to processor")
    
    def get_stats(self):
        """Get processor statistics"""
        return {
            "is_running": self.is_running,
            "processed_count": self.processed_count,
            "error_count": self.error_count,
            "last_run": self.last_run_time.isoformat() if self.last_run_time else None
        }