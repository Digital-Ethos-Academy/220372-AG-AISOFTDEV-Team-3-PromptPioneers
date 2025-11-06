"""
Pytest Test Suite for File Attachment CRUD Endpoints

This suite contains happy path tests for the main CRUD operations
of the AI-Powered Requirement Analyzer's file attachment API.

Requirements:
- Tests are independent and self-contained.
- Each test uses realistic data and validates status codes & response content.
"""

import pytest
import sys
import os
from fastapi.testclient import TestClient
from datetime import datetime

# Add the project root directory to Python path to import main
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from main import app

client = TestClient(app)

# --------------------------------------------------------------------------
# Helper: Default payload for file attachments
# --------------------------------------------------------------------------

def get_file_attachment_payload(
    conversation_id=1,
    original_filename="requirements.docx",
    file_type="docx",
    file_size=12345,
    storage_path="/storage/reqs/requirements.docx",
    extracted_text="Extracted requirement text.",
    status="uploaded",
    additional_metadata='{"author": "Alice"}'
):
    return {
        "conversation_id": conversation_id,
        "original_filename": original_filename,
        "file_type": file_type,
        "file_size": file_size,
        "storage_path": storage_path,
        "extracted_text": extracted_text,
        "status": status,
        "additional_metadata": additional_metadata,
    }

# --------------------------------------------------------------------------
# Test: POST /file-attachments/
# --------------------------------------------------------------------------

def test_create_file_attachment():
    """
    Test successful creation of a file attachment.
    Asserts 201 status and verifies response data.
    """
    payload = get_file_attachment_payload()
    response = client.post("/file-attachments/", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()

    # Check that response fields match input and system-generated fields exist
    assert data["id"] > 0
    assert data["conversation_id"] == payload["conversation_id"]
    assert data["original_filename"] == payload["original_filename"]
    assert data["file_type"] == payload["file_type"]
    assert data["file_size"] == payload["file_size"]
    assert data["storage_path"] == payload["storage_path"]
    assert data["extracted_text"] == payload["extracted_text"]
    assert data["status"] == payload["status"]
    assert data["additional_metadata"] == payload["additional_metadata"]
    assert "created_at" in data
    assert "updated_at" in data
    # Check date format
    datetime.fromisoformat(data["created_at"])
    datetime.fromisoformat(data["updated_at"])

# --------------------------------------------------------------------------
# Test: GET /file-attachments/
# --------------------------------------------------------------------------

def test_list_file_attachments():
    """
    Test successful retrieval of all file attachments.
    Asserts 200 status and verifies response structure.
    """
    # Create at least one file attachment to ensure results
    payload = get_file_attachment_payload(original_filename="overview.md", file_type="md")
    create_resp = client.post("/file-attachments/", json=payload)
    assert create_resp.status_code == 201
    created_id = create_resp.json()["id"]

    response = client.get("/file-attachments/")
    assert response.status_code == 200, response.text
    attachments = response.json()
    assert isinstance(attachments, list)
    # At least one item should match the one we just created
    found = False
    for item in attachments:
        assert "id" in item
        assert "conversation_id" in item
        assert "original_filename" in item
        assert "file_type" in item
        assert "file_size" in item
        assert "storage_path" in item
        assert "extracted_text" in item
        assert "status" in item
        assert "additional_metadata" in item
        assert "created_at" in item
        assert "updated_at" in item
        if item["id"] == created_id:
            found = True
            assert item["original_filename"] == payload["original_filename"]
            assert item["file_type"] == payload["file_type"]
    assert found, "Created item not found in GET /file-attachments/ list"

# --------------------------------------------------------------------------
# Test: GET /file-attachments/{id}
# --------------------------------------------------------------------------

def test_get_file_attachment_by_id():
    """
    Test successful retrieval of a specific file attachment.
    Asserts 200 status and verifies response data.
    """
    payload = get_file_attachment_payload(original_filename="single.txt", file_type="txt")
    create_resp = client.post("/file-attachments/", json=payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    file_id = created["id"]

    response = client.get(f"/file-attachments/{file_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == file_id
    assert data["original_filename"] == payload["original_filename"]
    assert data["file_type"] == payload["file_type"]
    assert data["file_size"] == payload["file_size"]
    assert data["conversation_id"] == payload["conversation_id"]
    assert "created_at" in data
    assert "updated_at" in data

# --------------------------------------------------------------------------
# Test: PUT /file-attachments/{id}
# --------------------------------------------------------------------------

def test_update_file_attachment_put():
    """
    Test successful full update of a file attachment (PUT).
    Asserts 200 status and verifies updated data.
    """
    # Create original record
    payload = get_file_attachment_payload(original_filename="put_test.md", file_type="md")
    create_resp = client.post("/file-attachments/", json=payload)
    assert create_resp.status_code == 201
    file_id = create_resp.json()["id"]

    # Prepare new data for full update
    updated_payload = get_file_attachment_payload(
        conversation_id=2,
        original_filename="requirements_v2.docx",
        file_type="docx",
        file_size=54321,
        storage_path="/storage/reqs/requirements_v2.docx",
        extracted_text="Updated extracted text.",
        status="processed",
        additional_metadata='{"author": "Bob"}',
    )
    resp = client.put(f"/file-attachments/{file_id}", json=updated_payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["id"] == file_id
    assert data["conversation_id"] == updated_payload["conversation_id"]
    assert data["original_filename"] == updated_payload["original_filename"]
    assert data["file_type"] == updated_payload["file_type"]
    assert data["file_size"] == updated_payload["file_size"]
    assert data["storage_path"] == updated_payload["storage_path"]
    assert data["extracted_text"] == updated_payload["extracted_text"]
    assert data["status"] == updated_payload["status"]
    assert data["additional_metadata"] == updated_payload["additional_metadata"]

# --------------------------------------------------------------------------
# Test: PATCH /file-attachments/{id}
# --------------------------------------------------------------------------

def test_partial_update_file_attachment_patch():
    """
    Test successful partial update of a file attachment (PATCH).
    Asserts 200 status and verifies only updated fields change.
    """
    # Create original
    payload = get_file_attachment_payload(original_filename="patch_test.txt", file_type="txt")
    create_resp = client.post("/file-attachments/", json=payload)
    assert create_resp.status_code == 201
    orig = create_resp.json()
    file_id = orig["id"]

    # Only update status and additional_metadata
    patch_data = {
        "status": "processing",
        "additional_metadata": '{"reviewed": true}'
    }
    resp = client.patch(f"/file-attachments/{file_id}", json=patch_data)
    assert resp.status_code == 200, resp.text
    updated = resp.json()
    # Unchanged fields
    assert updated["conversation_id"] == orig["conversation_id"]
    assert updated["original_filename"] == orig["original_filename"]
    assert updated["file_type"] == orig["file_type"]
    assert updated["file_size"] == orig["file_size"]
    assert updated["storage_path"] == orig["storage_path"]
    assert updated["extracted_text"] == orig["extracted_text"]
    # Changed fields
    assert updated["status"] == patch_data["status"]
    assert updated["additional_metadata"] == patch_data["additional_metadata"]
    assert updated["id"] == file_id
    assert "created_at" in updated
    assert "updated_at" in updated