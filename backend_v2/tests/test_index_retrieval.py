import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.append(str(project_root))

# Load Env
load_dotenv(project_root / ".env")

async def test_index_retrieval():
    print("--- STARTING INDEX RETRIEVAL TEST ---")
    
    from src.container import Container
    from src.domain.entities import Subject
    from src.application.use_cases.ingest_document import IngestDocumentUseCase
    from src.infrastructure.ai.agent_nodes import AgentNodes
    from src.domain.agent_types import GraphState
    
    container = Container.get_instance()
    
    # 1. Setup Subject
    subject_name = "Index Test Subject"
    print(f"Creating subject: {subject_name}")
    subject = Subject.create(name=subject_name)
    await container.subject_repository.save(subject)
    
    # 2. Ingest Document
    pdf_path = project_root / "pdf_tests_documents" / "1_BMC_OBS.pdf"
    if not pdf_path.exists():
        print(f"ERROR: Test PDF not found at {pdf_path}")
        return

    print(f"Ingesting {pdf_path.name}...")
    ingest_use_case = IngestDocumentUseCase(
        container.document_repository,
        container.vector_store,
        container.embedding_service,
        container.file_parser,
        container.text_chunker,
        container.llm_service
    )
    
    doc = await ingest_use_case.execute(str(pdf_path), subject.id, pdf_path.name)
    print(f"Ingestion Complete. Doc ID: {doc.id}")
    print(f"Has Summary? {'Yes' if doc.summary else 'No'}")
    print(f"Has Index? {'Yes' if doc.index else 'No'}")
    if doc.index:
        print(f"Index Keys: {doc.index.keys()}")
        chunk_map = doc.index.get("chunk_map", [])
        print(f"Mapped {len(chunk_map)} chunks in index.")

    # 3. Test Queries
    nodes = AgentNodes()
    
    queries = [
        ("Summarize this document", "global_generic"),
        ("What are the conclusions?", "section_generic"),
        ("What is the Value Proposition?", "specific")
    ]
    
    print("\n--- TESTING QUERIES ---")
    
    for q, expected_intent in queries:
        print(f"\nQuery: '{q}' (Expected: {expected_intent})")
        
        state = {"question": q, "subject_id": subject.id}
        result = await nodes.retrieve(state)
        
        docs = result.get("documents", [])
        print(f"Retrieved {len(docs)} documents/chunks.")
        
        if docs:
            first_doc = docs[0]
            content_preview = first_doc.get("content", "")[:100].replace("\n", " ")
            print(f"First Result Preview: {content_preview}...")
            
            # Check for source metadata to confirm intent path
            meta = first_doc.get("metadata", {})
            if meta.get("source") == "summary":
                print("✅ Path: Global Summary")
            elif "chunk_index" in meta:
                print("✅ Path: Chunk/Index Retrieval")
            else:
                print("ℹ️  Path: Vector Search (Default)")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_index_retrieval())
