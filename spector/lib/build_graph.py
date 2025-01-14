from typing_extensions import TypedDict, Annotated
from typing import List, Sequence
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.postgres import PostgresSaver

from spector.lib.node.route_question import RouteQuestionNode
from spector.lib.node.web_search import WebSearchNode
from spector.lib.node.retrieve import RetrieveNode
from spector.lib.node.retrieval_grade import RagGraderNode
from spector.lib.node.route_rag import RouteRagNode
from spector.lib.node.rag_generate import RagGenerateNode
from spector.lib.node.grade_rag_generation import RagGenerationGraderNode
from spector.lib.node.plain_answer import PlainGenerationNode


MODEL = "gpt-4o-mini"
TEMPERATURE = 0


class GraphState(TypedDict):
    question: Annotated[Sequence[BaseMessage], add_messages]
    generation: str
    documents: List[str]


def build_graph(connection_pool):
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
            "not supported": "rag_generate",  # Hallucinations: re-generate
            "not useful": "web_search",  # Fails to answer question: fall-back to web-search
            "useful": END,
        },
    )
    workflow.add_edge("plain_answer", END)

    postgres_saver = PostgresSaver(connection_pool)
    postgres_saver.setup()
    graph = workflow.compile(checkpointer=postgres_saver)

    return graph
