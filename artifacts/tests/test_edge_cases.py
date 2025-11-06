
import pytest
import sys
import os
from fastapi.testclient import TestClient
from datetime import datetime

# Add the project root directory to Python path to import main
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from main import app

client = TestClient(app)

# --------------------------
# Helper: Valid attachment payload
# --------------------------
def valid_file_attachment_payload(**overrides):
    payload = {
        "conversation_id": 1,
        "original_filename": "requirements.txt",
        "file_type": "txt",
        "file_size": 1024,
        "storage_path": "/files/requirements.txt",
        "extracted_text": "Sample text",
        "status": "uploaded",
        "additional_metadata": "{\"author\": \"QA\"}"
    }
    payload.update(overrides)
    return payload


# ==========================================================================
# Invalid Data Scenarios
# ==========================================================================

@pytest.mark.parametrize("file_size", [-1, 0, 50 * 1024 * 1024 + 1])
def test_create_file_attachment_invalid_file_size(file_size):
    """
    Test POST /file-attachments/ with invalid file_size
    (negative, zero, exceeding 50MB limit) returns 422 Unprocessable Entity.
    """
    payload = valid_file_attachment_payload(file_size=file_size)
    response = client.post("/file-attachments/", json=payload)
    assert response.status_code == 422
    # Pydantic validation error structure
    assert "file_size" in str(response.json()).lower()


@pytest.mark.parametrize("conversation_id", [-42, 0])
def test_create_file_attachment_invalid_conversation_id(conversation_id):
    """
    Test POST /file-attachments/ with invalid conversation_id
    (negative, zero) returns 422 Unprocessable Entity.
    """
    payload = valid_file_attachment_payload(conversation_id=conversation_id)
    response = client.post("/file-attachments/", json=payload)
    assert response.status_code == 422
    assert "conversation_id" in str(response.json()).lower()


def test_create_file_attachment_invalid_file_type():
    """
    Test POST /file-attachments/ with unsupported file_type returns 422.
    """
    payload = valid_file_attachment_payload(file_type="pdf")
    response = client.post("/file-attachments/", json=payload)
    assert response.status_code == 422
    # enum validation error
    assert "file_type" in str(response.json()).lower()
    assert "value is not a valid enumeration" in str(response.json()).lower() or "file_type" in str(response.json()).lower()


def test_create_file_attachment_missing_required_fields():
    """
    Test POST /file-attachments/ with missing required fields returns 422.
    """
    payload = {}  # Empty payload
    response = client.post("/file-attachments/", json=payload)
    assert response.status_code == 422
    # Should mention missing required fields
    body = response.json()
    required_fields = ["conversation_id", "original_filename", "file_type", "file_size", "storage_path"]
    for field in required_fields:
        assert any(field in str(err["loc"]) for err in body["detail"])


@pytest.mark.parametrize("original_filename", ["", None])
def test_create_file_attachment_empty_or_null_original_filename(original_filename):
    """
    Test POST /file-attachments/ with empty or null original_filename returns 422.
    """
    payload = valid_file_attachment_payload(original_filename=original_filename)
    response = client.post("/file-attachments/", json=payload)
    assert response.status_code == 422
    # Pydantic error for min_length or missing field
    assert "original_filename" in str(response.json()).lower()


# ==========================================================================
# Non-existent Resource Scenarios
# ==========================================================================

@pytest.mark.parametrize("method, endpoint", [
    ("get", "/file-attachments/999999"),
    ("put", "/file-attachments/999999"),
    ("patch", "/file-attachments/999999"),
    ("delete", "/file-attachments/999999"),
])
def test_resource_not_found(method, endpoint):
    """
    Test GET/PUT/PATCH/DELETE /file-attachments/{non_existent_id} returns 404.
    """
    # For PUT and PATCH, must supply a valid body
    if method == "put":
        response = client.put(endpoint, json=valid_file_attachment_payload())
    elif method == "patch":
        response = client.patch(endpoint, json={"original_filename": "newfile.txt"})
    elif method == "delete":
        response = client.delete(endpoint)
    else:
        response = client.get(endpoint)

    assert response.status_code == 404
    body = response.json()
    assert body.get("detail") is not None
    assert "not found" in body["detail"].lower()


# ==========================================================================
# Invalid ID Scenarios
# ==========================================================================

@pytest.mark.parametrize("file_id", [-1, 0])
@pytest.mark.parametrize("method", ["get", "put", "patch", "delete"])
def test_invalid_file_id_returns_400(file_id, method):
    """
    Test GET/PUT/PATCH/DELETE /file-attachments/{file_id}
    with negative or zero file_id returns 400 Bad Request.
    """
    endpoint = f"/file-attachments/{file_id}"
    if method == "get":
        response = client.get(endpoint)
    elif method == "put":
        response = client.put(endpoint, json=valid_file_attachment_payload())
    elif method == "patch":
        response = client.patch(endpoint, json={"original_filename": "update.txt"})
    elif method == "delete":
        response = client.delete(endpoint)
    else:
        pytest.fail("Unknown method")

    assert response.status_code == 400
    body = response.json()
    assert "file id must be a positive integer" in body.get("detail", "").lower()


# ==========================================================================
# Empty Update Scenario
# ==========================================================================

def test_patch_file_attachment_empty_body_returns_400():
    """
    Test PATCH /file-attachments/{id} with empty request body returns 400.
    """
    # First, create a valid record to patch
    create_resp = client.post("/file-attachments/", json=valid_file_attachment_payload())
    assert create_resp.status_code == 201
    file_id = create_resp.json()["id"]

    # Send PATCH with empty body
    response = client.patch(f"/file-attachments/{file_id}", json={})
    assert response.status_code == 400
    body = response.json()
    assert "no fields provided for update" in body.get("detail", "").lower()