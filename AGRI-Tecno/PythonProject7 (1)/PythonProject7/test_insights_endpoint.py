#!/usr/bin/env python
"""
Test script for the new /crop-insights endpoint
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Test data
test_payload = {
    "crop": "Rice",
    "soil_image_confidence": 0.85,
    "farm_size_acres": 2.5,
    "latitude": 27.1767,  # Example: Lucknow, India
    "longitude": 78.0081,
    "sowing_date": "2024-12-10",
    "season": "Rabi",
}

print("Testing /crop-insights endpoint...")
print("=" * 60)
print(f"Request payload: {json.dumps(test_payload, indent=2)}")
print("=" * 60)

try:
    response = requests.post(
        f"{BASE_URL}/crop-insights",
        data=test_payload,
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    print("=" * 60)
    
    if response.status_code == 200:
        result = response.json()
        print("✓ SUCCESS! Response received:")
        print(json.dumps(result, indent=2)[:2000])  # Print first 2000 chars
        print("\n... (truncated)")
    else:
        print(f"✗ Error: {response.text}")

except requests.exceptions.ConnectionError:
    print("✗ Connection error. Is the backend running at http://localhost:8000?")
except Exception as e:
    print(f"✗ Error: {e}")
