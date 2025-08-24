#!/usr/bin/env python3
"""
Test script to verify API connections for accurate fact-checking responses
"""
import os
import openai
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai_connection():
    """Test OpenAI API connection"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("OpenAI API key not configured")
        return False
    
    try:
        openai.api_key = api_key
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, this is a test."}],
            max_tokens=10
        )
        print("OpenAI API connection successful")
        return True
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return False

def test_gemini_connection():
    """Test Google Gemini API connection"""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("Google Gemini API key not configured")
        return False
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Hello, this is a test.")
        print("Google Gemini API connection successful")
        return True
    except Exception as e:
        print(f"Google Gemini API error: {e}")
        return False

def main():
    print("Testing API connections for accurate fact-checking...\n")
    
    openai_ok = test_openai_connection()
    gemini_ok = test_gemini_connection()
    
    print("\nAPI Status Summary:")
    print(f"OpenAI (Primary): {'Ready' if openai_ok else 'Needs setup'}")
    print(f"Gemini (Fallback): {'Ready' if gemini_ok else 'Needs setup'}")
    
    if openai_ok and gemini_ok:
        print("\nAll APIs configured! Your app will provide the most accurate responses.")
    elif gemini_ok:
        print("\nOnly Gemini is configured. Add OpenAI API key for best accuracy.")
    elif openai_ok:
        print("\nOnly OpenAI is configured. Gemini is available as fallback.")
    else:
        print("\nNo APIs configured. Please add API keys to .env file.")
    
    print("\nTo get OpenAI API key: https://platform.openai.com/api-keys")
    print("To get Gemini API key: https://makersuite.google.com/app/apikey")

if __name__ == "__main__":
    main()
