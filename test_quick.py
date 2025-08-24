#!/usr/bin/env python3
"""
Quick test script for Holy Books Facts Checker
"""

import requests
import json

def test_app():
    """Test the application endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Holy Books Facts Checker...")
    
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
    
    # Test 3: Fact check endpoint
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
        else:
            print(f"❌ Fact check endpoint error: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Fact check endpoint error: {e}")
    
    print("\n🎉 Test completed!")
    print(f"🌐 Open your browser and go to: {base_url}")

if __name__ == "__main__":
    test_app()
