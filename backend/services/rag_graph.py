from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END

# Minimal state for the graph
class RAGState(TypedDict, total=False):
    question: str
    embedding: List[float]
    docs: List[Dict[str, Any]]
    answer: str


def build_graph(llm_service, vector_client):
    def embed_node(state: RAGState) -> RAGState:
        q = state.get("question", "") or ""
        state["embedding"] = llm_service.get_embedding(q)
        return state

    def retrieve_node(state: RAGState) -> RAGState:
        emb = state.get("embedding")
        if not emb:
            state["docs"] = []
            return state
        matches = vector_client.query_similar(emb, top_k=5)
        state["docs"] = matches
        return state

    def answer_node(state: RAGState) -> RAGState:
        docs = state.get("docs", []) or []
        context_text = "\n".join(d.get("content", "") for d in docs if d.get("content"))
        q = state.get("question", "") or ""
        prompt = f"Context:\n{context_text}\n\nQuestion: {q}"
        state["answer"] = llm_service.get_response(prompt)
        return state

    graph = StateGraph(RAGState)
    graph.add_node("embed", embed_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("answer", answer_node)

    graph.set_entry_point("embed")
    graph.add_edge("embed", "retrieve")
    graph.add_edge("retrieve", "answer")
    graph.add_edge("answer", END)

    return graph.compile()
