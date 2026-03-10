import os
from dotenv import load_dotenv
from pathlib import Path

print(f"Current working directory: {Path.cwd()}")
print(f".env exists: {(Path.cwd() / '.env').exists()}")

load_dotenv()  # Load from current directory

print(f"AZURE_OCR_KEY: {os.getenv('AZURE_OCR_KEY')}")
print(f"AZURE_OCR_ENDPOINT: {os.getenv('AZURE_OCR_ENDPOINT')}")