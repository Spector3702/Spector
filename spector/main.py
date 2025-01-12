import os
os.environ["OPENAI_API_KEY"] = "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"
os.environ['TAVILY_API_KEY'] = "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"

from typing_extensions import TypedDict
from typing import List
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from lib.route_question import RouteQuestionNode
from lib.web_search import WebSearchNode
from lib.retrieve import RetrieveNode
from lib.retrieval_grade import RagGraderNode
from lib.route_rag import RouteRagNode
from lib.rag_generate import RagGenerateNode
from lib.grade_rag_generation import RagGenerationGraderNode
from lib.plain_answer import PlainGenerationNode


MODEL = 'gpt-4o-mini'
TEMPERATURE = 0
class GraphState(TypedDict):
    question : str
    generation : str
    documents : List[str]
    

workflow = StateGraph(GraphState)

web_search_node = WebSearchNode()
workflow.add_node("web_search", web_search_node.execute)

retrieve_node = RetrieveNode()
workflow.add_node("retrieve", retrieve_node.execute)

plain_answer_node = PlainGenerationNode(MODEL, TEMPERATURE)
workflow.add_node("plain_answer", plain_answer_node.execute)

rag_grader_node = RagGraderNode(MODEL, TEMPERATURE)
workflow.add_node("rag_grader", rag_grader_node.execute)

rag_generate_node = RagGenerateNode(MODEL, TEMPERATURE)
workflow.add_node("rag_generate", rag_generate_node.execute)

route_question_node = RouteQuestionNode(MODEL, TEMPERATURE)
workflow.set_conditional_entry_point(
    route_question_node.execute,
    {
        "web_search": "web_search",
        "vectorstore": "retrieve",
        "plain_answer": "plain_answer",
    },
)
workflow.add_edge("retrieve", "rag_grader")
workflow.add_edge("web_search", "rag_grader")

route_rag_node = RouteRagNode()
workflow.add_conditional_edges(
    "rag_grader",
    route_rag_node.execute,
    {
        "web_search": "web_search",
        "rag_generate": "rag_generate",
    },
)

rag_generation_grader = RagGenerationGraderNode(MODEL, TEMPERATURE)
workflow.add_conditional_edges(
    "rag_generate",
    rag_generation_grader.execute,
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