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
        self.llm_service = OpenAILLMService()
        self.embedding_service = HuggingFaceEmbeddingService()
        self.file_parser = PyMuPDFParser()
        self.text_chunker = LangChainTextChunker()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Container()
        return cls._instance
