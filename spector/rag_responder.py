from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def create_rag_responder():
    instruction = """
    你是一位負責處理使用者問題的助手，請利用提取出來的文件內容來回應問題。
    若問題的答案無法從文件內取得，請直接回覆你不知道，禁止虛構答案。
    注意：請確保答案的準確性。
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system",instruction),
            ("system","文件: \n\n {documents}"),
            ("human","問題: {question}"),
        ]
    )

    # LLM & chain
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    rag_chain = prompt | llm | StrOutputParser()

    return rag_chain