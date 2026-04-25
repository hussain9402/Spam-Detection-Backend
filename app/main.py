from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import prediction_routes, processor_routes, message_routes
from app.services.processor import MessageProcessor

# Create processor instance (this will auto-start)
message_processor = MessageProcessor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """This runs when server starts and stops"""
    # STARTUP - Auto-start the processor
    print("=" * 50)
    print("🚀 Starting Spam Detection Backend")
    print("=" * 50)
    print("🔄 Auto-starting message processor...")
    message_processor.start_continuous_processing(interval=10, batch_size=5)
    print("✅ Message processor is running in background")
    print("=" * 50)
    
    yield  # Server runs here
    
    # SHUTDOWN - Stop the processor
    print("\n🛑 Shutting down server...")
    message_processor.stop_processing()
    print("✅ Message processor stopped")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Spam Detection API",
    description="API for detecting spam in messages, images, and audio",
    version="1.0.0",
    lifespan=lifespan  # ← THIS IS THE KEY CHANGE
)

# Include all routers
app.include_router(prediction_routes.router)
app.include_router(processor_routes.router)
app.include_router(message_routes.router)

# Optional: Add a root endpoint to show available routes
@app.get("/")
async def root():
    return {
        "message": "Spam Detection API",
        "docs": "/docs",
        "auto_processor_running": message_processor.is_running,  # ← ADD THIS
        "endpoints": [
            "/predict",
            "/predict-image", 
            "/predict-audio",
            "/processor/start",
            "/processor/stop", 
            "/processor/status",
            "/processor/run-now",
            "/messages/unprocessed",
            "/messages/test"
        ]
    }