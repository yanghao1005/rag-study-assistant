"""
Quick database connection test
"""
import sys
from pathlib import Path
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import get_db
from app.core.config import settings

def test_connection():
    """Test basic Supabase connection"""
    print("Testing Supabase connection...")
    print(f"URL: {settings.supabase_url}")
    
    try:
        db = get_db()
        
        # Try to query subjects table
        result = db.table("subjects").select("*").limit(1).execute()
        
        print(f"✅ Connection successful!")
        print(f"   Subjects count: {len(result.data)}")
        
        # Try to insert and delete a test chunk
        test_uuid = str(uuid.uuid4())
        print(f"\n   Testing insert with UUID: {test_uuid}")
        
        test_record = {
            "document_id": test_uuid,
            "subject_id": test_uuid,
            "content": "Test content",
            "embedding": [0.1] * 768,
            "metadata": {"test": True}
        }
        
        insert_result = db.table("document_chunks").insert(test_record).execute()
        print(f"   ✅ Insert successful: {len(insert_result.data)} record")
        
        # Delete test record
        delete_result = db.table("document_chunks").delete().eq("document_id", test_uuid).execute()
        print(f"   ✅ Delete successful: {len(delete_result.data)} record cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
