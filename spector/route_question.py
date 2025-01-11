from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI


class web_search(BaseModel):
    query: str = Field(description="使用網路搜尋時輸入的問題")

class vectorstore(BaseModel):
    query: str = Field(description="搜尋向量資料庫時輸入的問題")


instruction = """
你是將使用者問題導向向量資料庫或網路搜尋的專家。
向量資料庫包含有關愛情文件。對於這些主題的問題，請使用向量資料庫工具。其他情況則使用網路搜尋工具。
"""
route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",instruction),
        ("human", "{question}"),
    ]
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
structured_llm_router = llm.bind_tools(tools=[web_search, vectorstore])

question_router = route_prompt | structured_llm_router


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