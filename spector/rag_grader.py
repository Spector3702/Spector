from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI


class GradeDocuments(BaseModel):
    binary_score: str = Field(description="請問文章與問題是否相關。('yes' or 'no')")


def create_rag_grader():
    instruction = """
    你是一個評分的人員，負責評估文件與使用者問題的關聯性。
    如果文件包含與使用者問題相關的關鍵字或語意，則將其評為相關。
    輸出 'yes' or 'no' 代表文件與問題的相關與否。
    """
    grade_prompt = ChatPromptTemplate.from_messages(
        [
            ("system",instruction),
            ("human", "文件: \n\n {document} \n\n 使用者問題: {question}"),
        ]
    )

    # Grader LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm_grader = llm.with_structured_output(GradeDocuments)

    # 使用 LCEL 語法建立 chain
    retrieval_grader = grade_prompt | structured_llm_grader

    return retrieval_grader