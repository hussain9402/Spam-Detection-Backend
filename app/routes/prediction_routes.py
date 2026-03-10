from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from app.services.spam_service import predict_spam
from app.services.ocr_service import extract_text_from_image
from app.services.speech_service import speech_to_text

# Create router for prediction endpoints
router = APIRouter(prefix="", tags=["Prediction APIs"])

class Message(BaseModel):
    text: str

@router.get("/")
def home():
    return {"message": "SMS Spam Classifier API is running"}

@router.post("/predict")
def predict(message: Message):
    result = predict_spam(message.text)
    return {"prediction": result}

@router.post("/predict-image")
async def predict_image(file: UploadFile = File(...)):
    contents = await file.read()
    extracted_text = extract_text_from_image(contents)
    result = predict_spam(extracted_text)
    return {
        "filename": file.filename,
        "extracted_text": extracted_text,
        "prediction": result
    }

@router.post("/predict-audio")
async def predict_audio(file: UploadFile = File(...)):
    contents = await file.read()
    extracted_text = speech_to_text(contents)
    result = predict_spam(extracted_text)
    return {
        "filename": file.filename,
        "extracted_text": extracted_text,
        "prediction": result
    }