from app.core.database import get_db

def verify():
    print("=== Verifying Database Persistence ===")
    try:
        db = get_db()
        result = db.table("flashcards").select("id", count="exact").execute()
        count = result.count
        print(f"Total Flashcards in DB: {count}")
        
        if count > 0:
            print("✅ SUCCESS: Flashcards are being saved.")
            # Show the last one
            last = db.table("flashcards").select("question").order("created_at", desc=True).limit(1).execute()
            if last.data:
                print(f"   Last Question: {last.data[0]['question']}")
        else:
            print("❌ FAILURE: No flashcards found in DB.")
            
    except Exception as e:
        print(f"Error checking DB: {e}")

if __name__ == "__main__":
    verify()
