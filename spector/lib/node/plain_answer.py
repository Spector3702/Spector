from langchain_core.output_parsers import StrOutputParser

from spector.lib.node.base_node import BaseNode


class PlainGenerationNode(BaseNode):
    def __init__(self, model, temperature):
        instruction = """
        你是一位負責處理使用者問題的助手，請利用你的知識來回應問題。
        回應問題時請確保答案的準確性，勿虛構答案。
        """
        templates = [
            ("system",instruction),
            ("human","問題: {question}"),
        ]
        super().__init__(templates, model, temperature)

    def build_chain(self):
        return self.prompt | self.llm | StrOutputParser()

    def execute(self, state):
        print("---GENERATE PLAIN ANSWER---")
        question = state["question"]
        generation = self.build_chain().invoke({"question": question})
        return {"question": question, "generation": generation}