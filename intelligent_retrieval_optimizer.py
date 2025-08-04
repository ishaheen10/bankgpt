#!/usr/bin/env python3
"""
Intelligent Retrieval Optimizer - DSPy-Based Query Optimization System
Dynamically optimizes retrieval strategies for maximum efficiency and relevance
"""

import dspy
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field
import json
import re
import time
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import statistics
import asyncio

# ═══════════════════════════════════════════════════════════════════════
# MOCK LLM FOR DEMONSTRATION PURPOSES
# ═══════════════════════════════════════════════════════════════════════

class MockLLM(dspy.LM):
    """Mock LLM for demonstration purposes when no real LLM is available."""
    
    def __init__(self, model_name="mock-llm"):
        self.model_name = model_name
        self.kwargs = {"temperature": 0.7, "max_tokens": 1000}
    
    def generate(self, prompt, **kwargs):
        """Generate mock responses based on prompt patterns."""
        
        # Mock responses for different types of queries
        if "query_complexity" in prompt.lower():
            return ["moderate"]
        elif "target_companies" in prompt.lower():
            return ['["HBL", "UBL"]']
        elif "intent_classification" in prompt.lower():
            return ["analysis"]
        elif "time_periods" in prompt.lower():
            return ['["2023", "2024"]']
        elif "confidence_score" in prompt.lower():
            return [0.85]
        elif "retrieval_mode" in prompt.lower():
            return ["focused"]
        elif "optimal_top_k" in prompt.lower():
            return [15]
        elif "semantic_keywords" in prompt.lower():
            return ['["financial statements", "balance sheet", "income statement"]']
        elif "filters_config" in prompt.lower():
            return ['{"year": ["2023"], "company": ["HBL"]}']
        elif "expected_efficiency" in prompt.lower():
            return [0.75]
        elif "primary_keywords" in prompt.lower():
            return ['["revenue", "assets", "liabilities"]']
        elif "secondary_keywords" in prompt.lower():
            return ['["profit", "equity", "cash flow"]']
        elif "company_specific_terms" in prompt.lower():
            return ['["HBL", "Habib Bank Limited"]']
        elif "keyword_rationale" in prompt.lower():
            return ["Selected keywords based on financial analysis requirements"]
        elif "time_filters" in prompt.lower():
            return ['{"year": ["2023"], "quarter": ["Q4"]}']
        elif "company_filters" in prompt.lower():
            return ['{"tickers": ["HBL"], "sectors": ["banking"]}']
        elif "content_filters" in prompt.lower():
            return ['{"type": ["financial_statement"], "format": ["annual"]}']
        elif "filter_priority" in prompt.lower():
            return ['["time", "company", "content"]']
        else:
            return ["Mock response for demonstration"]
    
    def __call__(self, prompt, **kwargs):
        return self.generate(prompt, **kwargs)

# ═══════════════════════════════════════════════════════════════════════
# RETRIEVAL STRATEGY MODELS
# ═══════════════════════════════════════════════════════════════════════

class QueryComplexity(Enum):
    SIMPLE = "simple"           # Single company, single period
    MODERATE = "moderate"       # Multiple companies OR periods
    COMPLEX = "complex"         # Multiple companies AND periods
    COMPARATIVE = "comparative" # Cross-company comparisons

class RetrievalMode(Enum):
    FOCUSED = "focused"         # Low top_k, high precision
    BROAD = "broad"            # High top_k, comprehensive
    ADAPTIVE = "adaptive"       # Dynamic based on query
    HYBRID = "hybrid"          # Multiple search strategies

@dataclass
class RetrievalMetrics:
    """Comprehensive metrics for retrieval efficiency analysis."""
    query_hash: str
    retrieval_time: float
    chunks_retrieved: int
    chunks_used: int
    efficiency_ratio: float  # chunks_used / chunks_retrieved
    semantic_keywords: List[str]
    filters_applied: List[str]
    top_k_used: int
    query_complexity: QueryComplexity
    retrieval_mode: RetrievalMode
    success_score: float  # Quality of final analysis
    timestamp: datetime

# ═══════════════════════════════════════════════════════════════════════
# ADVANCED DSPY SIGNATURES FOR RETRIEVAL OPTIMIZATION
# ═══════════════════════════════════════════════════════════════════════

class QueryAnalysisSignature(dspy.Signature):
    """Analyze query characteristics to determine optimal retrieval strategy."""
    
    user_query: str = dspy.InputField(desc="Natural language financial query")
    available_tickers: str = dspy.InputField(desc="Available bank ticker symbols")
    conversation_context: str = dspy.InputField(desc="Previous conversation context")
    historical_performance: str = dspy.InputField(desc="Historical retrieval performance data", required=False)
    
    query_complexity: str = dspy.OutputField(desc="Query complexity level: simple, moderate, complex, comparative")
    target_companies: str = dspy.OutputField(desc="JSON list of target companies with confidence scores")
    intent_classification: str = dspy.OutputField(desc="Primary intent: statement, analysis, comparison, ratios")
    time_periods: str = dspy.OutputField(desc="Required time periods in standard format")
    confidence_score: float = dspy.OutputField(desc="Confidence in analysis accuracy (0.0-1.0)")

class RetrievalStrategySignature(dspy.Signature):
    """Determine optimal retrieval strategy based on query analysis."""
    
    query_analysis: str = dspy.InputField(desc="Structured query analysis results")
    user_query: str = dspy.InputField(desc="Original user query")
    efficiency_history: str = dspy.InputField(desc="Historical efficiency patterns for similar queries", required=False)
    
    retrieval_mode: str = dspy.OutputField(desc="Recommended retrieval mode: focused, broad, adaptive, hybrid")
    optimal_top_k: int = dspy.OutputField(desc="Optimal number of chunks to retrieve")
    semantic_keywords: str = dspy.OutputField(desc="JSON list of optimized semantic search keywords")
    filters_config: str = dspy.OutputField(desc="JSON configuration for search filters")
    expected_efficiency: float = dspy.OutputField(desc="Expected efficiency ratio (0.0-1.0)")

class KeywordOptimizationSignature(dspy.Signature):
    """Optimize semantic search keywords for maximum relevance."""
    
    user_query: str = dspy.InputField(desc="Original user query")
    query_intent: str = dspy.InputField(desc="Classified intent from query analysis")
    target_companies: str = dspy.InputField(desc="Target companies for search")
    historical_keywords: str = dspy.InputField(desc="Previously successful keywords for similar queries", required=False)
    
    primary_keywords: str = dspy.OutputField(desc="JSON list of primary semantic search keywords")
    secondary_keywords: str = dspy.OutputField(desc="JSON list of secondary keywords for fallback")
    company_specific_terms: str = dspy.OutputField(desc="JSON list of company-specific search terms")
    keyword_rationale: str = dspy.OutputField(desc="Explanation of keyword selection strategy")

class FilterOptimizationSignature(dspy.Signature):
    """Optimize search filters for efficiency and relevance."""
    
    query_analysis: str = dspy.InputField(desc="Structured query analysis")
    retrieval_strategy: str = dspy.InputField(desc="Selected retrieval strategy")
    performance_feedback: str = dspy.InputField(desc="Feedback from previous similar queries", required=False)
    
    time_filters: str = dspy.OutputField(desc="JSON configuration for time-based filters")
    company_filters: str = dspy.OutputField(desc="JSON configuration for company-specific filters")
    content_filters: str = dspy.OutputField(desc="JSON configuration for content-type filters")
    filter_priority: str = dspy.OutputField(desc="JSON list of filter application priority")

# ═══════════════════════════════════════════════════════════════════════
# ADVANCED REWARD FUNCTIONS FOR RETRIEVAL OPTIMIZATION
# ═══════════════════════════════════════════════════════════════════════

class RetrievalRewardFunctions:
    """Sophisticated reward functions for optimizing retrieval efficiency."""
    
    @staticmethod
    def query_analysis_reward(args, pred) -> float:
        """Reward function for query analysis accuracy."""
        score = 0.0
        feedback_points = []
        
        # 1. Query complexity assessment (25%)
        if hasattr(pred, 'query_complexity') and pred.query_complexity in ['simple', 'moderate', 'complex', 'comparative']:
            score += 0.25
        else:
            feedback_points.append("Must classify query complexity accurately")
        
        # 2. Company extraction accuracy (25%)
        try:
            companies = json.loads(pred.target_companies)
            if isinstance(companies, list) and len(companies) > 0:
                score += 0.25
            else:
                feedback_points.append("Must extract target companies properly")
        except (json.JSONDecodeError, AttributeError):
            feedback_points.append("Target companies must be valid JSON list")
        
        # 3. Intent classification (25%)
        if hasattr(pred, 'intent_classification') and pred.intent_classification in ['statement', 'analysis', 'comparison', 'ratios']:
            score += 0.25
        else:
            feedback_points.append("Must classify intent correctly")
        
        # 4. Confidence calibration (25%)
        if hasattr(pred, 'confidence_score') and 0.0 <= pred.confidence_score <= 1.0:
            score += 0.25
        else:
            feedback_points.append("Must provide valid confidence score")
        
        return min(score, 1.0)
    
    @staticmethod
    def retrieval_efficiency_reward(args, pred, actual_metrics: RetrievalMetrics = None) -> float:
        """Reward function based on actual retrieval efficiency."""
        if not actual_metrics:
            return 0.5  # Default score if no metrics available
        
        score = 0.0
        
        # 1. Efficiency ratio reward (40%)
        if actual_metrics.efficiency_ratio >= 0.8:
            score += 0.40
        elif actual_metrics.efficiency_ratio >= 0.6:
            score += 0.25
        elif actual_metrics.efficiency_ratio >= 0.4:
            score += 0.15
        else:
            score += 0.05
        
        # 2. Retrieval time reward (30%)
        if actual_metrics.retrieval_time <= 2.0:  # Under 2 seconds
            score += 0.30
        elif actual_metrics.retrieval_time <= 5.0:  # Under 5 seconds
            score += 0.20
        elif actual_metrics.retrieval_time <= 10.0:  # Under 10 seconds
            score += 0.10
        else:
            score += 0.05
        
        # 3. Top-k optimization reward (20%)
        if hasattr(pred, 'optimal_top_k'):
            k_efficiency = actual_metrics.chunks_used / pred.optimal_top_k if pred.optimal_top_k > 0 else 0
            if k_efficiency >= 0.7:
                score += 0.20
            elif k_efficiency >= 0.5:
                score += 0.15
            elif k_efficiency >= 0.3:
                score += 0.10
            else:
                score += 0.05
        
        # 4. Success score alignment (10%)
        if actual_metrics.success_score >= 0.8:
            score += 0.10
        elif actual_metrics.success_score >= 0.6:
            score += 0.05
        
        return min(score, 1.0)
    
    @staticmethod
    def keyword_optimization_reward(args, pred, retrieval_results: Dict[str, Any] = None) -> float:
        """Reward function for keyword optimization effectiveness."""
        score = 0.0
        
        # 1. Keyword diversity (30%)
        try:
            primary_kw = json.loads(pred.primary_keywords)
            secondary_kw = json.loads(pred.secondary_keywords)
            
            total_keywords = len(primary_kw) + len(secondary_kw)
            if 5 <= total_keywords <= 15:  # Optimal range
                score += 0.30
            elif 3 <= total_keywords <= 20:
                score += 0.20
            else:
                score += 0.10
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # 2. Keyword relevance (40%)
        if retrieval_results and 'relevance_scores' in retrieval_results:
            avg_relevance = statistics.mean(retrieval_results['relevance_scores'])
            if avg_relevance >= 0.8:
                score += 0.40
            elif avg_relevance >= 0.6:
                score += 0.25
            elif avg_relevance >= 0.4:
                score += 0.15
            else:
                score += 0.05
        else:
            score += 0.20  # Default when no results available
        
        # 3. Rationale quality (30%)
        if hasattr(pred, 'keyword_rationale') and len(pred.keyword_rationale) > 50:
            score += 0.30
        else:
            score += 0.10
        
        return min(score, 1.0)

# ═══════════════════════════════════════════════════════════════════════
# INTELLIGENT RETRIEVAL MODULES
# ═══════════════════════════════════════════════════════════════════════

class IntelligentQueryAnalyzer(dspy.Module):
    """Advanced query analysis with learning capabilities."""
    
    def __init__(self):
        super().__init__()
        self.analyze_query = dspy.ChainOfThought(QueryAnalysisSignature)
        
        # Multi-stage analysis with refinement
        self.refined_analysis = dspy.Refine(
            module=self.analyze_query,
            N=2,
            reward_fn=RetrievalRewardFunctions.query_analysis_reward,
            threshold=0.8
        )
        
        self.performance_history = []
    
    def forward(self, user_query: str, available_tickers: str, conversation_context: str = ""):
        """Analyze query with historical performance context."""
        
        # Prepare historical context
        historical_performance = self._get_historical_context(user_query)
        
        result = self.refined_analysis(
            user_query=user_query,
            available_tickers=available_tickers,
            conversation_context=conversation_context,
            historical_performance=historical_performance
        )
        
        return result
    
    def _get_historical_context(self, user_query: str) -> str:
        """Get relevant historical performance data."""
        # Analyze recent performance for similar queries
        similar_queries = [
            perf for perf in self.performance_history[-50:]  # Last 50 queries
            if self._query_similarity(user_query, perf.get('original_query', '')) > 0.6
        ]
        
        if similar_queries:
            avg_efficiency = statistics.mean([q.get('efficiency_ratio', 0.5) for q in similar_queries])
            return f"Similar queries achieved {avg_efficiency:.2f} average efficiency"
        
        return "No historical data available"
    
    def _query_similarity(self, query1: str, query2: str) -> float:
        """Simple similarity metric for queries."""
        # Basic keyword overlap similarity
        words1 = set(query1.lower().split())
        words2 = set(query2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def update_performance_history(self, performance_data: Dict[str, Any]):
        """Update performance history for learning."""
        self.performance_history.append(performance_data)
        
        # Keep only last 100 entries
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]

class AdaptiveRetrievalStrategy(dspy.Module):
    """Adaptive retrieval strategy optimizer."""
    
    def __init__(self):
        super().__init__()
        self.strategy_generator = dspy.ChainOfThought(RetrievalStrategySignature)
        
        # Advanced strategy selection with learning
        self.optimized_strategy = dspy.BestOfN(
            module=self.strategy_generator,
            N=3,
            reward_fn=self._strategy_reward,
            threshold=0.75
        )
        
        self.efficiency_patterns = {}
    
    def _strategy_reward(self, args, pred) -> float:
        """Reward function for strategy selection."""
        score = 0.0
        
        # Valid retrieval mode
        if hasattr(pred, 'retrieval_mode') and pred.retrieval_mode in ['focused', 'broad', 'adaptive', 'hybrid']:
            score += 0.3
        
        # Reasonable top_k
        if hasattr(pred, 'optimal_top_k') and 5 <= pred.optimal_top_k <= 50:
            score += 0.3
        
        # Valid JSON outputs
        try:
            json.loads(pred.semantic_keywords)
            json.loads(pred.filters_config)
            score += 0.2
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # Realistic efficiency expectation
        if hasattr(pred, 'expected_efficiency') and 0.3 <= pred.expected_efficiency <= 1.0:
            score += 0.2
        
        return min(score, 1.0)
    
    def forward(self, query_analysis: str, user_query: str):
        """Generate optimized retrieval strategy."""
        
        # Get historical efficiency patterns
        efficiency_history = self._get_efficiency_history(query_analysis)
        
        result = self.optimized_strategy(
            query_analysis=query_analysis,
            user_query=user_query,
            efficiency_history=efficiency_history
        )
        
        return result
    
    def _get_efficiency_history(self, query_analysis: str) -> str:
        """Get historical efficiency data for similar query patterns."""
        # Analyze efficiency patterns
        if self.efficiency_patterns:
            return json.dumps(self.efficiency_patterns)
        return "No historical efficiency data available"
    
    def update_efficiency_patterns(self, pattern_key: str, metrics: RetrievalMetrics):
        """Update efficiency patterns for learning."""
        if pattern_key not in self.efficiency_patterns:
            self.efficiency_patterns[pattern_key] = []
        
        self.efficiency_patterns[pattern_key].append({
            'efficiency_ratio': metrics.efficiency_ratio,
            'retrieval_time': metrics.retrieval_time,
            'top_k_used': metrics.top_k_used,
            'success_score': metrics.success_score
        })
        
        # Keep only last 20 entries per pattern
        if len(self.efficiency_patterns[pattern_key]) > 20:
            self.efficiency_patterns[pattern_key] = self.efficiency_patterns[pattern_key][-20:]

class IntelligentKeywordOptimizer(dspy.Module):
    """Intelligent keyword optimization system."""
    
    def __init__(self):
        super().__init__()
        self.optimize_keywords = dspy.ChainOfThought(KeywordOptimizationSignature)
        
        # Keyword optimization with validation
        self.validated_keywords = dspy.Refine(
            module=self.optimize_keywords,
            N=2,
            reward_fn=RetrievalRewardFunctions.keyword_optimization_reward,
            threshold=0.7
        )
        
        self.successful_keywords = {}
    
    def forward(self, user_query: str, query_intent: str, target_companies: str):
        """Generate optimized keywords."""
        
        # Get historical successful keywords
        historical_keywords = self._get_historical_keywords(query_intent)
        
        result = self.validated_keywords(
            user_query=user_query,
            query_intent=query_intent,
            target_companies=target_companies,
            historical_keywords=historical_keywords
        )
        
        return result
    
    def _get_historical_keywords(self, query_intent: str) -> str:
        """Get historically successful keywords for intent."""
        if query_intent in self.successful_keywords:
            return json.dumps(self.successful_keywords[query_intent])
        return "No historical keyword data available"
    
    def update_keyword_success(self, query_intent: str, keywords: List[str], success_score: float):
        """Update successful keywords database."""
        if query_intent not in self.successful_keywords:
            self.successful_keywords[query_intent] = {}
        
        for keyword in keywords:
            if keyword not in self.successful_keywords[query_intent]:
                self.successful_keywords[query_intent][keyword] = []
            
            self.successful_keywords[query_intent][keyword].append(success_score)
            
            # Keep only last 10 scores per keyword
            if len(self.successful_keywords[query_intent][keyword]) > 10:
                self.successful_keywords[query_intent][keyword] = self.successful_keywords[query_intent][keyword][-10:]

class DynamicFilterOptimizer(dspy.Module):
    """Dynamic filter optimization system."""
    
    def __init__(self):
        super().__init__()
        self.optimize_filters = dspy.ChainOfThought(FilterOptimizationSignature)
        
        # Filter optimization with performance tracking
        self.performance_optimized = dspy.BestOfN(
            module=self.optimize_filters,
            N=2,
            reward_fn=self._filter_reward,
            threshold=0.7
        )
        
        self.filter_performance = {}
    
    def _filter_reward(self, args, pred) -> float:
        """Reward function for filter optimization."""
        score = 0.0
        
        # Valid JSON structures
        try:
            json.loads(pred.time_filters)
            json.loads(pred.company_filters)
            json.loads(pred.content_filters)
            json.loads(pred.filter_priority)
            score += 0.8
        except (json.JSONDecodeError, AttributeError):
            score += 0.2
        
        # Reasonable complexity
        if hasattr(pred, 'filter_priority'):
            try:
                priority = json.loads(pred.filter_priority)
                if 2 <= len(priority) <= 6:  # Reasonable number of filters
                    score += 0.2
            except:
                pass
        
        return min(score, 1.0)
    
    def forward(self, query_analysis: str, retrieval_strategy: str):
        """Generate optimized filter configuration."""
        
        # Get performance feedback
        performance_feedback = self._get_performance_feedback(query_analysis)
        
        result = self.performance_optimized(
            query_analysis=query_analysis,
            retrieval_strategy=retrieval_strategy,
            performance_feedback=performance_feedback
        )
        
        return result
    
    def _get_performance_feedback(self, query_analysis: str) -> str:
        """Get performance feedback for similar queries."""
        # Analyze filter performance patterns
        if self.filter_performance:
            return json.dumps(self.filter_performance)
        return "No filter performance data available"
    
    def update_filter_performance(self, filter_config: Dict[str, Any], performance_metrics: RetrievalMetrics):
        """Update filter performance tracking."""
        config_key = json.dumps(filter_config, sort_keys=True)
        
        if config_key not in self.filter_performance:
            self.filter_performance[config_key] = []
        
        self.filter_performance[config_key].append({
            'efficiency_ratio': performance_metrics.efficiency_ratio,
            'retrieval_time': performance_metrics.retrieval_time,
            'success_score': performance_metrics.success_score
        })
        
        # Keep only last 15 entries per config
        if len(self.filter_performance[config_key]) > 15:
            self.filter_performance[config_key] = self.filter_performance[config_key][-15:]

# ═══════════════════════════════════════════════════════════════════════
# COMPREHENSIVE RETRIEVAL OPTIMIZATION SYSTEM
# ═══════════════════════════════════════════════════════════════════════

class IntelligentRetrievalOptimizer:
    """
    Complete intelligent retrieval optimization system.
    Learns and adapts retrieval strategies for maximum efficiency.
    """
    
    def __init__(self):
        self.query_analyzer = IntelligentQueryAnalyzer()
        self.strategy_optimizer = AdaptiveRetrievalStrategy()
        self.keyword_optimizer = IntelligentKeywordOptimizer()
        self.filter_optimizer = DynamicFilterOptimizer()
        
        # Performance tracking
        self.retrieval_metrics = []
        self.optimization_history = []
        
        # Learning parameters
        self.learning_rate = 0.1
        self.adaptation_threshold = 0.8
        self.configured = False
    
    def configure(self, lm_model=None):
        """Configure the optimizer with DSPy language model."""
        try:
            if lm_model is None:
                lm_model = MockLLM()
                print("🔧 Using mock LLM for demonstration")
            
            dspy.configure(lm=lm_model)
            self.configured = True
            print("✅ DSPy configured successfully")
            
        except Exception as e:
            print(f"❌ DSPy configuration failed: {e}")
            self.configured = False
            raise e
    
    def optimize_retrieval(self, user_query: str, available_tickers: str, 
                          conversation_context: str = "") -> Dict[str, Any]:
        """
        Generate optimized retrieval configuration.
        Returns comprehensive retrieval strategy with all parameters.
        """
        
        if not self.configured:
            raise RuntimeError("System not configured. Call configure() first.")
        
        start_time = time.time()
        
        try:
            # Step 1: Analyze query characteristics
            query_analysis = self.query_analyzer(
                user_query=user_query,
                available_tickers=available_tickers,
                conversation_context=conversation_context
            )
            
            # Step 2: Determine optimal retrieval strategy
            retrieval_strategy = self.strategy_optimizer(
                query_analysis=json.dumps({
                    'complexity': query_analysis.query_complexity,
                    'companies': query_analysis.target_companies,
                    'intent': query_analysis.intent_classification,
                    'periods': query_analysis.time_periods
                }),
                user_query=user_query
            )
            
            # Step 3: Optimize semantic keywords
            keywords = self.keyword_optimizer(
                user_query=user_query,
                query_intent=query_analysis.intent_classification,
                target_companies=query_analysis.target_companies
            )
            
            # Step 4: Optimize filters
            filters = self.filter_optimizer(
                query_analysis=json.dumps({
                    'complexity': query_analysis.query_complexity,
                    'companies': query_analysis.target_companies,
                    'intent': query_analysis.intent_classification,
                    'periods': query_analysis.time_periods
                }),
                retrieval_strategy=json.dumps({
                    'mode': retrieval_strategy.retrieval_mode,
                    'top_k': retrieval_strategy.optimal_top_k,
                    'expected_efficiency': retrieval_strategy.expected_efficiency
                })
            )
            
            # Generate comprehensive configuration
            optimization_config = {
                'query_hash': self._generate_query_hash(user_query),
                'analysis': {
                    'complexity': query_analysis.query_complexity,
                    'companies': json.loads(query_analysis.target_companies),
                    'intent': query_analysis.intent_classification,
                    'periods': json.loads(query_analysis.time_periods),
                    'confidence': query_analysis.confidence_score
                },
                'strategy': {
                    'mode': retrieval_strategy.retrieval_mode,
                    'top_k': retrieval_strategy.optimal_top_k,
                    'expected_efficiency': retrieval_strategy.expected_efficiency
                },
                'keywords': {
                    'primary': json.loads(keywords.primary_keywords),
                    'secondary': json.loads(keywords.secondary_keywords),
                    'company_specific': json.loads(keywords.company_specific_terms),
                    'rationale': keywords.keyword_rationale
                },
                'filters': {
                    'time_filters': json.loads(filters.time_filters),
                    'company_filters': json.loads(filters.company_filters),
                    'content_filters': json.loads(filters.content_filters),
                    'priority': json.loads(filters.filter_priority)
                },
                'optimization_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat()
            }
            
            # Store for learning
            self.optimization_history.append(optimization_config)
            
            return optimization_config
            
        except Exception as e:
            print(f"❌ Error in optimize_retrieval: {e}")
            # Return a basic fallback configuration
            return self._create_fallback_config(user_query, start_time)
    
    def _create_fallback_config(self, user_query: str, start_time: float) -> Dict[str, Any]:
        """Create a fallback configuration when DSPy fails."""
        return {
            'query_hash': self._generate_query_hash(user_query),
            'analysis': {
                'complexity': 'simple',
                'companies': ['HBL'],
                'intent': 'analysis',
                'periods': ['2023'],
                'confidence': 0.5
            },
            'strategy': {
                'mode': 'focused',
                'top_k': 15,
                'expected_efficiency': 0.7
            },
            'keywords': {
                'primary': ['financial', 'statement', 'analysis'],
                'secondary': ['revenue', 'profit', 'balance'],
                'company_specific': ['HBL'],
                'rationale': 'Fallback keywords due to system error'
            },
            'filters': {
                'time_filters': {'year': ['2023']},
                'company_filters': {'tickers': ['HBL']},
                'content_filters': {'type': ['financial_statement']},
                'priority': ['time', 'company', 'content']
            },
            'optimization_time': time.time() - start_time,
            'timestamp': datetime.now().isoformat(),
            'fallback': True
        }
    
    def track_retrieval_performance(self, query_hash: str, retrieval_results: Dict[str, Any],
                                   chunks_used: int, final_analysis_quality: float) -> RetrievalMetrics:
        """
        Track actual retrieval performance for learning.
        """
        
        metrics = RetrievalMetrics(
            query_hash=query_hash,
            retrieval_time=retrieval_results.get('retrieval_time', 0),
            chunks_retrieved=retrieval_results.get('chunks_retrieved', 0),
            chunks_used=chunks_used,
            efficiency_ratio=chunks_used / retrieval_results.get('chunks_retrieved', 1),
            semantic_keywords=retrieval_results.get('keywords_used', []),
            filters_applied=retrieval_results.get('filters_applied', []),
            top_k_used=retrieval_results.get('top_k_used', 0),
            query_complexity=QueryComplexity(retrieval_results.get('query_complexity', 'simple')),
            retrieval_mode=RetrievalMode(retrieval_results.get('retrieval_mode', 'focused')),
            success_score=final_analysis_quality,
            timestamp=datetime.now()
        )
        
        self.retrieval_metrics.append(metrics)
        
        # Update learning systems
        self._update_learning_systems(metrics)
        
        return metrics
    
    def _update_learning_systems(self, metrics: RetrievalMetrics):
        """Update all learning systems with new performance data."""
        
        # Update query analyzer
        self.query_analyzer.update_performance_history({
            'query_hash': metrics.query_hash,
            'efficiency_ratio': metrics.efficiency_ratio,
            'success_score': metrics.success_score,
            'retrieval_time': metrics.retrieval_time
        })
        
        # Update strategy optimizer
        pattern_key = f"{metrics.query_complexity.value}_{metrics.retrieval_mode.value}"
        self.strategy_optimizer.update_efficiency_patterns(pattern_key, metrics)
        
        # Update keyword optimizer
        self.keyword_optimizer.update_keyword_success(
            query_intent=metrics.query_complexity.value,  # Simplified mapping
            keywords=metrics.semantic_keywords,
            success_score=metrics.success_score
        )
        
        # Update filter optimizer
        filter_config = {
            'filters_applied': metrics.filters_applied,
            'top_k_used': metrics.top_k_used
        }
        self.filter_optimizer.update_filter_performance(filter_config, metrics)
    
    def _generate_query_hash(self, user_query: str) -> str:
        """Generate unique hash for query tracking."""
        import hashlib
        return hashlib.md5(user_query.encode()).hexdigest()[:12]
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        
        if not self.retrieval_metrics:
            return {"status": "No performance data available"}
        
        recent_metrics = self.retrieval_metrics[-50:]  # Last 50 queries
        
        report = {
            "total_queries_optimized": len(self.retrieval_metrics),
            "recent_performance": {
                "avg_efficiency_ratio": statistics.mean([m.efficiency_ratio for m in recent_metrics]),
                "avg_retrieval_time": statistics.mean([m.retrieval_time for m in recent_metrics]),
                "avg_success_score": statistics.mean([m.success_score for m in recent_metrics]),
                "efficiency_distribution": {
                    "high_efficiency": len([m for m in recent_metrics if m.efficiency_ratio >= 0.8]),
                    "medium_efficiency": len([m for m in recent_metrics if 0.5 <= m.efficiency_ratio < 0.8]),
                    "low_efficiency": len([m for m in recent_metrics if m.efficiency_ratio < 0.5])
                }
            },
            "strategy_performance": self._analyze_strategy_performance(recent_metrics),
            "keyword_insights": self._analyze_keyword_performance(recent_metrics),
            "optimization_trends": self._analyze_optimization_trends(),
            "recommendations": self._generate_recommendations(recent_metrics)
        }
        
        return report
    
    def _analyze_strategy_performance(self, metrics: List[RetrievalMetrics]) -> Dict[str, Any]:
        """Analyze performance by retrieval strategy."""
        strategy_performance = {}
        
        for mode in RetrievalMode:
            mode_metrics = [m for m in metrics if m.retrieval_mode == mode]
            if mode_metrics:
                strategy_performance[mode.value] = {
                    "count": len(mode_metrics),
                    "avg_efficiency": statistics.mean([m.efficiency_ratio for m in mode_metrics]),
                    "avg_time": statistics.mean([m.retrieval_time for m in mode_metrics]),
                    "success_rate": len([m for m in mode_metrics if m.success_score >= 0.7]) / len(mode_metrics)
                }
        
        return strategy_performance
    
    def _analyze_keyword_performance(self, metrics: List[RetrievalMetrics]) -> Dict[str, Any]:
        """Analyze keyword effectiveness."""
        keyword_performance = {}
        
        for metric in metrics:
            for keyword in metric.semantic_keywords:
                if keyword not in keyword_performance:
                    keyword_performance[keyword] = {"uses": 0, "total_efficiency": 0, "total_success": 0}
                
                keyword_performance[keyword]["uses"] += 1
                keyword_performance[keyword]["total_efficiency"] += metric.efficiency_ratio
                keyword_performance[keyword]["total_success"] += metric.success_score
        
        # Calculate averages
        for keyword, stats in keyword_performance.items():
            if stats["uses"] > 0:
                stats["avg_efficiency"] = stats["total_efficiency"] / stats["uses"]
                stats["avg_success"] = stats["total_success"] / stats["uses"]
        
        # Return top performing keywords
        top_keywords = sorted(
            keyword_performance.items(),
            key=lambda x: x[1]["avg_efficiency"],
            reverse=True
        )[:10]
        
        return dict(top_keywords)
    
    def _analyze_optimization_trends(self) -> Dict[str, Any]:
        """Analyze optimization trends over time."""
        if len(self.retrieval_metrics) < 10:
            return {"status": "Insufficient data for trend analysis"}
        
        # Split into early and recent performance
        half_point = len(self.retrieval_metrics) // 2
        early_metrics = self.retrieval_metrics[:half_point]
        recent_metrics = self.retrieval_metrics[half_point:]
        
        early_avg = statistics.mean([m.efficiency_ratio for m in early_metrics])
        recent_avg = statistics.mean([m.efficiency_ratio for m in recent_metrics])
        
        return {
            "efficiency_improvement": recent_avg - early_avg,
            "learning_effectiveness": "improving" if recent_avg > early_avg else "stable",
            "early_average": early_avg,
            "recent_average": recent_avg
        }
    
    def _generate_recommendations(self, metrics: List[RetrievalMetrics]) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Analyze efficiency patterns
        low_efficiency_queries = [m for m in metrics if m.efficiency_ratio < 0.5]
        if len(low_efficiency_queries) > len(metrics) * 0.3:
            recommendations.append("Consider more aggressive filtering to improve efficiency")
        
        # Analyze retrieval time patterns
        slow_queries = [m for m in metrics if m.retrieval_time > 5.0]
        if len(slow_queries) > len(metrics) * 0.2:
            recommendations.append("Optimize search parameters to reduce retrieval time")
        
        # Analyze success patterns
        low_success_queries = [m for m in metrics if m.success_score < 0.7]
        if len(low_success_queries) > len(metrics) * 0.3:
            recommendations.append("Improve keyword selection for better content relevance")
        
        # Default recommendation
        if not recommendations:
            recommendations.append("System is performing well, continue monitoring")
        
        return recommendations
    
    def optimize_dspy_modules(self, trainset: List[Dict[str, Any]]):
        """Optimize DSPy modules based on training data."""
        
        print("🚀 Starting DSPy optimization for retrieval modules...")
        
        # Create composite metric for optimization
        def retrieval_metric(example, pred):
            scores = []
            
            # Query analysis accuracy
            if hasattr(pred, 'query_complexity'):
                scores.append(RetrievalRewardFunctions.query_analysis_reward(example, pred))
            
            # Keyword optimization
            if hasattr(pred, 'primary_keywords'):
                scores.append(RetrievalRewardFunctions.keyword_optimization_reward(example, pred))
            
            return sum(scores) / len(scores) if scores else 0.0
        
        # Optimize modules
        from dspy.teleprompt import BootstrapFewShotWithRandomSearch
        
        optimizer = BootstrapFewShotWithRandomSearch(
            metric=retrieval_metric,
            max_bootstrapped_demos=3,
            num_candidate_programs=6
        )
        
        # Optimize query analyzer
        self.query_analyzer = optimizer.compile(
            student=self.query_analyzer,
            trainset=trainset
        )
        
        print("✅ DSPy optimization completed for retrieval modules")


# ═══════════════════════════════════════════════════════════════════════
# USAGE EXAMPLE AND TESTING
# ═══════════════════════════════════════════════════════════════════════

def demonstrate_intelligent_retrieval():
    """Demonstrate the intelligent retrieval optimization system."""
    
    print("🎯 Intelligent Retrieval Optimization Demo")
    print("=" * 50)
    
    # Initialize system
    optimizer = IntelligentRetrievalOptimizer()
    
    # Configure DSPy with mock LLM for demonstration
    try:
        optimizer.configure()
    except Exception as e:
        print(f"⚠️  System configuration failed: {e}")
        print("🔄 Falling back to simplified demonstration...")
        demonstrate_simplified_retrieval()
        return
    
    # Example queries
    test_queries = [
        "Show me HBL's financial statements for 2023",
        "Compare UBL and HBL financial performance in 2023 vs 2022",
        "What are the banking ratios for all major banks?",
        "Analyze MCB's quarterly results for Q1-2024"
    ]
    
    available_tickers = "['HBL', 'UBL', 'MCB', 'NBP', 'BAFL']"
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-" * 40)
        
        try:
            # Generate optimization configuration
            config = optimizer.optimize_retrieval(
                user_query=query,
                available_tickers=available_tickers
            )
            
            # Check if fallback was used
            if config.get('fallback', False):
                print("⚠️  Used fallback configuration")
            
            print(f"🔍 Complexity: {config['analysis']['complexity']}")
            print(f"🎯 Intent: {config['analysis']['intent']}")
            print(f"📊 Strategy: {config['strategy']['mode']} (top_k={config['strategy']['top_k']})")
            print(f"🔑 Keywords: {config['keywords']['primary'][:3]}...")
            print(f"⏱️  Optimization time: {config['optimization_time']:.3f}s")
            
            # Simulate retrieval results
            simulated_results = {
                'retrieval_time': 2.5,
                'chunks_retrieved': config['strategy']['top_k'],
                'chunks_used': int(config['strategy']['top_k'] * 0.7),  # 70% usage
                'keywords_used': config['keywords']['primary'],
                'filters_applied': list(config['filters']['time_filters'].keys()),
                'top_k_used': config['strategy']['top_k'],
                'query_complexity': config['analysis']['complexity'],
                'retrieval_mode': config['strategy']['mode']
            }
            
            # Track performance
            metrics = optimizer.track_retrieval_performance(
                query_hash=config['query_hash'],
                retrieval_results=simulated_results,
                chunks_used=simulated_results['chunks_used'],
                final_analysis_quality=0.8
            )
            
            print(f"📈 Efficiency: {metrics.efficiency_ratio:.2f}")
            print(f"⚡ Retrieval time: {metrics.retrieval_time:.2f}s")
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            print("🔄 Continuing with next query...")
    
    # Generate performance report
    print("\n📊 Performance Report")
    print("=" * 30)
    
    try:
        report = optimizer.get_performance_report()
        if report.get('status') == 'No performance data available':
            print("⚠️  No performance data available yet")
        else:
            print(f"Total queries: {report['total_queries_optimized']}")
            print(f"Avg efficiency: {report['recent_performance']['avg_efficiency_ratio']:.2f}")
            print(f"Avg retrieval time: {report['recent_performance']['avg_retrieval_time']:.2f}s")
            print(f"Recommendations: {report['recommendations']}")
    except Exception as e:
        print(f"❌ Error generating report: {e}")

def demonstrate_simplified_retrieval():
    """Simplified demonstration without DSPy dependencies."""
    
    print("\n🎯 Simplified Retrieval Optimization Demo")
    print("=" * 50)
    
    # Show the concept without actual DSPy execution
    test_queries = [
        "Show me HBL's financial statements for 2023",
        "Compare UBL and HBL financial performance in 2023 vs 2022",
        "What are the banking ratios for all major banks?",
        "Analyze MCB's quarterly results for Q1-2024"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Query {i}: {query}")
        print("-" * 40)
        
        # Simulate the optimization process
        if "compare" in query.lower():
            complexity = "complex"
            intent = "comparison"
            top_k = 25
            keywords = ["financial performance", "comparison", "analysis"]
        elif "ratio" in query.lower():
            complexity = "moderate"
            intent = "ratios"
            top_k = 20
            keywords = ["banking ratios", "financial metrics", "performance"]
        elif "quarterly" in query.lower():
            complexity = "moderate"
            intent = "analysis"
            top_k = 15
            keywords = ["quarterly results", "Q1", "financial analysis"]
        else:
            complexity = "simple"
            intent = "statement"
            top_k = 12
            keywords = ["financial statements", "balance sheet", "income statement"]
        
        print(f"🔍 Complexity: {complexity}")
        print(f"🎯 Intent: {intent}")
        print(f"📊 Strategy: focused (top_k={top_k})")
        print(f"🔑 Keywords: {keywords}")
        print(f"📈 Expected efficiency: {0.7 + (i * 0.05):.2f}")
        print(f"⚡ Expected retrieval time: {2.0 + (i * 0.3):.1f}s")
    
    print("\n💡 Key Insights:")
    print("• Simple queries use fewer chunks (top_k=12)")
    print("• Complex comparisons need more data (top_k=25)")
    print("• Keywords adapt to query intent")
    print("• System learns efficiency patterns over time")
    print("• DSPy modules would optimize these parameters automatically")

if __name__ == "__main__":
    demonstrate_intelligent_retrieval() 