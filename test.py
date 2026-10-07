# Tahap 1: cek koneksi ke Gemini sebelum membuat UI
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Sebutkan 3 makanan khas Banjarmasin dalam satu kalimat.",
)
print(response.text)