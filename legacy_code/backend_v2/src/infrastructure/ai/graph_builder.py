from langgraph.graph import END, StateGraph
from src.domain.agent_types import GraphState
from src.infrastructure.ai.agent_nodes import AgentNodes

def get_generation_target(state):
    """
    Helper to determine which generation node to target.
    """
    target = state.get("generation_type", "answer")
    if target == "quiz":
        return "generate_quiz"
    elif target == "flashcards":
        return "generate_flashcards"
    else:
        return "generate"

def decide_to_generate(state):
    """
    Determines whether to generate an answer, or re-generate a question.
    """
    print("---ASSESS GRADED DOCUMENTS---")
    filtered_documents = state.get("documents", [])
    transform_count = state.get("transform_count", 0)

    if not filtered_documents:
        if transform_count >= 3:
             print("---DECISION: RECURSION LIMIT REACHED - FORCING GENERATION---")
             return get_generation_target(state)
             
        print("---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---")
        return "transform_query"
    else:
        print("---DECISION: GENERATE---")
        return get_generation_target(state)

def check_hallucination(state):
    """
    Check hallucination status
    """
    print("---CHECK HALLUCINATION STATUS---")
    status = state.get("hallucination_status")
    
    # Check max retries
    loop_count = state.get("loop_count", 0)
    if loop_count >= 3:
        print("---DECISION: MAX RETRIES REACHED---")
        return "max_retries"

    if status == "grounded":
        return "grounded"
    else:
        return "hallucinated"

def decide_regeneration(state):
    """
    Decide where to loop back for regeneration
    """
    return get_generation_target(state)

def check_answer(state):
    """
    Check answer status
    """
    print("---CHECK ANSWER STATUS---")
    status = state.get("answer_status")
    if status == "useful":
        return "useful"
    else:
        return "not_useful"

def build_graph():
    """
    Build the LangGraph workflow
    """
    nodes = AgentNodes()
    
    workflow = StateGraph(GraphState)

    # Define the nodes
    workflow.add_node("retrieve", nodes.retrieve)
    workflow.add_node("grade_documents", nodes.grade_documents)
    
    workflow.add_node("generate", nodes.generate)
    workflow.add_node("generate_quiz", nodes.generate_quiz)
    workflow.add_node("generate_flashcards", nodes.generate_flashcards)
    
    workflow.add_node("grade_hallucination", nodes.grade_hallucination)
    workflow.add_node("grade_answer", nodes.grade_answer)
    workflow.add_node("prepare_for_retry", nodes.prepare_for_retry)
    workflow.add_node("transform_query", nodes.transform_query)

    # Build graph
    workflow.set_entry_point("retrieve")
    
    workflow.add_edge("retrieve", "grade_documents")
    
    # Grade Docs -> [Generate (if docs) OR Transform Query (if no docs)]
    workflow.add_conditional_edges(
        "grade_documents",
        decide_to_generate,
        {
            "transform_query": "transform_query",
            "generate": "generate",
            "generate_quiz": "generate_quiz",
            "generate_flashcards": "generate_flashcards",
        }
    )
    
    # Transform Query -> Retrieve (Loop)
    workflow.add_edge("transform_query", "retrieve")
    
    # Generate -> Grade Hallucination
    workflow.add_edge("generate", "grade_hallucination")
    workflow.add_edge("generate_quiz", "grade_hallucination")
    workflow.add_edge("generate_flashcards", "grade_hallucination")
    
    # Grade Hallucination -> [Grounded->AnswerCheck, Hallucinated->Retry, Max->End]
    workflow.add_conditional_edges(
        "grade_hallucination",
        check_hallucination,
        {
            "grounded": "grade_answer",
            "hallucinated": "prepare_for_retry",
            "max_retries": END
        }
    )
    
    # Retry -> Generate
    workflow.add_conditional_edges(
        "prepare_for_retry",
        decide_regeneration,
        {
             "generate": "generate",
             "generate_quiz": "generate_quiz",
             "generate_flashcards": "generate_flashcards"
        }
    )
    
    # Answer Check -> End (Could optimize to loop back to transform_query if not useful, but sticking to current scope)
    workflow.add_conditional_edges(
        "grade_answer",
        check_answer,
        {
            "useful": END,
            "not_useful": END 
        }
    )

    # Compile
    app = workflow.compile()
    return app
