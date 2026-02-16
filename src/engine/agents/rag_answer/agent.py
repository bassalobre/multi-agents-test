from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from src.engine.agents.rag_answer.system_prompt import RAG_ANSWER_SYSTEM_PROMPT
from src.engine.agents.rag_answer.model import RAGAnswerOutput
from src.engine.llm import get_llm

class RAGAnswerAgent:
    def __init__(self):
        self.llm = get_llm()
        self.parser = PydanticOutputParser(pydantic_object=RAGAnswerOutput)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", RAG_ANSWER_SYSTEM_PROMPT),
            ("human", """User Question:
{question}

Retrieved Context:
{context}

Analyze the context and provide the answer in JSON format:""")
        ])
        
        self.chain = self.prompt | self.llm | self.parser

    def invoke(self, question: str, context: str) -> RAGAnswerOutput:
        return self.chain.invoke({
            "question": question,
            "context": context,
            "format_instructions": self.parser.get_format_instructions()
        })
