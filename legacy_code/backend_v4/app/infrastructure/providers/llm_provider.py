class LLMProvider:
    def generate_json(self, prompt: str) -> dict:
        normalized = prompt.lower()
        if "flashcards" in normalized:
            return {
                "flashcards": [
                    {
                        "front": "What is retrieval-augmented generation?",
                        "back": "A technique that grounds LLM outputs with retrieved external context.",
                    }
                ],
                "sources": [
                    {
                        "document_type": "pdf",
                        "page": 1,
                        "chapter_name": "Chapter 1",
                        "preview": "RAG combines retrieval and generation.",
                    }
                ],
            }

        if "quiz" in normalized:
            return {
                "questions": [
                    {
                        "question": "Which component improves grounding in RAG?",
                        "options": ["Vector retrieval", "Temperature=2", "No context", "Random prompts"],
                        "correct_answer": 0,
                        "explanation": "Retrieval adds relevant context before generation.",
                    }
                ]
            }

        return {}
