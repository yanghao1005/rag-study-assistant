from src.infrastructure.supabase.repositories import SupabaseDocumentRepository, SupabaseSubjectRepository, SupabaseVectorStore
from src.infrastructure.ai.services import OpenAILLMService, HuggingFaceEmbeddingService
from src.infrastructure.file_parser import PyMuPDFParser
from src.infrastructure.text_chunker import LangChainTextChunker

class Container:
    _instance = None

    def __init__(self):
        self.subject_repository = SupabaseSubjectRepository()
        self.document_repository = SupabaseDocumentRepository()
        self.vector_store = SupabaseVectorStore()
        
        # Load Settings
        from src.config import get_settings
        settings = get_settings()
        
        # LLM Factory
        if settings.DEFAULT_LLM_PROVIDER == "openai":
            from src.infrastructure.ai.services import OpenAILLMService
            self.llm_service = OpenAILLMService()
        else:
             # Default or fallback
            from src.infrastructure.ai.services import OpenAILLMService
            self.llm_service = OpenAILLMService()

        # Embedding Factory
        if settings.DEFAULT_EMBEDDING_PROVIDER == "openai":
            from src.infrastructure.ai.services import OpenAIEmbeddingService
            self.embedding_service = OpenAIEmbeddingService()
        elif settings.DEFAULT_EMBEDDING_PROVIDER == "huggingface":
            from src.infrastructure.ai.services import HuggingFaceEmbeddingService
            self.embedding_service = HuggingFaceEmbeddingService()
        else:
            # Default
            from src.infrastructure.ai.services import HuggingFaceEmbeddingService
            self.embedding_service = HuggingFaceEmbeddingService()

        self.file_parser = PyMuPDFParser()
        self.text_chunker = LangChainTextChunker()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Container()
        return cls._instance
