#!/usr/bin/env python3
"""
Test script to verify the backend is working
"""

import requests
import json

def test_backend():
    """Test the backend endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing Backend Endpoints")
    print("=" * 40)
    
    # Test 1: Health check
    print("1️⃣ Testing /test endpoint...")
    try:
        response = requests.get(f"{base_url}/test", timeout=5)
        if response.status_code == 200:
            print("✅ /test endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ /test endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ /test endpoint error: {e}")
    
    # Test 2: Health check
    print("\n2️⃣ Testing /healthz endpoint...")
    try:
        response = requests.get(f"{base_url}/healthz", timeout=5)
        if response.status_code == 200:
            print("✅ /healthz endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ /healthz endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ /healthz endpoint error: {e}")
    
    # Test 3: Get tickets
    print("\n3️⃣ Testing /tickets endpoint...")
    try:
        response = requests.get(f"{base_url}/tickets", timeout=5)
        if response.status_code == 200:
            print("✅ /tickets endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ /tickets endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ /tickets endpoint error: {e}")
    
    # Test 4: Create ticket
    print("\n4️⃣ Testing /ticket endpoint...")
    try:
        test_ticket = {
            "name": "Test User",
            "department": "Test Dept",
            "issue_type": "Test Issue",
            "description": "This is a test ticket",
            "priority": "Medium"
        }
        response = requests.post(f"{base_url}/ticket", json=test_ticket, timeout=5)
        if response.status_code == 200:
            print("✅ /ticket endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ /ticket endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ /ticket endpoint error: {e}")

if __name__ == "__main__":
    test_backend()
