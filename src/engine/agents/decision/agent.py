from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from src.engine.agents.decision.system_prompt import DECISION_SYSTEM_PROMPT
from src.engine.agents.decision.model import DecisionOutput
from src.engine.llm import get_llm

class DecisionAgent:
    def __init__(self):
        self.llm = get_llm()
        self.parser = PydanticOutputParser(pydantic_object=DecisionOutput)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", DECISION_SYSTEM_PROMPT),
            ("human", """Input to Analyze:
\"\"\"
{query}
\"\"\"

Analyze the input above. JSON Output:""")
        ])
        
        self.chain = self.prompt | self.llm | self.parser

    def invoke(self, query: str) -> DecisionOutput:
        return self.chain.invoke({
            "query": query,
            "format_instructions": self.parser.get_format_instructions()
        })
