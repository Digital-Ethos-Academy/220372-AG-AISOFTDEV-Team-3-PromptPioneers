"""Test complete workflow with proper data setup"""
from database import SessionLocal
from models import Conversation, Message, FileAttachment
import traceback

def test_complete_workflow():
    """Test creating conversation, message, and file attachment"""
    db = SessionLocal()
    try:
        print("Step 1: Creating conversation...")
        conversation = Conversation(
            title="Test Conversation",
            status="active",
            additional_metadata='{"test": true}'
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        print(f"✓ Created conversation with ID: {conversation.id}")
        
        print("\nStep 2: Creating message...")
        message = Message(
            conversation_id=conversation.id,
            sender="user",
            message_type="text",
            content="This is a test message",
            status="delivered",
            additional_metadata='{"test": true}'
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        print(f"✓ Created message with ID: {message.id}")
        
        print("\nStep 3: Creating file attachment...")
        attachment = FileAttachment(
            conversation_id=conversation.id,
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
        print(f"✓ Created file attachment with ID: {attachment.id}")
        
        print("\nStep 4: Querying all file attachments...")
        attachments = db.query(FileAttachment).all()
        print(f"✓ Found {len(attachments)} file attachment(s)")
        
        for att in attachments:
            print(f"   - ID: {att.id}, File: {att.original_filename}, Status: {att.status}")
        
        print("\n" + "=" * 60)
        print("✓ ALL STEPS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ Error: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_complete_workflow()
