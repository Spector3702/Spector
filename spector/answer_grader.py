from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI


class GradeAnswer(BaseModel):
    binary_score: str = Field(description="答案是否回應問題。('yes' or 'no')")


def create_answer_grader():
    instruction = """
    你是一個評分的人員，負責確認答案是否回應了問題。
    輸出 'yes' or 'no'。 'Yes' 代表答案確實回應了問題， 'No' 則代表答案並未回應問題。
    """

    answer_prompt = ChatPromptTemplate.from_messages(
        [
            ("system",instruction),
            ("human", "使用者問題: \n\n {question} \n\n 答案: {generation}"),
        ]
    )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm_grader = llm.with_structured_output(GradeAnswer)

    answer_grader = answer_prompt | structured_llm_grader

    return answer_grader 