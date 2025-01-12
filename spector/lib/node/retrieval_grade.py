from pydantic import BaseModel, Field

from spector.lib.node.base_node import BaseNode


class GradeDocuments(BaseModel):
    binary_score: str = Field(description="請問文章與問題是否相關。('yes' or 'no')")


class RagGraderNode(BaseNode):
    def __init__(self, model, temperature):
        instruction = """
        你是一個評分的人員，負責評估文件與使用者問題的關聯性。
        如果文件包含與使用者問題相關的關鍵字或語意，則將其評為相關。
        輸出 'yes' or 'no' 代表文件與問題的相關與否。
        """
        templates = [
            ("system",instruction),
            ("human", "文件: \n\n {document} \n\n 使用者問題: {question}"),
        ]
        super().__init__(templates, model, temperature)

    def build_chain(self):
        structured_llm_grader = self.llm.with_structured_output(GradeDocuments)
        return self.prompt | structured_llm_grader


    def execute(self, state):
        print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")

        documents = state["documents"]
        question = state["question"]

        # Score each doc
        filtered_docs = []
        for d in documents:
            score = self.build_chain().invoke({"question": question, "document": d.page_content})
            grade = score.binary_score
            if grade == "yes":
                print("  -GRADE: DOCUMENT RELEVANT-")
                filtered_docs.append(d)
            else:
                print("  -GRADE: DOCUMENT NOT RELEVANT-")
                continue
        return {"documents": filtered_docs, "question": question}
