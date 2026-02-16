import json

from typing import Dict, Any, Optional

from src.engine.agents.compliance.agent import ComplianceAgent
from src.engine.agents.decision.agent import DecisionAgent
from src.engine.agents.direct_answer.agent import DirectAnswerAgent
from src.engine.agents.rag_answer.agent import RAGAnswerAgent

from src.engine.agents.compliance.model import ComplianceInput
from src.engine.retriever import EngineRetriever
from src.logger import logger

class Orchestrator:
    def __init__(self):
        logger.info("Initializing Orchestrator and sub-agents...")
        self.compliance_agent = ComplianceAgent()
        self.decision_agent = DecisionAgent()
        self.direct_agent = DirectAnswerAgent()
        self.rag_agent = RAGAnswerAgent()

        self.retriever = EngineRetriever()
        logger.info("Orchestrator initialized.")

    def run(self, query: str, user_role: str = "standard") -> Dict[str, Any]:
        """
        Main execution flow:
        1. Compliance Check
        2. Decision Making (Direct vs RAG)
        3. Execution & Answer Generation
        """
        logger.info(f"--- New Request: {query} (Role: {user_role}) ---")

        logger.info("Step 1: Compliance Check")
        compliance_input = ComplianceInput(query=query, user_role=user_role)
        compliance_result = self.compliance_agent.invoke(compliance_input)

        if not compliance_result.is_safe:
            logger.warning(f"Compliance Blocked: {compliance_result.reason}")
            return {
                "status": "blocked",
                "reason": compliance_result.reason,
                "category": compliance_result.category,
                "risk_level": compliance_result.risk_level,
                "answer": f"I cannot answer that request. Reason: {compliance_result.reason}"
            }
        
        safe_query = compliance_result.sanitized_query or query
        logger.info(f"Query is safe. Proceeding with: '{safe_query}'")

        logger.info("Step 2: Decision Making")
        decision_result = self.decision_agent.invoke(safe_query)
        strategy = decision_result.decision
        logger.info(f"Decision: {strategy.upper()} (Reason: {decision_result.reason})")

        if strategy == "direct":
            logger.info("Step 3: Executing Direct Strategy")
            answer = self.direct_agent.invoke(safe_query)
            return {
                "status": "success",
                "strategy": "direct",
                "answer": answer,
                "decision_reason": decision_result.reason
            }
        
        elif strategy == "rag":
            logger.info("Step 3: Executing RAG Strategy")
            
            search_terms = decision_result.search_terms or [safe_query]
            context_str = self.retriever.search(search_terms)

            rag_result = self.rag_agent.invoke(safe_query, context_str)
            
            return {
                "status": "success",
                "strategy": "rag",
                "answer": rag_result.answer,
                "context_sufficient": rag_result.context_sufficient,
                "citations": rag_result.citations,
                "decision_reason": decision_result.reason
            }

        return {
            "status": "error",
            "message": "Unknown strategy"
        }
