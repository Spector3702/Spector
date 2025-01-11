import os

from typing_extensions import TypedDict
from typing import List
from langchain.schema import Document
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.tools.tavily_search import TavilySearchResults

from vectorstore import create_vectorstore
from question_router import create_question_router
from plain import create_plain_llm
from rag_grader import create_rag_grader
from rag_responder import create_rag_responder
from hallucination_grader import create_hallucination_grader
from answer_grader import create_answer_grader


os.environ["OPENAI_API_KEY"] = "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"
os.environ['TAVILY_API_KEY'] = "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"


question_router = create_question_router()

vector_store = create_vectorstore()
web_search_tool = TavilySearchResults(include_domains=["https://www.leagueoflegends.com/zh-tw/champions/"])
plain = create_plain_llm()

rag_grader = create_rag_grader()

rag_responder = create_rag_responder()

hallucination_grader = create_hallucination_grader()

answer_grader = create_answer_grader()


class GraphState(TypedDict):
    question : str
    generation : str
    documents : List[str]


def route_question(state):
    print("---ROUTE QUESTION---")
    question = state["question"]
    source = question_router.invoke({"question": question})

    # Fallback to plain LLM or raise error if no decision
    if "tool_calls" not in source.additional_kwargs:
        print("  -ROUTE TO PLAIN LLM-")
        return "plain_answer"
    if len(source.additional_kwargs["tool_calls"]) == 0:
      raise "Router could not decide source"

    # Choose datasource
    datasource = source.additional_kwargs["tool_calls"][0]["function"]["name"]
    if datasource == 'web_search':
        print("  -ROUTE TO WEB SEARCH-")
        return "web_search"
    elif datasource == 'vectorstore':
        print("  -ROUTETO VECTORSTORE-")
        return "vectorstore"


def plain_answer(state):
    print("---GENERATE PLAIN ANSWER---")
    question = state["question"]
    generation = plain.invoke({"question": question})
    return {"question": question, "generation": generation}


def retrieve(state):
    print("---RETRIEVE---")
    question = state["question"]
    documents = vector_store.invoke(question)

    return {"documents":documents, "question":question}


def web_search(state):
    print("---WEB SEARCH---")
    question = state["question"]
    documents = state.get("documents", [])

    docs = web_search_tool.invoke({"query": question})
    web_results = [Document(page_content=d["content"]) for d in docs]

    documents = documents + web_results

    return {"documents": documents, "question": question}


def retrieval_grade(state):
    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")

    documents = state["documents"]
    question = state["question"]

    # Score each doc
    filtered_docs = []
    for d in documents:
        score = rag_grader.invoke({"question": question, "document": d.page_content})
        grade = score.binary_score
        if grade == "yes":
            print("  -GRADE: DOCUMENT RELEVANT-")
            filtered_docs.append(d)
        else:
            print("  -GRADE: DOCUMENT NOT RELEVANT-")
            continue
    return {"documents": filtered_docs, "question": question}


def route_rag(state):
    print("---ROUTE RAG---")
    filtered_documents = state["documents"]

    if not filtered_documents:
        # All documents have been filtered check_relevance
        print("  -DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, ROUTE TO WEB SEARCH-")
        return "web_search"
    else:
        # We have relevant documents, so generate answer
        print("  -DECISION: GENERATE WITH RAG LLM-")
        return "rag_generate"


def rag_generate(state):
    print("---GENERATE IN RAG MODE---")
    question = state["question"]
    documents = state["documents"]

    generation = rag_responder.invoke({"documents": documents, "question": question})
    return {"documents": documents, "question": question, "generation": generation}


def grade_rag_generation(state):
    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader.invoke({"documents": documents, "generation": generation})
    grade = score.binary_score

    # Check hallucination
    if grade == "no":
        print("  -DECISION: GENERATION IS GROUNDED IN DOCUMENTS-")
        # Check question-answering
        print("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke({"question": question,"generation": generation})
        grade = score.binary_score
        if grade == "yes":
            print("  -DECISION: GENERATION ADDRESSES QUESTION-")
            return "useful"
        else:
            print("  -DECISION: GENERATION DOES NOT ADDRESS QUESTION-")
            return "not useful"
    else:
        print("  -DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY-")
        return "not supported"
    

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