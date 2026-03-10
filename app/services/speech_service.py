import azure.cognitiveservices.speech as speechsdk
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Replace with your values
SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

# env_path = Path(__file__).parent.parent .parent/ ".env"


def speech_to_text(audio_bytes):
    speech_config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )
    
    # Save temp audio file
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_bytes)
    
    audio_config = speechsdk.audio.AudioConfig(filename="temp_audio.wav")
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config
    )
    
    result = recognizer.recognize_once()
    
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    else:
        return ""