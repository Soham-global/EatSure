import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

print("API KEY FOUND:", bool(os.environ.get("GEMINI_API_KEY")))
print("API KEY VALUE:", os.environ.get("GEMINI_API_KEY")[:10], "...")

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

models = genai.list_models()
print("\nAVAILABLE MODELS:\n")

for m in models:
    print(m.name, "->", m.supported_generation_methods)
