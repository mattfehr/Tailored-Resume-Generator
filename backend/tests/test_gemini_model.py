import os
import sys
import google.generativeai as genai

# Add parent directory (backend/) to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.config import Config

# Configure Gemini API
genai.configure(api_key=Config.GEMINI_API_KEY)

def main():
    print("\nChecking available Gemini models...\n")
    try:
        models = list(genai.list_models())
        if not models:
            print("No models found. Check your API key or permissions.")
            return
        for model in models:
            print(f"{model.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    main()
