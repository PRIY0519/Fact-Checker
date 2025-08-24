#!/usr/bin/env python3
"""
Test script for Offline Holy Books Facts Checker
"""

import requests
import json

def test_offline_app():
    """Test the offline application endpoints"""
    base_url = "http://localhost:5001"
    
    print("🧪 Testing Offline Holy Books Facts Checker...")
    
    # Test 1: Home page
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Home page is accessible")
        else:
            print(f"❌ Home page error: {response.status_code}")
    except Exception as e:
        print(f"❌ Home page error: {e}")
        return
    
    # Test 2: History endpoint
    try:
        response = requests.get(f"{base_url}/api/history")
        if response.status_code == 200:
            print("✅ History endpoint is working")
        else:
            print(f"❌ History endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ History endpoint error: {e}")
    
    # Test 3: Fact check endpoint with Bhagavad Gita reference
    try:
        test_claim = "Does Bhagavad Gita 2:47 say that outcomes don't matter?"
        data = {
            "claim": test_claim,
            "language": "en"
        }
        response = requests.post(
            f"{base_url}/api/fact-check",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Fact check endpoint is working")
            print(f"   Verdict: {result.get('verdict', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 'N/A')}%")
            print(f"   Mode: {result.get('mode', 'N/A')}")
            print(f"   Rationale: {result.get('rationale', 'N/A')[:100]}...")
        else:
            print(f"❌ Fact check endpoint error: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Fact check endpoint error: {e}")
    
    # Test 4: Fact check endpoint with Quran reference
    try:
        test_claim = "What does the Quran say about charity?"
        data = {
            "claim": test_claim,
            "language": "en"
        }
        response = requests.post(
            f"{base_url}/api/fact-check",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Quran fact check is working")
            print(f"   Verdict: {result.get('verdict', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 'N/A')}%")
        else:
            print(f"❌ Quran fact check error: {response.status_code}")
    except Exception as e:
        print(f"❌ Quran fact check error: {e}")
    
    print("\n🎉 Offline test completed!")
    print(f"🌐 Open your browser and go to: {base_url}")
    print("💡 Try these claims:")
    print("   - 'Does Bhagavad Gita 2:47 say that outcomes don't matter?'")
    print("   - 'What does the Quran say about charity?'")
    print("   - 'Does the Bible mention peacemakers?'")

if __name__ == "__main__":
    test_offline_app()
