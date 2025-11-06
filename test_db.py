"""Test database operations to diagnose 500 errors"""
from database import SessionLocal
from models import FileAttachment
import traceback

def test_query():
    db = SessionLocal()
    try:
        print("Testing database query...")
        result = db.query(FileAttachment).all()
        print(f"✓ Success! Found {len(result)} attachments")
        return True
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_query()
