from langchain_core.output_parsers import StrOutputParser

from spector.lib.base_node import BaseNode

class RagGenerateNode(BaseNode):
    def __init__(self, model, temperature):
        instruction = """
        你是一位負責處理使用者問題的助手，請利用提取出來的文件內容來回應問題。
        若問題的答案無法從文件內取得，請直接回覆你不知道，禁止虛構答案。
        注意：請確保答案的準確性。
        """
        templates = [
            ("system",instruction),
            ("system","文件: \n\n {documents}"),
            ("human","問題: {question}"),
        ]
        super().__init__(templates, model, temperature)

    def build_chain(self):
        return self.prompt | self.llm | StrOutputParser()

    def execute(self, state):
        print("---GENERATE IN RAG MODE---")
        question = state["question"]
        documents = state["documents"]

        generation = self.build_chain().invoke({"documents": documents, "question": question})
        return {"documents": documents, "question": question, "generation": generation}
