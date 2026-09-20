This is a high-level architectural blueprint for your TFM (Master's Thesis). Since you are using **Next.js** for the frontend, I have selected a backend and a suite of technologies that balance cutting-edge research with production-grade stability.

### Backend Recommendation: Python (FastAPI)
For an AI-heavy project involving GraphRAG and complex orchestration, **Python (FastAPI)** is the undisputed choice over Node.js.
* **Why:** You need access to `LlamaIndex` or `LangChain` (the Python versions are more mature), `NetworkX` for graph processing, and `PyTorch/Transformers` if you do local embedding/reranking.
* **Integration:** Next.js will communicate with FastAPI via a REST API or Server-Sent Events (SSE) for streaming AI responses.

---

# Technical Specification: Agentic-GraphRAG Learning System

## 1. System Architecture
The system follows an **Agentic Hybrid RAG** design. It moves away from a "linear pipeline" to a "decision-making loop."



### A. The Multi-Index Layer
To solve the "Summary" problem, we don't just store one type of data. We build three:
1.  **Vector Index (Top-K):** Standard chunks (512-1024 tokens). Good for: *"What is the definition of X?"*
2.  **Summary Index (Recursive):** Using the **RAPTOR** approach. We cluster chunks and summarize them, then summarize those summaries into a tree. Good for: *"What are the main themes of this chapter?"*
3.  **Knowledge Graph Index (GraphRAG):** Extracts (Subject-Predicate-Object) triplets. Good for: *"How does Concept A relate to Concept D across different lectures?"*

### B. The Routing Layer (The Brain)
A **Semantic Router** identifies the intent of the user query:
* **Level 1 (Direct):** Fact retrieval -> Vector Index.
* **Level 2 (Global):** Synthesis/Comparison -> Summary/Graph Index.
* **Level 3 (Action):** Quiz/Flashcard generation -> Task-specific Agent.

---

## 2. The Quiz & Flashcard Pipeline
Generating high-quality educational content requires more than a simple prompt.

1.  **Knowledge Extraction:** The Agent crawls the Knowledge Graph to find "High-Centrality Nodes" (the most important concepts).
2.  **Distractor Generation:** For Multiple Choice Questions (MCQs), the AI uses the Vector Store to find "Hard Negatives"—concepts that are similar but incorrect—to make the quiz challenging.
3.  **Formatting:** Outputs are strictly parsed into JSON/Anki format using **Instructor** or **Pydantic** to ensure the Next.js frontend can render them perfectly.

---

## 3. Technical Implementation Details

| Component | Technology | Implementation Note |
| :--- | :--- | :--- |
| **Orchestration** | **LlamaIndex (Python)** | Superior for "Data Indexing" compared to LangChain. |
| **Vector DB** | **Qdrant** or **Pinecone** | Use Qdrant if you want to run it locally in Docker. |
| **Graph DB** | **Neo4j** | Necessary for storing entities and relationships for GraphRAG. |
| **Reranker** | **Cohere Rerank** or **BGE-Reranker** | **Crucial:** Reduces "Noise" by re-evaluating the top 20 retrieved results. |
| **LLM** | **Gemini 1.5 Pro** or **GPT-4o** | Use Gemini for its 1M+ context window to handle massive PDF notes. |

---

## 4. Key Precautions & Challenges (Critical for Thesis)

### A. The "Lost in the Middle" Phenomenon
When you provide too much context (e.g., a whole semester of notes), LLMs tend to forget information in the middle of the text.
* **Fix:** Use a **Reranker** to ensure only the most relevant 5-7 chunks are sent to the LLM, rather than dumping everything.

### B. Context Fragmentation
If you cut a note in the middle of a formula or a proof, the RAG will fail.
* **Fix:** Use **Markdown-aware splitting** or **Semantic Chunking** (breaking text based on changes in meaning rather than character count).

### C. Hallucination in Quizzes
AI might invent facts or create "correct" answers that aren't in the notes.
* **Fix:** Implement a **Self-Correction Loop**. Have a second "Evaluator Agent" check the generated Quiz against the original Source Snippets before showing it to the user.

### D. Cost & Latency
GraphRAG and Recursive Summaries are expensive and slow (they require many LLM calls).
* **Fix:** Perform Indexing **asynchronously**. When a user uploads a PDF, show a loading bar and process the Graph/Summary in the background.

---

## 5. Summary of the Workflow for your TFM

1.  **Ingestion:** PDF -> Markdown Conversion -> Semantic Chunking.
2.  **Indexing:** Build Vector Embeddings + Extract Knowledge Graph + Build Summary Tree.
3.  **Interaction:** * User asks for a summary? Router -> Summary Tree.
    * User asks for a Quiz? Agent -> Graph Nodes -> Distractor Generation -> Quiz JSON.
4.  **Frontend:** Next.js fetches the JSON and renders interactive cards.

**Final Advice for your Thesis:** Focus your "Innovation" section on the **Hybrid Retrieval** (how you combined Graph and Vector to solve the summary problem). This is a very "hot" topic in AI research right now.

Do you need a specific code snippet for the **FastAPI + LlamaIndex** routing logic to get your backend started?