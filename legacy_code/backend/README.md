# RAG Study Assistant - Backend

FastAPI backend with **flexible AI provider support** for easy testing and experimentation.

## 🎯 Key Features

- **Plug-and-Play AI Providers**: Switch between OpenAI, Ollama, HuggingFace, Cohere, Anthropic via environment variables
- **Docker Support**: Containerized development environment
- **Flexible Configuration**: Easy model and embedding swapping for testing
- **Clean Architecture**: Separation of concerns with service layer abstraction

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   └── v1/           # API v1 routes
│   ├── core/             # Core configuration
│   │   ├── config.py     # Settings & AI provider config
│   │   ├── database.py   # Supabase connection
│   │   └── logging.py    # Structured logging
│   ├── services/         # Business logic
│   │   └── ai/           # AI service abstraction
│   │       ├── base.py           # Abstract base classes
│   │       ├── factory.py        # Provider factory
│   │       ├── openai_provider.py    # OpenAI implementation
│   │       └── ollama_provider.py    # Ollama implementation
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   └── main.py           # FastAPI app
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit .env with your credentials
# Set AI_PROVIDER=openai (or ollama, huggingface, etc.)
# Add your API keys

# 3. Build and run
docker-compose up --build

# API will be available at http://localhost:8000
```

### Option 2: Local Python

```bash
# 1. Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy and configure .env
cp .env.example .env

# 4. Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔧 Switching AI Providers

### OpenAI (Default)
```env
AI_PROVIDER=openai
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### Ollama (Local Models)
```env
AI_PROVIDER=ollama
EMBEDDING_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

**Setup Ollama:**
```bash
# Uncomment ollama service in docker-compose.yml
# Or install locally: https://ollama.ai

# Pull models
ollama pull llama2
ollama pull nomic-embed-text
```

### HuggingFace (To be implemented)
```env
AI_PROVIDER=huggingface
EMBEDDING_PROVIDER=huggingface
HUGGINGFACE_API_KEY=hf_your_key
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.1
HUGGINGFACE_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## 🧪 Testing Different Configurations

The architecture makes it easy to test different AI setups:

```bash
# Test with OpenAI
AI_PROVIDER=openai docker-compose up

# Test with local Ollama
AI_PROVIDER=ollama docker-compose up

# Mix providers (e.g., OpenAI LLM + Ollama embeddings)
AI_PROVIDER=openai
EMBEDDING_PROVIDER=ollama
```

## 📊 API Endpoints

### Health Check
```bash
GET http://localhost:8000/health
```

### Root
```bash
GET http://localhost:8000/
```

Returns current AI provider configuration.

## 🔨 Development

### Add New AI Provider

1. Create provider file: `app/services/ai/your_provider.py`
2. Implement `BaseLLM` and `BaseEmbedding` interfaces
3. Add to factory in `app/services/ai/factory.py`
4. Update `config.py` with new provider enum

Example:
```python
# app/services/ai/custom_provider.py
from app.services.ai.base import BaseLLM

class CustomLLM(BaseLLM):
    def generate(self, prompt: str, **kwargs) -> str:
        # Your implementation
        pass
```

### Run Tests (coming soon)
```bash
pytest
```

## 📝 Environment Variables

See `.env.example` for all available configuration options.

**Required:**
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon key
- `AI_PROVIDER` - Which LLM provider to use
- `EMBEDDING_PROVIDER` - Which embedding provider to use
- Provider-specific API keys (based on your choice)

**Optional:**
- `CHUNK_SIZE` - Text chunk size (default: 1000)
- `CHUNK_OVERLAP` - Chunk overlap (default: 200)
- `TOP_K` - Number of similar chunks to retrieve (default: 5)
- `SIMILARITY_THRESHOLD` - Similarity cutoff (default: 0.7)

## 🐳 Docker Commands

```bash
# Build
docker-compose build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop
docker-compose down

# Rebuild after code changes
docker-compose up --build
```

## 📚 Next Steps

1. ✅ Backend structure created with flexible AI provider support
2. 🔄 Implement PDF parsing service
3. 🔄 Implement RAG pipeline
4. 🔄 Create API endpoints (subjects, documents, chapters, generate)
5. 🔄 Add tests

## 🤝 Contributing

This is a TFM (Master's Thesis) project. For questions, contact the maintainer.

## 📄 License

MIT
