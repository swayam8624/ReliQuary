"""
Agent Nodes Package for ReliQuary Multi-Agent Consensus System

This package contains specialized agent implementations that participate in
distributed consensus for access control decisions.
"""

import warnings

from langchain_core._api.deprecation import LangChainPendingDeprecationWarning

warnings.filters = [
    filter_entry
    for filter_entry in warnings.filters
    if not (
        filter_entry[0] == "default"
        and filter_entry[2] is LangChainPendingDeprecationWarning
    )
]
warnings.simplefilter("ignore", LangChainPendingDeprecationWarning, append=False)

from .neutral_agent import NeutralAgent, NeutralDecisionState, DecisionConfidence
from .permissive_agent import PermissiveAgent, PermissiveDecisionState
from .strict_agent import StrictAgent, StrictDecisionState
from .watchdog_agent import WatchdogAgent, WatchdogDecisionState, ThreatLevel

__all__ = [
    "NeutralAgent",
    "NeutralDecisionState",
    "DecisionConfidence",
    "PermissiveAgent", 
    "PermissiveDecisionState",
    "StrictAgent",
    "StrictDecisionState",
    "WatchdogAgent",
    "WatchdogDecisionState",
    "ThreatLevel"
]
