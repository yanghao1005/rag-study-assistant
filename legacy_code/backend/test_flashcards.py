import asyncio
import httpx
import json

# Configuration
API_URL = "http://localhost:8000/api/v1"

async def main():
    print("=== Testing Flashcard Generation API ===")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. Get a Subject
        print("\n1. Fetching Subjects...")
        try:
            response = await client.get(f"{API_URL}/subjects")
            response.raise_for_status()
            subjects = response.json()
            
            if not subjects:
                print("❌ No subjects found. Please run test_api_upload.py first.")
                return
                
            # Pick the first one (likely "Test Subject")
            subject = subjects[0]
            print(f"   Selected Subject: {subject['name']} ({subject['id']})")
            
        except Exception as e:
            print(f"❌ Error fetching subjects: {e}")
            return

        # 2. Generate Flashcards
        print(f"\n2. Generating Flashcards for '{subject['name']}'...")
        payload = {
            "scope": "subject",
            "scope_id": subject["id"],
            "topic": "Key Concepts", # Summary/General topic
            "count": 3
        }
        
        try:
            response = await client.post(f"{API_URL}/generate/flashcards", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                flashcards = data.get("flashcards", [])
                
                if not flashcards:
                    print("⚠️ No flashcards returned. (Did RAG retrieve any context?)")
                else:
                    print(f"\n✅ Generated {len(flashcards)} Flashcards:")
                    for i, card in enumerate(flashcards, 1):
                        print(f"\n   Card {i}")
                        print(f"   Q: {card['front']}")
                        print(f"   A: {card['back']}")
                        
                # Show sources if any
                sources = data.get("sources", [])
                if sources:
                    print(f"\n   (Based on {len(sources)} context chunks)")
            else:
                print(f"❌ API Error ({response.status_code}): {response.text}")
                
        except Exception as e:
            print(f"❌ Request Failed: {e}")

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
