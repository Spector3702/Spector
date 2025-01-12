from langchain_core.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI


class BaseNode():
    def __init__(self, templates, model, temperature):
        self.prompt = self._build_prompt(templates)
        self.llm = self._build_llm(model, temperature)

    def _build_prompt(self, templates):
        return ChatPromptTemplate.from_messages(templates)
    
    def _build_llm(self, model, temperature):
        return ChatOpenAI(model=model, temperature=temperature)
    
    def build_chain(self):
        pass
        
    def execute(self, state):
        pass