from langchain.schema import Document
from langchain_community.tools.tavily_search import TavilySearchResults


class WebSearchNode():
    def __init__(self):
        self.web_search_tool = TavilySearchResults(
            include_domains=[
                "https://law.moj.gov.tw/"
            ]
        )

    def execute(self, state):
        print("---WEB SEARCH---")
        question = state["question"]
        documents = state.get("documents", [])
        query = question[-1].content

        docs = self.web_search_tool.invoke({"query": query})
        print("docs: ", docs)
        web_results = [Document(page_content=d["content"]) for d in docs]

        documents = documents + web_results

        return {"documents": documents, "question": question}