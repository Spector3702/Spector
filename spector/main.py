import os
os.environ["OPENAI_API_KEY"] = "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"
os.environ['TAVILY_API_KEY'] = "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"

from typing_extensions import TypedDict
from typing import List
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from lib.route_question import route_question
from lib.web_search import web_search
from lib.retrieve import retrieve
from lib.retrieval_grade import retrieval_grade
from lib.route_rag import route_rag
from lib.rag_generate import rag_generate
from lib.grade_rag_generation import grade_rag_generation
from lib.plain_answer import plain_answer


class GraphState(TypedDict):
    question : str
    generation : str
    documents : List[str]
    

workflow = StateGraph(GraphState)

workflow.add_node("web_search", web_search)
workflow.add_node("retrieve", retrieve)
workflow.add_node("retrieval_grade", retrieval_grade)
workflow.add_node("rag_generate", rag_generate)
workflow.add_node("plain_answer", plain_answer)

workflow.set_conditional_entry_point(
    route_question,
    {
        "web_search": "web_search",
        "vectorstore": "retrieve",
        "plain_answer": "plain_answer",
    },
)
workflow.add_edge("retrieve", "retrieval_grade")
workflow.add_edge("web_search", "retrieval_grade")
workflow.add_conditional_edges(
    "retrieval_grade",
    route_rag,
    {
        "web_search": "web_search",
        "rag_generate": "rag_generate",
    },
)
workflow.add_conditional_edges(
    "rag_generate",
    grade_rag_generation,
    {
        "not supported": "rag_generate", # Hallucinations: re-generate
        "not useful": "web_search", # Fails to answer question: fall-back to web-search
        "useful": END,
    },
)
workflow.add_edge("plain_answer", END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

inputs = {"question": "阿卡利的技能是什麼？"}
config = {"configurable": {"thread_id": "abc123"}}

for output in app.stream(inputs, config):
    print("\n")

# Final generation
if 'rag_generate' in output.keys():
    print(output['rag_generate']['generation'])
elif 'plain_answer' in output.keys():
    print(output['plain_answer']['generation'])