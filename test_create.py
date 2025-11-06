"""Test create endpoint with detailed error info"""
from database import SessionLocal
from models import FileAttachment as FileAttachmentModel
import traceback

def test_direct_create():
    """Test creating directly with SQLAlchemy"""
    db = SessionLocal()
    try:
        print("Creating file attachment directly...")
        attachment = FileAttachmentModel(
            conversation_id=1,
            original_filename="test.txt",
            file_type="txt",
            file_size=1024,
            storage_path="/uploads/test.txt",
            extracted_text="Test content",
            status="uploaded",
            additional_metadata='{"key": "value"}'
        )
        db.add(attachment)
        db.commit()
        db.refresh(attachment)
        print(f"✓ Success! Created attachment with ID: {attachment.id}")
        return True
    except Exception as e:
        db.rollback()
        print(f"✗ Error: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_direct_create()
