from fastapi import FastAPI
from app.routes import prediction_routes, processor_routes, message_routes

# Create FastAPI app
app = FastAPI(
    title="Spam Detection API",
    description="API for detecting spam in messages, images, and audio",
    version="1.0.0"
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