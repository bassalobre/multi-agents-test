from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from src.engine.agents.compliance.model import ComplianceInput, ComplianceOutput
from src.engine.agents.compliance.system_prompt import COMPLIANCE_SYSTEM_PROMPT
from src.engine.llm import get_llm

class ComplianceAgent:
    def __init__(self):
        self.llm = get_llm()
        self.parser = PydanticOutputParser(pydantic_object=ComplianceOutput)
        
        self.semantic_blocklist = [
            "ignore previous instructions",
            "system override",
            "act as DAN",
            "make a bomb",
            "child porn",
            "credit card generator"
        ]

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", COMPLIANCE_SYSTEM_PROMPT),
            ("human", """Input to Analyze:
\"\"\"
{query}
\"\"\"

Context/Metadata:
- User Role: {user_role}

Analyze the input above. JSON Output:""")
        ])
        
        self.chain = self.prompt | self.llm | self.parser

    def heuristic_check(self, query: str) -> Optional[ComplianceOutput]:
        """Fast-fail check for obvious blocks"""
        query_lower = query.lower()
        for term in self.semantic_blocklist:
            if term in query_lower:
                return ComplianceOutput(
                    is_safe=False,
                    reason=f"Blocked by heuristic: contains prohibited term '{term}'",
                    category="heuristic_block",
                    risk_level="high"
                )
        if len(query) > 10000:
             return ComplianceOutput(
                is_safe=False,
                reason="Blocked by heuristic: Input too long",
                category="dos_protection",
                risk_level="medium"
            )
        return None

    def invoke(self, input_data: ComplianceInput) -> ComplianceOutput:
        heuristic_result = self.heuristic_check(input_data.query)
        if heuristic_result:
            return heuristic_result
            
        return self.chain.invoke({
            "query": input_data.query,
            "user_role": input_data.user_role,
            "format_instructions": self.parser.get_format_instructions()
        })
