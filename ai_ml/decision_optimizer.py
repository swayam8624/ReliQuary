"""
Advanced Decision Optimizer and NLP Processor for ReliQuary AI/ML System

This module implements intelligent decision optimization algorithms and natural
language processing capabilities for audit analysis and enhanced decision-making.
"""

import re
import json
import time
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict

# NLP and text processing
try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK not available - using basic text processing")

try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers not available - using basic NLP")


class OptimizationStrategy(Enum):
    """Decision optimization strategies"""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    ADAPTIVE = "adaptive"


class AuditSeverity(Enum):
    """Audit finding severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class OptimizedDecision:
    """Optimized decision result"""
    original_decision: str
    optimized_decision: str
    optimization_strategy: OptimizationStrategy
    confidence_improvement: float
    risk_reduction: float
    reasoning: List[str]
    safeguards_added: List[str]
    performance_impact: str
    optimization_time: float


@dataclass
class AuditAnalysis:
    """NLP analysis of audit logs and findings"""
    analysis_id: str
    text_content: str
    sentiment_score: float
    key_entities: List[str]
    risk_keywords: List[str]
    severity_assessment: AuditSeverity
    extracted_threats: List[str]
    compliance_issues: List[str]
    recommendations: List[str]
    confidence: float
    processing_time: float


class DecisionOptimizer:
    """Advanced decision optimization engine"""
    
    def __init__(self, optimizer_name: str = "decision_optimizer_v1"):
        self.optimizer_name = optimizer_name
        self.logger = logging.getLogger(f"decision_optimizer.{optimizer_name}")
        
        # Optimization parameters
        self.risk_tolerance = 0.3
        self.performance_weight = 0.4
        self.security_weight = 0.6
        
        # Historical optimization data
        self.optimization_history = []
        self.strategy_performance = defaultdict(list)
        
        # Decision patterns
        self.decision_patterns = self._initialize_decision_patterns()
    
    def _initialize_decision_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize common decision patterns and their optimizations"""
        return {
            "high_risk_access": {
                "triggers": ["low_trust", "anomalous_behavior", "sensitive_resource"],
                "conservative": "deny_with_explanation",
                "balanced": "allow_with_strict_monitoring",
                "aggressive": "allow_with_verification",
                "safeguards": ["multi_factor_auth", "session_monitoring", "audit_logging"]
            },
            "routine_access": {
                "triggers": ["high_trust", "normal_behavior", "regular_resource"],
                "conservative": "allow_with_monitoring",
                "balanced": "allow",
                "aggressive": "allow_with_caching",
                "safeguards": ["basic_logging", "periodic_review"]
            },
            "emergency_access": {
                "triggers": ["emergency_context", "authorized_user", "critical_resource"],
                "conservative": "allow_with_approval",
                "balanced": "allow_with_monitoring",
                "aggressive": "allow_immediately",
                "safeguards": ["emergency_logging", "post_access_review", "approval_notification"]
            },
            "suspicious_activity": {
                "triggers": ["multiple_failures", "unusual_pattern", "policy_violation"],
                "conservative": "deny_and_investigate",
                "balanced": "deny_with_escalation",
                "aggressive": "allow_with_warnings",
                "safeguards": ["security_alert", "user_notification", "enhanced_monitoring"]
            }
        }
    
    async def optimize_decision(self, 
                              original_decision: str,
                              context_data: Dict[str, Any],
                              risk_factors: List[str],
                              trust_score: float,
                              strategy: OptimizationStrategy = OptimizationStrategy.BALANCED) -> OptimizedDecision:
        """Optimize a decision using AI-driven analysis"""
        start_time = time.time()
        
        try:
            # Analyze decision context
            decision_pattern = self._identify_decision_pattern(context_data, risk_factors, trust_score)
            
            # Generate optimized decision
            optimized_decision = self._generate_optimized_decision(
                original_decision, decision_pattern, strategy
            )
            
            # Calculate improvements
            confidence_improvement = self._calculate_confidence_improvement(
                original_decision, optimized_decision, trust_score, risk_factors
            )
            
            risk_reduction = self._calculate_risk_reduction(
                original_decision, optimized_decision, risk_factors
            )
            
            # Generate reasoning
            reasoning = self._generate_optimization_reasoning(
                original_decision, optimized_decision, decision_pattern, strategy
            )
            
            # Determine safeguards
            safeguards = self._determine_safeguards(decision_pattern, risk_factors, trust_score)
            
            # Assess performance impact
            performance_impact = self._assess_performance_impact(optimized_decision, safeguards)
            
            optimization_time = time.time() - start_time
            
            result = OptimizedDecision(
                original_decision=original_decision,
                optimized_decision=optimized_decision,
                optimization_strategy=strategy,
                confidence_improvement=confidence_improvement,
                risk_reduction=risk_reduction,
                reasoning=reasoning,
                safeguards_added=safeguards,
                performance_impact=performance_impact,
                optimization_time=optimization_time
            )
            
            # Update optimization history
            self._update_optimization_history(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Decision optimization failed: {e}")
            
            return OptimizedDecision(
                original_decision=original_decision,
                optimized_decision=original_decision,  # Fallback
                optimization_strategy=strategy,
                confidence_improvement=0.0,
                risk_reduction=0.0,
                reasoning=[f"Optimization failed: {str(e)}"],
                safeguards_added=[],
                performance_impact="unknown",
                optimization_time=time.time() - start_time
            )
    
    def _identify_decision_pattern(self, context_data: Dict[str, Any], 
                                 risk_factors: List[str], trust_score: float) -> str:
        """Identify the decision pattern based on context"""
        # Check for emergency context
        if context_data.get('emergency', False) or 'emergency' in context_data.get('access_type', '').lower():
            return "emergency_access"
        
        # Check for suspicious activity
        if len(risk_factors) > 2 or trust_score < 0.3:
            return "suspicious_activity"
        
        # Check for high-risk access
        if (context_data.get('resource_sensitivity', 'low') in ['high', 'critical'] or 
            trust_score < 0.6 or 
            len(risk_factors) > 0):
            return "high_risk_access"
        
        # Default to routine access
        return "routine_access"
    
    def _generate_optimized_decision(self, original_decision: str, 
                                   pattern: str, strategy: OptimizationStrategy) -> str:
        """Generate optimized decision based on pattern and strategy"""
        if pattern not in self.decision_patterns:
            return original_decision
        
        pattern_config = self.decision_patterns[pattern]
        strategy_key = strategy.value
        
        if strategy_key in pattern_config:
            return pattern_config[strategy_key]
        
        return original_decision
    
    def _calculate_confidence_improvement(self, original: str, optimized: str, 
                                        trust_score: float, risk_factors: List[str]) -> float:
        """Calculate confidence improvement from optimization"""
        if original == optimized:
            return 0.0
        
        # Base improvement from optimization
        base_improvement = 0.2
        
        # Additional improvement based on risk mitigation
        risk_improvement = min(0.3, len(risk_factors) * 0.1)
        
        # Trust-based adjustment
        trust_adjustment = (1.0 - trust_score) * 0.2
        
        return min(1.0, base_improvement + risk_improvement + trust_adjustment)
    
    def _calculate_risk_reduction(self, original: str, optimized: str, risk_factors: List[str]) -> float:
        """Calculate risk reduction from optimization"""
        if original == optimized:
            return 0.0
        
        # Risk reduction heuristics
        if "deny" in optimized.lower() and "allow" in original.lower():
            return 0.8  # High risk reduction by denying
        
        if "monitoring" in optimized.lower() and "monitoring" not in original.lower():
            return 0.4  # Moderate risk reduction by adding monitoring
        
        if "verification" in optimized.lower():
            return 0.6  # Good risk reduction with verification
        
        return 0.2  # Default small improvement
    
    def _generate_optimization_reasoning(self, original: str, optimized: str, 
                                       pattern: str, strategy: OptimizationStrategy) -> List[str]:
        """Generate reasoning for the optimization"""
        reasoning = []
        
        reasoning.append(f"Applied {strategy.value} optimization strategy")
        reasoning.append(f"Identified decision pattern: {pattern}")
        
        if original != optimized:
            reasoning.append(f"Modified decision from '{original}' to '{optimized}'")
            
            if "monitoring" in optimized.lower():
                reasoning.append("Added monitoring for enhanced security")
            
            if "verification" in optimized.lower():
                reasoning.append("Added verification step for risk mitigation")
            
            if "deny" in optimized.lower() and "allow" in original.lower():
                reasoning.append("Changed to deny for security protection")
        else:
            reasoning.append("Original decision deemed optimal")
        
        return reasoning
    
    def _determine_safeguards(self, pattern: str, risk_factors: List[str], trust_score: float) -> List[str]:
        """Determine appropriate safeguards for the decision"""
        safeguards = []
        
        if pattern in self.decision_patterns:
            base_safeguards = self.decision_patterns[pattern].get("safeguards", [])
            safeguards.extend(base_safeguards)
        
        # Additional safeguards based on risk factors
        if len(risk_factors) > 2:
            safeguards.append("enhanced_audit_logging")
        
        if trust_score < 0.5:
            safeguards.append("trust_verification")
        
        if "anomaly" in str(risk_factors):
            safeguards.append("behavioral_monitoring")
        
        return list(set(safeguards))  # Remove duplicates
    
    def _assess_performance_impact(self, decision: str, safeguards: List[str]) -> str:
        """Assess performance impact of the optimized decision"""
        impact_score = 0
        
        # Decision-based impact
        if "verification" in decision.lower():
            impact_score += 2
        if "monitoring" in decision.lower():
            impact_score += 1
        
        # Safeguard-based impact
        impact_score += len(safeguards) * 0.5
        
        if impact_score < 1:
            return "minimal"
        elif impact_score < 2:
            return "low"
        elif impact_score < 4:
            return "moderate"
        else:
            return "high"
    
    def _update_optimization_history(self, result: OptimizedDecision):
        """Update optimization history for learning"""
        self.optimization_history.append({
            "timestamp": datetime.now(),
            "strategy": result.optimization_strategy.value,
            "confidence_improvement": result.confidence_improvement,
            "risk_reduction": result.risk_reduction,
            "performance_impact": result.performance_impact
        })
        
        # Keep last 1000 optimizations
        if len(self.optimization_history) > 1000:
            self.optimization_history = self.optimization_history[-1000:]
        
        # Update strategy performance tracking
        self.strategy_performance[result.optimization_strategy.value].append({
            "confidence_improvement": result.confidence_improvement,
            "risk_reduction": result.risk_reduction
        })


class NLPProcessor:
    """Natural Language Processing for audit analysis and text intelligence"""
    
    def __init__(self, processor_name: str = "nlp_processor_v1"):
        self.processor_name = processor_name
        self.logger = logging.getLogger(f"nlp_processor.{processor_name}")
        
        # Initialize NLP components
        self.sentiment_analyzer = None
        self.lemmatizer = None
        self.stop_words = set()
        
        # Risk keyword patterns
        self.risk_keywords = [
            'unauthorized', 'breach', 'violation', 'attack', 'intrusion',
            'malware', 'suspicious', 'anomaly', 'threat', 'vulnerability',
            'exploit', 'compromise', 'escalation', 'abuse', 'fraud'
        ]
        
        # Compliance keywords
        self.compliance_keywords = [
            'gdpr', 'hipaa', 'sox', 'pci', 'compliance', 'regulation',
            'policy', 'standard', 'requirement', 'audit', 'review'
        ]
        
        self._initialize_nlp_components()
    
    def _initialize_nlp_components(self):
        """Initialize NLP processing components"""
        try:
            if NLTK_AVAILABLE:
                # Download required NLTK data (in production, these should be pre-downloaded)
                try:
                    import nltk
                    nltk.data.find('vader_lexicon')
                    nltk.data.find('stopwords')
                    nltk.data.find('wordnet')
                    nltk.data.find('punkt')
                except LookupError:
                    self.logger.warning("NLTK data not found - using basic processing")
                
                try:
                    self.sentiment_analyzer = SentimentIntensityAnalyzer()
                    self.lemmatizer = WordNetLemmatizer()
                    self.stop_words = set(stopwords.words('english'))
                except Exception as e:
                    self.logger.warning(f"NLTK initialization failed: {e}")
            
            self.logger.info("NLP processor initialized")
            
        except Exception as e:
            self.logger.error(f"NLP initialization failed: {e}")
    
    async def analyze_audit_text(self, text_content: str, 
                               content_type: str = "audit_log") -> AuditAnalysis:
        """Perform comprehensive NLP analysis of audit text"""
        start_time = time.time()
        
        try:
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text_content)
            
            # Sentiment analysis
            sentiment_score = self._analyze_sentiment(cleaned_text)
            
            # Entity and keyword extraction
            key_entities = self._extract_entities(cleaned_text)
            risk_keywords = self._extract_risk_keywords(cleaned_text)
            
            # Threat detection
            extracted_threats = self._detect_threats(cleaned_text)
            
            # Compliance analysis
            compliance_issues = self._analyze_compliance(cleaned_text)
            
            # Severity assessment
            severity = self._assess_severity(sentiment_score, risk_keywords, extracted_threats)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                severity, extracted_threats, compliance_issues
            )
            
            # Calculate confidence
            confidence = self._calculate_analysis_confidence(
                len(cleaned_text), len(key_entities), len(risk_keywords)
            )
            
            processing_time = time.time() - start_time
            
            return AuditAnalysis(
                analysis_id=f"nlp_{int(time.time())}_{hash(text_content) % 10000}",
                text_content=text_content,
                sentiment_score=sentiment_score,
                key_entities=key_entities,
                risk_keywords=risk_keywords,
                severity_assessment=severity,
                extracted_threats=extracted_threats,
                compliance_issues=compliance_issues,
                recommendations=recommendations,
                confidence=confidence,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Audit text analysis failed: {e}")
            
            return AuditAnalysis(
                analysis_id=f"nlp_error_{int(time.time())}",
                text_content=text_content,
                sentiment_score=0.0,
                key_entities=[],
                risk_keywords=[],
                severity_assessment=AuditSeverity.INFO,
                extracted_threats=[],
                compliance_issues=[],
                recommendations=[f"Analysis failed: {str(e)}"],
                confidence=0.0,
                processing_time=time.time() - start_time
            )
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for analysis"""
        # Basic cleaning
        cleaned = re.sub(r'[^\w\s]', ' ', text.lower())
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Remove stop words if available
        if self.stop_words:
            words = cleaned.split()
            cleaned = ' '.join([word for word in words if word not in self.stop_words])
        
        return cleaned
    
    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of the text"""
        if NLTK_AVAILABLE and self.sentiment_analyzer:
            try:
                scores = self.sentiment_analyzer.polarity_scores(text)
                return scores['compound']  # Overall sentiment score
            except Exception as e:
                self.logger.warning(f"Sentiment analysis failed: {e}")
        
        # Fallback: simple keyword-based sentiment
        negative_words = ['error', 'fail', 'deny', 'reject', 'violation', 'breach']
        positive_words = ['success', 'allow', 'grant', 'approve', 'valid']
        
        words = text.lower().split()
        negative_count = sum(1 for word in words if word in negative_words)
        positive_count = sum(1 for word in words if word in positive_words)
        
        if negative_count + positive_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract key entities from text"""
        entities = []
        
        # Simple regex-based entity extraction
        # IP addresses
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        entities.extend(re.findall(ip_pattern, text))
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        entities.extend(re.findall(email_pattern, text))
        
        # User IDs (assuming format like user123, admin456)
        user_pattern = r'\b(?:user|admin|account)[\w]*\d+\b'
        entities.extend(re.findall(user_pattern, text))
        
        return list(set(entities))  # Remove duplicates
    
    def _extract_risk_keywords(self, text: str) -> List[str]:
        """Extract security risk keywords from text"""
        found_keywords = []
        
        for keyword in self.risk_keywords:
            if keyword in text.lower():
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _detect_threats(self, text: str) -> List[str]:
        """Detect potential security threats in text"""
        threats = []
        
        threat_patterns = {
            'brute_force': r'brute.?force|password.?attack|login.?attempt',
            'malware': r'malware|virus|trojan|ransomware',
            'phishing': r'phishing|social.?engineering|fake.?email',
            'data_breach': r'data.?breach|information.?leak|unauthorized.?access',
            'insider_threat': r'insider.?threat|employee.?abuse|privilege.?abuse'
        }
        
        for threat_name, pattern in threat_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                threats.append(threat_name)
        
        return threats
    
    def _analyze_compliance(self, text: str) -> List[str]:
        """Analyze compliance-related issues in text"""
        compliance_issues = []
        
        for keyword in self.compliance_keywords:
            if keyword in text.lower():
                compliance_issues.append(f"Compliance reference: {keyword}")
        
        # Specific compliance violations
        if re.search(r'violation|non.?compliant|breach.*policy', text, re.IGNORECASE):
            compliance_issues.append("Policy violation detected")
        
        return compliance_issues
    
    def _assess_severity(self, sentiment_score: float, risk_keywords: List[str], 
                        threats: List[str]) -> AuditSeverity:
        """Assess the severity of audit findings"""
        severity_score = 0
        
        # Sentiment contribution
        if sentiment_score < -0.5:
            severity_score += 2
        elif sentiment_score < 0:
            severity_score += 1
        
        # Risk keywords contribution
        severity_score += len(risk_keywords)
        
        # Threat contribution
        severity_score += len(threats) * 2
        
        # Determine severity level
        if severity_score >= 8:
            return AuditSeverity.CRITICAL
        elif severity_score >= 6:
            return AuditSeverity.HIGH
        elif severity_score >= 4:
            return AuditSeverity.MEDIUM
        elif severity_score >= 2:
            return AuditSeverity.LOW
        else:
            return AuditSeverity.INFO
    
    def _generate_recommendations(self, severity: AuditSeverity, threats: List[str], 
                                compliance_issues: List[str]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if severity in [AuditSeverity.CRITICAL, AuditSeverity.HIGH]:
            recommendations.append("Immediate investigation required")
            recommendations.append("Escalate to security team")
        
        if threats:
            recommendations.append(f"Address detected threats: {', '.join(threats)}")
        
        if compliance_issues:
            recommendations.append("Review compliance requirements")
        
        if severity == AuditSeverity.MEDIUM:
            recommendations.append("Monitor for pattern development")
        
        if not recommendations:
            recommendations.append("Continue normal monitoring")
        
        return recommendations
    
    def _calculate_analysis_confidence(self, text_length: int, entity_count: int, 
                                     keyword_count: int) -> float:
        """Calculate confidence in the analysis"""
        confidence = 0.0
        
        # Text length contribution
        if text_length > 1000:
            confidence += 0.4
        elif text_length > 100:
            confidence += 0.2
        
        # Entity count contribution
        confidence += min(0.3, entity_count * 0.1)
        
        # Keyword count contribution
        confidence += min(0.3, keyword_count * 0.05)
        
        return min(1.0, confidence)