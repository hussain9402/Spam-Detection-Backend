from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

KEY = os.getenv("AZURE_OCR_KEY")
ENDPOINT = os.getenv("AZURE_OCR_ENDPOINT")

# env_path = Path(__file__).parent.parent.parent / ".env"


client = ImageAnalysisClient(
    endpoint=ENDPOINT,
    credential=AzureKeyCredential(KEY)
)

def extract_text_from_image(image_bytes):
    result = client.analyze(
        image_data=image_bytes,
        visual_features=["read"]
    )
    
    text = ""
    for line in result.read.blocks[0].lines:
        text += line.text + " "
    
    return text