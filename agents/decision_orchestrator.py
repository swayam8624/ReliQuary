"""
Decision Orchestrator for ReliQuary Multi-Agent System.
This module orchestrates the overall agent decision process.
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# Import agent nodes
try:
    from agents.nodes.neutral_agent import NeutralAgent
    from agents.nodes.permissive_agent import PermissiveAgent
    from agents.nodes.strict_agent import StrictAgent
    from agents.nodes.watchdog_agent import WatchdogAgent
except ImportError:
    # Mock implementations for development
    class NeutralAgent:
        def __init__(self):
            self.name = "neutral"
        
        async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "agent": self.name,
                "vote": "approve",
                "confidence": 0.7,
                "reasoning": "Neutral assessment based on context"
            }
    
    class PermissiveAgent:
        def __init__(self):
            self.name = "permissive"
        
        async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "agent": self.name,
                "vote": "approve",
                "confidence": 0.8,
                "reasoning": "Permissive assessment, allowing access"
            }
    
    class StrictAgent:
        def __init__(self):
            self.name = "strict"
        
        async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "agent": self.name,
                "vote": "approve",
                "confidence": 0.9,
                "reasoning": "Strict verification passed"
            }
    
    class WatchdogAgent:
        def __init__(self):
            self.name = "watchdog"
        
        async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "agent": self.name,
                "vote": "approve",
                "confidence": 0.85,
                "reasoning": "Security checks passed"
            }


class DecisionOutcome(Enum):
    """Possible outcomes of a decision process"""
    APPROVED = "approved"
    DENIED = "denied"
    PENDING = "pending"
    ERROR = "error"


@dataclass
class DecisionContext:
    """Context for decision making"""
    decision_type: str
    user_id: str
    resource_path: str
    context_data: Dict[str, Any]
    priority: int = 5
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class DecisionResult:
    """Result of a decision process"""
    decision: DecisionOutcome
    confidence: float
    agents_consulted: List[str]
    detailed_votes: Dict[str, Any]
    reasoning: str
    risk_assessment: Dict[str, Any]
    timestamp: datetime


class DecisionOrchestrator:
    """Orchestrates the overall agent decision process"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.agents = {
            "neutral": NeutralAgent(),
            "permissive": PermissiveAgent(),
            "strict": StrictAgent(),
            "watchdog": WatchdogAgent()
        }
    
    async def make_decision(self, context: Dict[str, Any], user_id: str, resource_path: str) -> Dict[str, Any]:
        """
        Make a decision by consulting multiple agents.
        
        Args:
            context: Context data for decision making
            user_id: ID of the user requesting access
            resource_path: Path to the resource being accessed
            
        Returns:
            Dictionary containing the decision result
        """
        try:
            # Create decision context
            decision_context = DecisionContext(
                decision_type=context.get("decision_type", "access_request"),
                user_id=user_id,
                resource_path=resource_path,
                context_data=context.get("context_data", {}),
                priority=context.get("priority", 5),
                metadata=context.get("metadata")
            )
            
            # Consult all agents concurrently
            agent_votes = await self._consult_agents(decision_context)
            
            # Aggregate votes to make final decision
            final_decision = self._aggregate_votes(agent_votes, decision_context)
            
            # Prepare result
            result = {
                "decision": final_decision.decision.value,
                "confidence": final_decision.confidence,
                "agents_consulted": final_decision.agents_consulted,
                "detailed_votes": final_decision.detailed_votes,
                "reasoning": final_decision.reasoning,
                "risk_assessment": final_decision.risk_assessment,
                "timestamp": final_decision.timestamp.isoformat()
            }
            
            self.logger.info(f"Decision made: {result['decision']} with confidence {result['confidence']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Decision making failed: {str(e)}")
            return {
                "decision": DecisionOutcome.ERROR.value,
                "confidence": 0.0,
                "agents_consulted": [],
                "detailed_votes": {},
                "reasoning": f"Error occurred during decision making: {str(e)}",
                "risk_assessment": {},
                "timestamp": datetime.now().isoformat()
            }
    
    async def _consult_agents(self, context: DecisionContext) -> List[Dict[str, Any]]:
        """
        Consult all available agents for their votes.
        
        Args:
            context: Decision context
            
        Returns:
            List of agent votes
        """
        # Create tasks for all agents
        tasks = []
        for agent_name, agent in self.agents.items():
            task = asyncio.create_task(
                agent.evaluate({
                    "decision_type": context.decision_type,
                    "user_id": context.user_id,
                    "resource_path": context.resource_path,
                    "context_data": context.context_data,
                    "priority": context.priority,
                    "metadata": context.metadata
                }),
                name=agent_name
            )
            tasks.append(task)
        
        # Execute all tasks concurrently
        votes = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_votes = []
        for i, vote in enumerate(votes):
            agent_name = list(self.agents.keys())[i]
            if isinstance(vote, Exception):
                self.logger.warning(f"Agent {agent_name} failed to provide vote: {str(vote)}")
                processed_votes.append({
                    "agent": agent_name,
                    "vote": "error",
                    "confidence": 0.0,
                    "reasoning": str(vote)
                })
            else:
                processed_votes.append(vote)
        
        return processed_votes
    
    def _aggregate_votes(self, votes: List[Dict[str, Any]], context: DecisionContext) -> DecisionResult:
        """
        Aggregate agent votes to make a final decision.
        
        Args:
            votes: List of agent votes
            context: Decision context
            
        Returns:
            Final decision result
        """
        # Count votes
        approve_votes = 0
        deny_votes = 0
        total_confidence = 0.0
        agents_consulted = []
        
        for vote in votes:
            agents_consulted.append(vote["agent"])
            if vote["vote"] == "approve":
                approve_votes += 1
                total_confidence += vote["confidence"]
            elif vote["vote"] == "deny":
                deny_votes += 1
                total_confidence += vote["confidence"]
        
        # Make decision based on majority vote
        if approve_votes > deny_votes:
            decision = DecisionOutcome.APPROVED
            reasoning = "Majority of agents approved the request"
        elif deny_votes > approve_votes:
            decision = DecisionOutcome.DENIED
            reasoning = "Majority of agents denied the request"
        else:
            # Tie breaker - use average confidence
            decision = DecisionOutcome.APPROVED if approve_votes > 0 else DecisionOutcome.DENIED
            reasoning = "Tie breaker applied"
        
        # Calculate average confidence
        avg_confidence = total_confidence / len(votes) if votes else 0.0
        
        # Simple risk assessment
        risk_assessment = {
            "risk_level": "low" if avg_confidence > 0.7 else "medium" if avg_confidence > 0.5 else "high",
            "approval_rate": approve_votes / len(votes) if votes else 0.0,
            "agent_consensus": f"{approve_votes}/{len(votes)} agents approved"
        }
        
        return DecisionResult(
            decision=decision,
            confidence=avg_confidence,
            agents_consulted=agents_consulted,
            detailed_votes={vote["agent"]: vote for vote in votes},
            reasoning=reasoning,
            risk_assessment=risk_assessment,
            timestamp=datetime.now()
        )


# Global decision orchestrator instance
_decision_orchestrator = None


def get_decision_orchestrator() -> DecisionOrchestrator:
    """Get the global decision orchestrator instance"""
    global _decision_orchestrator
    if _decision_orchestrator is None:
        _decision_orchestrator = DecisionOrchestrator()
    return _decision_orchestrator


async def make_agent_decision(context: Dict[str, Any], user_id: str, resource_path: str) -> Dict[str, Any]:
    """Convenience function to make an agent decision"""
    orchestrator = get_decision_orchestrator()
    return await orchestrator.make_decision(context, user_id, resource_path)