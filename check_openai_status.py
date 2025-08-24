#!/usr/bin/env python3
"""
Check OpenAI API status and quota
"""

import os
import openai
from dotenv import load_dotenv

def check_openai_status():
    """Check OpenAI API key and quota status"""
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ No OpenAI API key found in .env file")
        print("Please add your OpenAI API key to the .env file:")
        print("OPENAI_API_KEY=your_api_key_here")
        return
    
    print("✅ OpenAI API key found")
    
    # Test API connection
    try:
        # Set the API key
        openai.api_key = api_key
        
        # Try a simple API call
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        print("✅ OpenAI API is working")
        print(f"Response: {response.choices[0].message.content}")
        
    except Exception as e:
        error_str = str(e)
        
        if "quota" in error_str.lower() or "429" in error_str:
            print("❌ OpenAI API quota exceeded")
            print("Please check your billing status at: https://platform.openai.com/account/billing")
            print("You may need to:")
            print("1. Add payment method")
            print("2. Upgrade your plan")
            print("3. Wait for quota reset")
        elif "invalid" in error_str.lower() or "401" in error_str:
            print("❌ Invalid OpenAI API key")
            print("Please check your API key at: https://platform.openai.com/api-keys")
        else:
            print(f"❌ OpenAI API error: {e}")
            print("Please check your internet connection and try again")

if __name__ == "__main__":
    check_openai_status()
