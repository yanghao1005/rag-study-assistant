import asyncio
import httpx
from pathlib import Path
import os
import sys

# Configuration
API_URL = "http://localhost:8000/api/v1"
PDF_DIR = Path("pdf_tests_documents")

async def main():
    if not PDF_DIR.exists():
        print(f"Error: Directory '{PDF_DIR}' not found.")
        return

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Check/Create Subject
        print("Checking for Test Subject...")
        try:
            # List subjects to see if ours exists
            response = await client.get(f"{API_URL}/subjects")
            response.raise_for_status()
            subjects = response.json()
            
            subject_id = None
            for sub in subjects:
                if sub["name"] == "Test Subject":
                    subject_id = sub["id"]
                    print(f"Found existing subject: {subject_id}")
                    break
            
            if not subject_id:
                print("Creating new Test Subject...")
                response = await client.post(f"{API_URL}/subjects", json={
                    "name": "Test Subject",
                    "description": "Subject for automated API testing"
                })
                response.raise_for_status()
                subject = response.json()
                subject_id = subject["id"]
                print(f"Created subject: {subject_id}")

        except httpx.RequestError as e:
            print(f"Error connecting to API: {e}")
            print("Is the server running? (Try running start.bat)")
            return
        except httpx.HTTPstatusError as e:
            print(f"API Error: {e.response.text}")
            return

        # 2. Upload Documents
        pdf_files = list(PDF_DIR.glob("*.pdf"))
        if not pdf_files:
            print(f"No PDF files found in {PDF_DIR}")
            return
        
        print(f"\nFound {len(pdf_files)} PDF(s). Uploading...")
        
        for pdf_file in pdf_files:
            print(f"Uploading {pdf_file.name}...")
            
            try:
                # Prepare multipart upload
                files = {
                    "file": (pdf_file.name, open(pdf_file, "rb"), "application/pdf")
                }
                data = {
                    "subject_id": subject_id,
                    "title": pdf_file.stem
                }
                
                response = await client.post(
                    f"{API_URL}/documents/upload",
                    data=data,
                    files=files
                )
                
                if response.status_code == 201:
                    result = response.json()
                    print(f"✅ Success! Document ID: {result['document_id']}")
                    print(f"   Status: {result['status']}")
                else:
                    print(f"❌ Failed ({response.status_code}): {response.text}")

            except Exception as e:
                print(f"❌ Error uploading {pdf_file.name}: {e}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
