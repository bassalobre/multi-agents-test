from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.engine.llm import get_llm

class DirectAnswerAgent:
    def __init__(self):
        self.llm = get_llm(temperature=0.7)
        self.parser = StrOutputParser()
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful and friendly AI assistant.
Your goal is to answer the user's question directly, concisely, and politely.
You are NOT to use external tools or retrieval. Just use your general knowledge.

If the user greets you, greet them back warmly.
If the user asks a general question (e.g., "What is Python?"), answer it clearly.

Keep your answers helpful but concise.
            """),
            ("human", "{query}")
        ])
        
        self.chain = self.prompt | self.llm | self.parser

    def invoke(self, query: str) -> str:
        return self.chain.invoke({"query": query})
