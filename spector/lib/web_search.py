from langchain.schema import Document
from langchain_community.tools.tavily_search import TavilySearchResults


web_search_tool = TavilySearchResults(include_domains=["https://www.leagueoflegends.com/zh-tw/champions/"])


def web_search(state):
    print("---WEB SEARCH---")
    question = state["question"]
    documents = state.get("documents", [])

    docs = web_search_tool.invoke({"query": question})
    web_results = [Document(page_content=d["content"]) for d in docs]

    documents = documents + web_results

    return {"documents": documents, "question": question}