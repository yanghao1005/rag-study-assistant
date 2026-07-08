"""
Content Generator Service
Specialized service for generating educational content
"""
import json
import re
from typing import List, Dict, Optional, Literal
from app.services.rag_service import RAGService
from app.core.database import get_db
from app.core.logging import logger

FLASHCARD_PROMPT = """You are an expert educational content creator.
Your task is to create high-quality flashcards based strictly on the provided context.

CONTEXT:
{context}

TOPIC: {query}

INSTRUCTIONS:
Create exactly {count} flashcards.
Each flashcard must have a 'front' (question/term) and a 'back' (answer/definition).
The content must be accurate and derived ONLY from the context.
Return the result as a raw JSON array. Do not use Markdown formatting.

OUTPUT FORMAT:
[
  {{
    "front": "Question or Term",
    "back": "Answer or Definition"
  }}
]
"""

QUIZ_PROMPT = """You are an expert exam creator.
Your task is to create a multiple-choice quiz based strictly on the provided context.

CONTEXT:
{context}

TOPIC: {query}
DIFFICULTY: {difficulty}

INSTRUCTIONS:
Create exactly {count} multiple-choice questions.
Each question must have 4 options, one correct answer (index 0-3), and an explanation.
Return the result as a raw JSON array. Do not use Markdown formatting.

OUTPUT FORMAT:
[
  {{
    "question": "The question text?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "explanation": "Explanation of why the answer is correct."
  }}
]
"""

class ContentGenerator:
    def __init__(self):
        self.rag_service = RAGService()
    
    def _clean_json_response(self, response: str) -> str:
        """Clean markdown code blocks from response"""
        cleaned = response.strip()
        # Remove ```json ... ``` wrapper
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(\w+)?", "", cleaned)
            cleaned = re.sub(r"```$", "", cleaned)
        return cleaned.strip()

    def _get_subject_id(self, scope: str, scope_id: str) -> Optional[str]:
        """Resolve subject_id from scope"""
        if scope == "subject":
            return scope_id
        
        db = get_db()
        if scope == "document":
            result = db.table("documents").select("subject_id").eq("id", scope_id).single().execute()
            return result.data["subject_id"] if result.data else None
            
        # For chapter, we'd need to look up chapter -> document -> subject
        # Assuming not implemented yet or similar to document
        return None

    async def generate_flashcards(
        self,
        scope: Literal["subject", "document", "chapter"],
        scope_id: str,
        topic: str = "General",
        count: int = 5
    ) -> Dict:
        """Generate flashcards from context"""
        # 1. Retrieve context
        # Use a broader query for "Overview" or specific topic
        search_query = topic if topic else "Summary identifying key concepts"
        
        context = await self.rag_service.retrieve_context(
            query=search_query,
            scope=scope,
            scope_id=scope_id,
            top_k=8  # Fetch more context for generation
        )
        
        if not context:
            logger.warning("No context found for flashcard generation")
            return {"flashcards": [], "sources": []}
            
        # 2. Generate
        response_text = await self.rag_service.generate_with_context(
            query=topic,
            context=context,
            prompt_template=FLASHCARD_PROMPT,
            count=count
        )
        
        # 3. Parse
        try:
            cleaned_json = self._clean_json_response(response_text)
            flashcards = json.loads(cleaned_json)
            
            # Basic validation
            valid_cards = [
                card for card in flashcards 
                if "front" in card and "back" in card
            ]
            
            # Persist to DB
            subject_id = self._get_subject_id(scope, scope_id)
            if subject_id:
                try:
                    db = get_db()
                    records = []
                    for card in valid_cards[:count]:
                        records.append({
                            "subject_id": subject_id,
                            "document_id": scope_id if scope == "document" else None,
                            "question": card["front"],
                            "answer": card["back"],
                            "tags": [topic] if topic else []
                        })
                    
                    if records:
                        db.table("flashcards").insert(records).execute()
                        logger.info(f"Saved {len(records)} flashcards to DB")
                except Exception as e:
                    logger.error(f"Failed to save flashcards: {e}")
            
            return {
                "flashcards": valid_cards[:count],
                "sources": [{"id": c["id"], "content": c["content"][:50] + "..."} for c in context]
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse flashcard JSON: {e}\nResponse: {response_text}")
            raise ValueError("Failed to generate valid flashcards format")

    async def generate_quiz(
        self,
        scope: Literal["subject", "document", "chapter"],
        scope_id: str,
        topic: str = "General",
        count: int = 5,
        difficulty: str = "medium"
    ) -> Dict:
        """Generate quiz from context"""
        # 1. Retrieve context
        search_query = topic if topic else "Key concepts for assessment"
        
        context = await self.rag_service.retrieve_context(
            query=search_query,
            scope=scope,
            scope_id=scope_id,
            top_k=10
        )
        
        if not context:
            return {"questions": [], "sources": []}
            
        # 2. Generate
        response_text = await self.rag_service.generate_with_context(
            query=topic,
            context=context,
            prompt_template=QUIZ_PROMPT,
            count=count,
            difficulty=difficulty
        )
        
        # 3. Parse
        try:
            cleaned_json = self._clean_json_response(response_text)
            questions = json.loads(cleaned_json)
            
            # Basic validation
            valid_questions = []
            for q in questions:
                if all(k in q for k in ["question", "options", "correct_answer"]):
                    valid_questions.append(q)
            
            # Persist to DB
            subject_id = self._get_subject_id(scope, scope_id)
            if subject_id:
                try:
                    db = get_db()
                    # 1. Create Quiz
                    quiz_data = {
                        "subject_id": subject_id,
                        "title": f"Quiz: {topic}" if topic else "Generated Quiz",
                        "question_count": len(valid_questions[:count])
                    }
                    quiz_result = db.table("quizzes").insert(quiz_data).execute()
                    
                    if quiz_result.data:
                        quiz_id = quiz_result.data[0]["id"]
                        
                        # 2. Create Questions
                        q_records = []
                        for i, q in enumerate(valid_questions[:count]):
                            q_records.append({
                                "quiz_id": quiz_id,
                                "question": q["question"],
                                "options": q["options"], # JSONB handles list
                                "correct_answer": str(q["options"][q["correct_answer"]]) if isinstance(q["correct_answer"], int) and 0 <= q["correct_answer"] < len(q["options"]) else str(q["correct_answer"]),
                                "explanation": q.get("explanation"),
                                "order_index": i
                            })
                            
                        if q_records:
                            db.table("quiz_questions").insert(q_records).execute()
                            logger.info(f"Saved quiz {quiz_id} with {len(q_records)} questions")
                except Exception as e:
                    logger.error(f"Failed to save quiz: {e}")

            return {
                "questions": valid_questions[:count],
                "sources": [{"id": c["id"], "content": c["content"][:50] + "..."} for c in context]
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse quiz JSON: {e}\nResponse: {response_text}")
            raise ValueError("Failed to generate valid quiz format")
