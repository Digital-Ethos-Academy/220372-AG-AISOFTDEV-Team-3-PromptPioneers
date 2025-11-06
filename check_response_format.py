#!/usr/bin/env python3
"""
Quick test to check the actual response format
"""

import requests
import json

try:
    response = requests.post(
        'http://localhost:8000/api/process-prd',
        json={'user_input': 'I want to build a simple note-taking app'},
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ RAG API Success!")
        print("\n📊 Response Structure:")
        prd_content = data['prd_content']
        
        for field, value in prd_content.items():
            print(f"\n{field}:")
            print(f"  Type: {type(value)}")
            if isinstance(value, list):
                print(f"  Items: {len(value)}")
                print(f"  Sample: {value[0] if value else 'empty'}")
            else:
                print(f"  Content: {value[:100]}...")
                
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")