# SMS Spam Classification Backend

## Overview

This is the backend service for an SMS spam classification messaging application. The system uses machine learning models to detect spam messages and integrates with Azure Cognitive Services for processing images (OCR) and audio (speech-to-text) to classify them as spam or not. It leverages Firebase for message handling and provides a RESTful API built with FastAPI.

## Features

- **Text Spam Detection**: Classify text messages as spam or ham using a trained ML model.
- **Image Spam Detection**: Extract text from images using Azure Vision API and classify the extracted text.
- **Audio Spam Detection**: Convert speech to text using Azure Speech Services and classify the transcribed text.
- **Background Processing**: Automated batch processing of messages from Firebase with configurable intervals.
- **Real-time API**: RESTful endpoints for immediate predictions and processor control.
- **Firebase Integration**: Handles message storage and retrieval from Firebase Firestore.

## Project Structure

```
FYP-Backend/
├── notebook                 # Contain Jupyter Notebook file of model with dataset
├── firebase-key.json        # Firebase service account key
├── requirements.txt         # Python dependencies
└── app/
    ├── main.py              # FastAPI application entry point
    ├── ml_model/            # Machine learning model files
    ├── routes/
    │   ├── __init__.py
    │   ├── message_routes.py    # Routes for message handling
    │   ├── prediction_routes.py # Routes for spam predictions
    │   └── processor_routes.py  # Routes for processor control
    └── services/
        ├── firebase_handler.py  # Firebase operations
        ├── ocr_service.py       # Azure Vision API for OCR
        ├── processor.py         # Background message processor
        ├── spam_service.py      # Spam classification logic
        └── speech_service.py    # Azure Speech API for transcription
```

## Technologies Used

- **FastAPI**: Web framework for building APIs
- **Azure Cognitive Services**:
  - Vision API for image-to-text extraction
  - Speech Services for audio-to-text transcription
- **Firebase Admin SDK**: For Firestore database operations
- **Scikit-learn/Joblib**: For ML model loading and prediction (assumed based on joblib in requirements)
- **Python Libraries**: NLTK for text processing, Pandas for data handling, etc.

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory.

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Azure credentials**:
   - Ensure you have Azure subscription and API keys for Vision and Speech services.
   - Set environment variables or configure in the services (e.g., in `ocr_service.py` and `speech_service.py`).

4. **Firebase Setup**:
   - Place your Firebase service account key in `firebase-key.json`.
   - Ensure Firestore is set up and accessible.

5. **ML Model**:
   - Place your trained spam classification model in the `app/ml_model/` directory.

## Usage

### Running the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/docs` for interactive API documentation.

### API Endpoints

#### Prediction Endpoints
- `POST /predict`: Classify a text message.
  - Body: `{"text": "your message here"}`
- `POST /predict-image`: Upload an image and classify extracted text.
- `POST /predict-audio`: Upload an audio file and classify transcribed text.

#### Processor Endpoints
- `POST /processor/start`: Start background message processing.
- `POST /processor/stop`: Stop background processing.
- `GET /processor/status`: Get current processor status.
- `POST /processor/run-now`: Process a batch of messages immediately.

#### Message Endpoints
- `GET /messages/unprocessed`: Retrieve unprocessed messages.
- `POST /messages/test`: Test message handling.

### Background Processing

The processor can be started to continuously check for new messages in Firebase and process them in batches. Configure the interval and batch size when starting.

## Configuration

- Update API keys and endpoints in the service files as needed.
- Adjust ML model path in `spam_service.py`.
- Modify Firebase collection names in `firebase_handler.py` if necessary.


