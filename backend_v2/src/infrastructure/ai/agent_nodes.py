from typing import Any, Dict
from src.domain.agent_types import GraphState
from src.container import Container

class AgentNodes:
    def __init__(self):
        self.container = Container.get_instance()
    
    async def retrieve(self, state: GraphState) -> Dict[str, Any]:
        """
        Retrieve documents from vector store
        """
        print("---RETRIEVE---")
        question = state["question"]
        
        # Refine Query for Search
        # We want to strip instructions like "Create a quiz" and focus on the topic.
        refine_prompt = f"""You are a query optimizer. The user has sent a request that might include instructions (e.g., "Create a quiz", "Generate flashcards").
        Your goal is to extract the core TOPIC or KEYWORDS to use for a vector search database.
        
        User Request: {question}
        
        Rules:
        1. Remove instructions (e.g. "Create a quiz about...").
        2. If a specific topic is present, output ONLY that topic.
        3. If NO specific topic is mentioned (e.g. just "Generate flashcards"), output "Main concepts, summary, and key points".
        
        Provide ONLY the concise search query value. Do not explain."""
        
        search_query = await self.container.llm_service.generate(refine_prompt)
        print(f"---INFO: Refined Search Query: '{search_query}' (Original: '{question}')---")
        
        # Embed refined question
        query_embedding = await self.container.embedding_service.embed_text(search_query)
        
        # Search
        subject_id = state.get("subject_id")
        results = await self.container.vector_store.search(
            query_embedding=query_embedding,
            top_k=5,
            subject_id=subject_id
        )
        
        # Map dicts to Chunk entities (simplified for now, just keep as dicts if needed or map back)
        # Note: VectorStore.search returns dicts, GraphState expects Chunks or dicts (typed as Chunk for convenience)
        # Let's trust the typing is permissive or we map them.
        
        return {"documents": results, "question": question}

    async def generate(self, state: GraphState) -> Dict[str, Any]:
        """
        Generate answer using RAG
        """
        print("---GENERATE---")
        question = state["question"]
        documents = state["documents"]
        
        # Check if we have documents
        if not documents:
            return {"generation": "I couldn't find any documents to answer your question.", "question": question}
        
        # Context
        context_text = "\n\n".join([
            f"[Source: Page {d.get('page_num', '?')}]\n{d['content']}" 
            for d in documents
        ])
        
        feedback = state.get("feedback")
        feedback_prompt = f"\nNote: Your previous attempt had issues. Feedback: {feedback}\nPlease correct this in your new answer." if feedback else ""
        
        prompt = f"""
        You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
        {feedback_prompt}
        
        Question: {question} 
        
        Context:
        {context_text} 
        
        Answer:
        """
        
        generation = await self.container.llm_service.generate(prompt)
        return {"generation": generation, "documents": documents, "question": question}

    async def generate_quiz(self, state: GraphState) -> Dict[str, Any]:
        """
        Generate a quiz based on relevant documents
        """
        print("---GENERATE QUIZ---")
        question = state["question"]
        documents = state["documents"]
        
        if not documents:
            return {"generation": "I couldn't find any documents to generate a quiz.", "question": question}
        
        context_text = "\n\n".join([d["content"] for d in documents])
        
        feedback = state.get("feedback")
        feedback_prompt = f"\nNote: Your previous attempt had issues. Feedback: {feedback}\nPlease correct this in your new quiz." if feedback else ""
        
        prompt = f"""
        You are a generic quiz generator. Create a quiz with 3 multiple-choice questions based on the context provided.
        Format the output clearly with the Question, Options, and Correct Answer.
        {feedback_prompt}
        
        Topic/Question: {question}
        
        Context:
        {context_text} 
        
        Quiz:
        """
        
        generation = await self.container.llm_service.generate(prompt)
        return {"generation": generation, "documents": documents, "question": question}

    async def generate_flashcards(self, state: GraphState) -> Dict[str, Any]:
        """
        Generate flashcards based on relevant documents
        """
        print("---GENERATE FLASHCARDS---")
        question = state["question"]
        documents = state["documents"]
        
        if not documents:
            return {"generation": "I couldn't find any documents to generate flashcards.", "question": question}
        
        context_text = "\n\n".join([d["content"] for d in documents])
        
        feedback = state.get("feedback")
        feedback_prompt = f"\nNote: Your previous attempt had issues. Feedback: {feedback}\nPlease correct this in your new flashcards." if feedback else ""
        
        prompt = f"""
        You are a study assistant. Create 3 flashcards (Front/Back) based on the context provided.
        Focus on key concepts related to the user's request.
        {feedback_prompt}
        
        Topic/Question: {question}
        
        Context:
        {context_text}
        
        Flashcards:
        """
        
        generation = await self.container.llm_service.generate(prompt)
        return {"generation": generation, "documents": documents, "question": question}

    async def grade_documents(self, state: GraphState) -> Dict[str, Any]:
        """
        Determines whether the retrieved documents are relevant to the question.
        """
        print("---CHECK DOCUMENT RELEVANCE---")
        question = state["question"]
        documents = state["documents"]
        
        # Grade each document
        filtered_docs = []
        
        # Simple grading prompt
        system_prompt = """You are a grader assessing relevance of a retrieved document to a user question. \n 
        If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant. \n
        Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
        
        for d in documents:
            content = d["content"]
            prompt = f"System: {system_prompt}\n\nDocument: {content}\n\nQuestion: {question}\n\nIs it relevant? Answer 'yes' or 'no':"
            
            # Use LLM to grade (sequential for now, could be parallel)
            grade = await self.container.llm_service.generate(prompt)
            
            if "yes" in grade.lower():
                print("---GRADE: DOCUMENT RELEVANT---")
                filtered_docs.append(d)
                print("---GRADE: DOCUMENT NOT RELEVANT---")
                continue
                
        return {"documents": filtered_docs, "question": question}

    async def grade_hallucination(self, state: GraphState) -> Dict[str, Any]:
        """
        Determines whether the generation is grounded in the document.
        """
        print("---CHECK HALLUCINATIONS---")
        question = state["question"]
        documents = state["documents"]
        generation = state["generation"]
        
        system_prompt = """You are a grader assessing whether an answer is grounded in / supported by a set of facts.
        Give a score 'yes' or 'no'. 
        If 'no', provide a brief explanation of what part of the answer is not supported by the facts.
        Format: Score: [yes/no] Explanation: [explanation]"""
        
        context = "\n\n".join([d["content"] for d in documents])
        prompt = f"System: {system_prompt}\n\nFacts: {context}\n\nStudent Answer: {generation}\n\nAssessment:"
        
        response = await self.container.llm_service.generate(prompt)
        
        if "score: yes" in response.lower():
            print("---DECISION: GENERATION IS GROUNDED---")
            return {"hallucination_status": "grounded", "documents": documents, "question": question, "generation": generation}
        else:
            print("---DECISION: GENERATION IS HALLUCINATED---")
            # Extract feedback (simple split for now)
            feedback = response
            print(f"Feedback: {feedback}")
            return {"hallucination_status": "hallucinated", "documents": documents, "question": question, "generation": generation, "feedback": feedback}

    async def grade_answer(self, state: GraphState) -> Dict[str, Any]:
        """
        Determines whether the generation addresses the question.
        """
        print("---CHECK ANSWER RELEVANCE---")
        question = state["question"]
        generation = state["generation"]
        
        system_prompt = "You are a grader assessing whether an answer addresses / resolves a question. \n Give a binary score 'yes' or 'no'. 'yes' means the answer resolves the question."
        prompt = f"System: {system_prompt}\n\nQuestion: {question}\n\nStudent Answer: {generation}\n\nDoes the answer resolve the question? Answer 'yes' or 'no':"
        
        score = await self.container.llm_service.generate(prompt)
        
        if "yes" in score.lower():
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return {"answer_status": "useful", "question": question, "generation": generation}
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return {"answer_status": "not_useful", "question": question, "generation": "I generated an answer, but it doesn't seem to address your specific question fully."}

    async def prepare_for_retry(self, state: GraphState) -> Dict[str, Any]:
        """
        Increments loop count and potentially updates instructions or question
        """
        print("---PREPARE FOR RETRY---")
        loop_count = state.get("loop_count", 0)
        feedback = state.get("feedback", "No feedback provided.")
        new_count = loop_count + 1
        return {"loop_count": new_count, "generation": "Hallucinated. Retrying...", "feedback": feedback}

    async def transform_query(self, state: GraphState) -> Dict[str, Any]:
        """
        Transform the query to produce a better question.
        """
        print("---TRANSFORM QUERY---")
        question = state["question"]
        
        # Create a prompt to rewrite the question
        prompt = f"""You are a helpful assistant that generates optimal questions for semantic search. \n 
        Look at the input question and reason about the underlying semantic intent / meaning. \n 
        Here is the initial question:
        \n ------- \n
        {question} 
        \n ------- \n
        Formulate an improved question:"""
        
        better_question = await self.container.llm_service.generate(prompt)
        
        current_count = state.get("transform_count", 0)
        new_count = current_count + 1
        return {"question": better_question, "transform_count": new_count}
