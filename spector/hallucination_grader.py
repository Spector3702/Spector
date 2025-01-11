from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI


class GradeHallucinations(BaseModel):
    binary_score: str = Field(description="答案是否由為虛構。('yes' or 'no')")


def create_hallucination_grader():
    instruction = """
    你是一個評分的人員，負責確認LLM的回應是否為虛構的。
    以下會給你一個文件與相對應的LLM回應，請輸出 'yes' or 'no'做為判斷結果。
    'Yes' 代表LLM的回答是虛構的，未基於文件內容 'No' 則代表LLM的回答並未虛構，而是基於文件內容得出。
    """
    hallucination_prompt = ChatPromptTemplate.from_messages(
        [
            ("system",instruction),
            ("human", "文件: \n\n {documents} \n\n LLM 回應: {generation}"),
        ]
    )


    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm_grader = llm.with_structured_output(GradeHallucinations)

    hallucination_grader = hallucination_prompt | structured_llm_grader

    return hallucination_grader