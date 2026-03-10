from fastapi import APIRouter, BackgroundTasks
from app.services.firebase_handler import FirebaseHandler
from app.services.processor import MessageProcessor

# Create router for processor endpoints
router = APIRouter(prefix="/processor", tags=["Processor Control"])

# Initialize services
fb_handler = FirebaseHandler()
msg_processor = MessageProcessor()
processor_thread = None

@router.post("/start")
def start_processor(interval: int = 10, batch_size: int = 5):
    """Start the background message processor"""
    global processor_thread
    
    if msg_processor.is_running:
        return {"message": "Processor is already running"}
    
    processor_thread = msg_processor.start_continuous_processing(
        interval=interval, 
        batch_size=batch_size
    )
    return {
        "message": "Processor started",
        "interval": interval,
        "batch_size": batch_size
    }

@router.post("/stop")
def stop_processor():
    """Stop the background message processor"""
    if not msg_processor.is_running:
        return {"message": "Processor is not running"}
    
    msg_processor.stop_processing()
    return {"message": "Processor stopped"}

@router.get("/status")
def processor_status():
    """Get processor status"""
    return {
        "is_running": msg_processor.is_running,
        "processed_count": msg_processor.processed_count
    }

@router.post("/run-now")
def run_processor_now(batch_size: int = 5):
    """Run one batch immediately"""
    processed = msg_processor.process_batch(batch_size=batch_size)
    return {
        "message": f"Processed {processed} messages",
        "processed_count": msg_processor.processed_count
    }