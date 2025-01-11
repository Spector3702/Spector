from langchain_core.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser


instruction = """
你是一位負責處理使用者問題的助手，請利用你的知識來回應問題。
回應問題時請確保答案的準確性，勿虛構答案。
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system",instruction),
        ("human","問題: {question}"),
    ]
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_chain = prompt | llm | StrOutputParser()


def plain_answer(state):
    print("---GENERATE PLAIN ANSWER---")
    question = state["question"]
    generation = llm_chain.invoke({"question": question})
    return {"question": question, "generation": generation}