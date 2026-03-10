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
        for attempt in range(max_retries):
            try:
                logger.debug(f"Downloading from {media_url} (attempt {attempt + 1})")
                response = requests.get(media_url, timeout=30)
                
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
            
            # Wait before retrying
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
        
        logger.error(f"Failed to download after {max_retries} attempts")
        return None
    
    def process_text_message(self, message_data):
        """Process a text message"""
        try:
            text = message_data.get('text', '')
            if not text:
                logger.warning(f"Empty text message: {message_data.get('id')}")
                return None
            
            logger.debug(f"Processing text: {text[:50]}...")
            result = predict_spam(text)
            logger.info(f"Text prediction: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing text message: {e}")
            return None
    
    def process_image_message(self, message_data):
        """Process an image message"""
        try:
            media_url = message_data.get('media_url')
            if not media_url:
                logger.warning("No media URL found for image message")
                return None
            
            # Download image
            logger.info(f"Downloading image from {media_url}")
            image_bytes = self.download_file(media_url)
            if not image_bytes:
                logger.error("Failed to download image")
                return None
            
            # Extract text using OCR
            logger.info("Running OCR on image")
            extracted_text = extract_text_from_image(image_bytes)
            
            if not extracted_text:
                logger.warning("No text extracted from image")
                return None
            
            logger.info(f"OCR extracted: {extracted_text[:100]}...")
            
            # Detect spam
            result = predict_spam(extracted_text)
            logger.info(f"Image spam prediction: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing image message: {e}")
            return None
    
    def process_audio_message(self, message_data):
        """Process an audio message"""
        try:
            media_url = message_data.get('media_url')
            if not media_url:
                logger.warning("No media URL found for audio message")
                return None
            
            # Download audio
            logger.info(f"Downloading audio from {media_url}")
            audio_bytes = self.download_file(media_url)
            if not audio_bytes:
                logger.error("Failed to download audio")
                return None
            
            # Convert speech to text
            logger.info("Running speech-to-text on audio")
            extracted_text = speech_to_text(audio_bytes)
            
            if not extracted_text:
                logger.warning("No text extracted from audio")
                return None
            
            logger.info(f"Transcribed: {extracted_text[:100]}...")
            
            # Detect spam
            result = predict_spam(extracted_text)
            logger.info(f"Audio spam prediction: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing audio message: {e}")
            return None
    
    def process_single_message(self, message_data):
        """Process one message based on its type"""
        message_id = message_data.get('id')
        media_type = message_data.get('media_type', 'text')
        user_id = message_data.get('user_id', 'unknown')
        
        logger.info(f"Processing message {message_id} (user: {user_id}, type: {media_type})")
        
        try:
            # Route to appropriate handler
            if media_type == 'text':
                result = self.process_text_message(message_data)
            elif media_type == 'image':
                result = self.process_image_message(message_data)
            elif media_type == 'audio':
                result = self.process_audio_message(message_data)
            else:
                logger.error(f"Unknown media type: {media_type}")
                self.error_count += 1
                return False
            
            if result:
                # Update Firebase with the result
                success = self.firebase.update_message_status(message_id, result)
                
                if success:
                    self.processed_count += 1
                    logger.info(f"✅ Message {message_id} marked as {result}")
                    return True
                else:
                    logger.error(f"Failed to update Firebase for {message_id}")
                    self.error_count += 1
                    return False
            else:
                logger.warning(f"Could not extract/predict for {message_id}")
                self.error_count += 1
                return False
                
        except Exception as e:
            logger.error(f"Unexpected error processing {message_id}: {e}")
            self.error_count += 1
            return False
    
    def process_batch(self, batch_size=5):
        """Process a batch of unprocessed messages"""
        self.last_run_time = datetime.now()
        logger.info(f"Checking for new messages (batch size: {batch_size})")
        
        try:
            # Get unprocessed messages
            messages = self.firebase.get_unprocessed_messages(limit=batch_size)
            
            if not messages:
                logger.debug("No new messages to process")
                return 0
            
            logger.info(f"Found {len(messages)} new messages")
            
            # Process each message
            processed = 0
            for msg in messages:
                if self.process_single_message(msg):
                    processed += 1
            
            logger.info(f"Batch complete: {processed}/{len(messages)} processed successfully")
            return processed
            
        except Exception as e:
            logger.error(f"Error in process_batch: {e}")
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
                
                # Wait before next check
                time.sleep(interval)
            
            logger.info("Processor thread stopped")
        
        # Start in background thread
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