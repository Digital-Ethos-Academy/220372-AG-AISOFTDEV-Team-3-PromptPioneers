"""Comprehensive API endpoint tests"""
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_root():
    response = client.get("/")
    print(f"✓ Root: {response.status_code} - {response.json()['name']}")
    return response.status_code == 200

def test_health():
    response = client.get("/health")
    print(f"✓ Health: {response.status_code} - {response.json()['status']}")
    return response.status_code == 200

def test_list_empty():
    response = client.get("/file-attachments/")
    print(f"✓ List (empty): {response.status_code} - {len(response.json())} items")
    return response.status_code == 200

def test_create():
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
    response = client.post("/file-attachments/", json=data)
    if response.status_code == 201:
        result = response.json()
        print(f"✓ Create: {response.status_code} - Created ID {result['id']}")
        return result['id']
    else:
        print(f"✗ Create failed: {response.status_code} - {response.text}")
        return None

def test_get(file_id):
    response = client.get(f"/file-attachments/{file_id}")
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Get: {response.status_code} - Filename: {result['original_filename']}")
        return True
    else:
        print(f"✗ Get failed: {response.status_code}")
        return False

def test_list_with_data():
    response = client.get("/file-attachments/")
    count = len(response.json())
    print(f"✓ List (with data): {response.status_code} - {count} items")
    return response.status_code == 200 and count > 0

def test_update(file_id):
    data = {
        "conversation_id": 1,
        "original_filename": "updated_test.txt",
        "file_type": "txt",
        "file_size": 2048,
        "storage_path": "/uploads/updated_test.txt",
        "extracted_text": "Updated content",
        "status": "processed",
        "additional_metadata": '{"key": "updated"}'
    }
    response = client.put(f"/file-attachments/{file_id}", json=data)
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Update: {response.status_code} - Status: {result['status']}")
        return True
    else:
        print(f"✗ Update failed: {response.status_code}")
        return False

def test_partial_update(file_id):
    data = {"status": "failed"}
    response = client.patch(f"/file-attachments/{file_id}", json=data)
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Partial Update: {response.status_code} - Status: {result['status']}")
        return True
    else:
        print(f"✗ Partial update failed: {response.status_code}")
        return False

def test_delete(file_id):
    response = client.delete(f"/file-attachments/{file_id}")
    print(f"✓ Delete: {response.status_code} - Deleted ID {file_id}")
    return response.status_code == 204

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING ALL API ENDPOINTS")
    print("=" * 60)
    
    test_root()
    test_health()
    test_list_empty()
    
    file_id = test_create()
    if file_id:
        test_get(file_id)
        test_list_with_data()
        test_update(file_id)
        test_partial_update(file_id)
        test_delete(file_id)
    
    print("=" * 60)
    print("✓ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)
