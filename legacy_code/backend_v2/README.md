# RAG Study Assistant - Backend V2

Refactored backend using **Clean Architecture**.

## Structure
```
backend_v2/
  src/
    domain/          # Core entities and interfaces (Ports)
    application/     # Use Cases (Business Logic)
    infrastructure/  # External adapters (Supabase, OpenAI, PyMuPDF)
    presentation/    # API endpoints (FastAPI)
    container.py     # Dependency Injection
  main.py            # Entry point
```

## Setup

1. **Create Virtual Environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment**:
   Ensure `.env` exists (copied from `backend/.env`).

## Running

Start the server:
```bash
python main.py
```
Or with uvicorn directly:
```bash
uvicorn main:app --reload
```

## API Documentation

Visit `http://localhost:8000/docs` to test endpoints.

- **POST /api/v1/documents/upload**: Upload PDF + Chunking + Embedding
- **POST /api/v1/rag/query**: Ask questions using RAG
