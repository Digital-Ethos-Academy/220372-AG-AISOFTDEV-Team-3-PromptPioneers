"""
Quick test script to diagnose API endpoint issues
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_root():
    """Test root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Root endpoint status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing root: {e}")
        return False

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"\nHealth endpoint status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing health: {e}")
        return False

def test_list_attachments():
    """Test list file attachments endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/file-attachments/")
        print(f"\nList attachments status: {response.status_code}")
        if response.status_code == 500:
            print(f"Error response: {response.text}")
        else:
            print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing list: {e}")
        return False

def test_create_attachment():
    """Test creating a file attachment"""
    try:
        data = {
            "conversation_id": 1,
            "original_filename": "test.txt",
            "file_type": "txt",
            "file_size": 1024,
            "storage_path": "/uploads/test.txt",
            "extracted_text": "Test content",
            "status": "uploaded",
            "additional_metadata": '{"key": "value"}'
        }
        response = requests.post(f"{BASE_URL}/file-attachments/", json=data)
        print(f"\nCreate attachment status: {response.status_code}")
        if response.status_code == 500:
            print(f"Error response: {response.text}")
        else:
            print(f"Response: {response.json()}")
        return response.status_code == 201
    except Exception as e:
        print(f"Error testing create: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("API ENDPOINT TESTING")
    print("=" * 60)
    
    results = []
    results.append(("Root", test_root()))
    results.append(("Health", test_health()))
    results.append(("List", test_list_attachments()))
    results.append(("Create", test_create_attachment()))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:20} {status}")
    print("=" * 60)
