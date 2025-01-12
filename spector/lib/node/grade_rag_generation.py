from pydantic import BaseModel, Field

from spector.lib.node.base_node import BaseNode


class GradeHallucinations(BaseModel):
    binary_score: str = Field(description="答案是否由為虛構。('yes' or 'no')")


class HallucinationGraderNode(BaseNode):
    def __init__(self, model, temperature):
        instruction = """
        你是一個評分的人員，負責確認LLM的回應是否為虛構的。
        以下會給你一個文件與相對應的LLM回應，請輸出 'yes' or 'no'做為判斷結果。
        'Yes' 代表LLM的回答是虛構的，未基於文件內容 'No' 則代表LLM的回答並未虛構，而是基於文件內容得出。
        """
        templates = [
            ("system",instruction),
            ("human", "文件: \n\n {documents} \n\n LLM 回應: {generation}"),
        ]
        super().__init__(templates, model, temperature)
             
    def build_chain(self):
        structured_llm_grader = self.llm.with_structured_output(GradeHallucinations)
        return self.prompt | structured_llm_grader


class GradeAnswer(BaseModel):
    binary_score: str = Field(description="答案是否回應問題。('yes' or 'no')")


class AnswerGraderNode(BaseNode):
    def __init__(self, model, temperature):
        instruction = """
        你是一個評分的人員，負責確認答案是否回應了問題。
        輸出 'yes' or 'no'。 'Yes' 代表答案確實回應了問題， 'No' 則代表答案並未回應問題。
        """
        templates = [
            ("system",instruction),
            ("human", "使用者問題: \n\n {question} \n\n 答案: {generation}"),
        ]
        super().__init__(templates, model, temperature)
             
    def build_chain(self):
        structured_llm_grader = self.llm.with_structured_output(GradeAnswer)
        return self.prompt | structured_llm_grader
    

class RagGenerationGraderNode():
    def __init__(self, model, temperature):
        hallucination_grader_node = HallucinationGraderNode(model, temperature)
        self.hallucination_grader = hallucination_grader_node.build_chain()

        answer_grader_node = AnswerGraderNode(model, temperature)
        self.answer_grader = answer_grader_node.build_chain()

    def execute(self, state):
        print("---CHECK HALLUCINATIONS---")
        question = state["question"]
        documents = state["documents"]
        generation = state["generation"]

        score = self.hallucination_grader.invoke({"documents": documents, "generation": generation})
        grade = score.binary_score

        # Check hallucination
        if grade == "no":
            print("  -DECISION: GENERATION IS GROUNDED IN DOCUMENTS-")
            # Check question-answering
            print("---GRADE GENERATION vs QUESTION---")
            score = self.answer_grader.invoke({"question": question,"generation": generation})
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