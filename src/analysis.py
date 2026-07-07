import json
import os
import re
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()

def get_gemini_client():
    global _gemini_client

    if _gemini_client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            _gemini_client = genai.Client(api_key=api_key)

    return _gemini_client