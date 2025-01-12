from pydantic import BaseModel, Field

from spector.lib.base_node import BaseNode


class web_search(BaseModel):
    query: str = Field(description="使用網路搜尋時輸入的問題")

class vectorstore(BaseModel):
    query: str = Field(description="搜尋向量資料庫時輸入的問題")


class RouteQuestionNode(BaseNode):
    def __init__(self, model, temperature):
        instruction = """
        你是將使用者問題導向向量資料庫或網路搜尋的專家。
        向量資料庫包含有關愛情文件。對於這些主題的問題，請使用向量資料庫工具。其他情況則使用網路搜尋工具。
        """
        templates = [
            ("system",instruction),
            ("human", "{question}"),
        ]
        super().__init__(templates, model, temperature)

    def build_chain(self):
        structured_llm_router = self.llm.bind_tools(tools=[web_search, vectorstore])
        return self.prompt | structured_llm_router

    def execute(self, state):
        print("---ROUTE QUESTION---")
        question = state["question"]
        source = self.build_chain().invoke({"question": question})

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