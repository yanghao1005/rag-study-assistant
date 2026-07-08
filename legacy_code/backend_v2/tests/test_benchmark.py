import asyncio
import os
import json
import logging
import argparse
import sys
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("benchmark")

async def run_benchmark(
    llm_provider: str,
    llm_model: str,
    embedding_provider: str,
    embedding_model: str,
    test_docs_path: str,
    output_path: str
):
    # Overwrite Environment Variables BEFORE importing container/config
    os.environ["DEFAULT_LLM_PROVIDER"] = llm_provider
    os.environ["DEFAULT_LLM_MODEL"] = llm_model
    os.environ["DEFAULT_EMBEDDING_PROVIDER"] = embedding_provider
    os.environ["DEFAULT_EMBEDDING_MODEL"] = embedding_model
    
    # Now import app logic
    from src.container import Container
    from src.application.use_cases.ingest_document import IngestDocumentUseCase
    from src.application.use_cases.agentic_rag import AgenticRAGUseCase
    from src.config import get_settings
    
    # Reload settings to be safe (Container might have initialized already if imports top-level)
    get_settings.cache_clear()
    
    container = Container.get_instance()
    # Force re-init of services if container was already created
    # This is a bit hacky but necessary for dynamic switching in one script run if we were looping
    # But for a single run script, setting env before import is usually enough if Container is lazy.
    # However, Container.get_instance() creates it. Let's force re-creation if needed or just trust the process.
    # For a robust script, we might want to reinstantiate the container or services.
    # Given the Container implementation, it loads in __init__. So we should be good if it's the first time.
    
    ingest_service = IngestDocumentUseCase(
        document_repository=container.document_repository,
        vector_store=container.vector_store,
        file_parser=container.file_parser,
        text_chunker=container.text_chunker,
        embedding_service=container.embedding_service,
        llm_service=container.llm_service
    )
    
    rag_service = AgenticRAGUseCase(
        vector_store=container.vector_store,
        embedding_service=container.embedding_service,
        llm_service=container.llm_service
    )
    
    # 0. Ensure Benchmark Subject Exists
    from src.domain.entities import Subject
    
    logger.info("Creating/Ensuring Benchmark Subject...")
    subject = Subject.create(name="Benchmark Test Subject", description="Subject for automated benchmark tests")
    # We save it to ensure it exists. In a real scenario we might check by name, but creating new is safer for isolation if we cleanup.
    # For now, let's just save.
    await container.subject_repository.save(subject)
    logger.info(f"Using Subject: {subject.name} ({subject.id})")

    # 1. Ingest Documents
    docs_dir = Path(test_docs_path)
    if not docs_dir.exists():
        logger.error(f"Documents directory not found: {docs_dir}")
        return

    pdf_files = list(docs_dir.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDFs to ingest.")
    
    for pdf_path in pdf_files:
        logger.info(f"Ingesting: {pdf_path.name}")
        try:
            with open(pdf_path, "rb") as f:
                content = f.read()
                # Basic mock upload file
                from fastapi import UploadFile
                from io import BytesIO
                file_obj = UploadFile(filename=pdf_path.name, file=BytesIO(content))
                await ingest_service.execute(file_path=str(pdf_path), subject_id=subject.id, title=pdf_path.name)
        except Exception as e:
            logger.error(f"Failed to ingest {pdf_path.name}: {e}")

    # 2. Run Queries
    queries = [
        "What is the main topic of these documents?",
        "Explain the key concepts found.",
        "Create a quiz about the introduction.",
        "What are the conclusions?",
        "Generate flashcards for the first chapter.",
        "generate flashcards for Business Model Canvas concepts"
    ]
    
    results = []
    
    for q in queries:
        logger.info(f"Running Query: {q}")
        start_time = datetime.now()
        
        # Determine type
        gen_type = "answer"
        if "quiz" in q.lower():
            gen_type = "quiz"
        elif "flashcard" in q.lower():
            gen_type = "flashcards"
            
        try:
            response = await rag_service.execute(query=q, generation_type=gen_type, subject_id=subject.id)
            duration = (datetime.now() - start_time).total_seconds()
            
            results.append({
                "query": q,
                "type": gen_type,
                "answer": response.get("answer"),
                "context_count": len(response.get("context", [])),
                "duration_seconds": duration,
                "model_config": {
                    "llm": f"{llm_provider}/{llm_model}",
                    "embedding": f"{embedding_provider}/{embedding_model}"
                }
            })
        except Exception as e:
            logger.error(f"Query failed: {q} - {e}")
            results.append({
                "query": q,
                "type": gen_type,
                "error": str(e)
            })

    # 3. Save Results
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Benchmark complete. Results saved to {output_path}")
    
    # 4. Generate HTML Report
    generate_html_report(results, output_path.replace(".json", ".html"))

def generate_html_report(results: List[Dict], output_path: str):
    html_content = """
    <html>
    <head>
        <title>RAG Benchmark Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .answer { white-space: pre-wrap; font-family: monospace; background: #f9f9f9; padding: 10px; }
            .meta { font-size: 0.9em; color: #666; }
        </style>
    </head>
    <body>
        <h1>RAG Benchmark Report</h1>
    """
    
    if results:
        config = results[0].get("model_config", {})
        html_content += f"<h3>Configuration: LLM={config.get('llm')}, Embedding={config.get('embedding')}</h3>"
    
    html_content += """
        <table>
            <thead>
                <tr>
                    <th style="width: 15%">Query / Type</th>
                    <th style="width: 60%">Response</th>
                    <th style="width: 25%">Metrics</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for r in results:
        query = r.get("query")
        q_type = r.get("type")
        answer = r.get("answer", "Error: " + r.get("error", "Unknown"))
        duration = r.get('duration_seconds', 0)
        ctx_count = r.get('context_count', 0)
        
        html_content += f"""
            <tr>
                <td>
                    <b>{query}</b><br>
                    <span class="meta">Type: {q_type}</span>
                </td>
                <td>
                    <div class="answer">{answer}</div>
                </td>
                <td>
                    Time: {duration:.2f}s<br>
                    Context Docs: {ctx_count}
                </td>
            </tr>
        """
        
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    logger.info(f"HTML Report saved to {output_path}")

if __name__ == "__main__":
    default_docs_path = project_root / "pdf_tests_documents"
    
    parser = argparse.ArgumentParser(description="Run RAG Benchmark")
    parser.add_argument("--llm-provider", default="openai", help="LLM Provider (openai)")
    parser.add_argument("--llm-model", default="gpt-4o-mini", help="LLM Model Name")
    parser.add_argument("--embed-provider", default="openai", help="Embedding Provider (openai, huggingface)")
    parser.add_argument("--embed-model", default="text-embedding-3-small", help="Embedding Model Name")
    parser.add_argument("--docs-path", default=str(default_docs_path), help="Path to PDF documents")
    parser.add_argument("--output", default="benchmark_results.json", help="Output JSON path")
    
    args = parser.parse_args()
    
    asyncio.run(run_benchmark(
        llm_provider=args.llm_provider,
        llm_model=args.llm_model,
        embedding_provider=args.embed_provider,
        embedding_model=args.embed_model,
        test_docs_path=args.docs_path,
        output_path=args.output
    ))
