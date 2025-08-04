"""
PSX Financial Assistant - Advanced DSPy-Based Structured Analysis
Modern prompt engineering using DSPy framework with sophisticated refinement and optimization
"""

import dspy
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field
import json
import re
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════
# ADVANCED DSPY SIGNATURES FOR FINANCIAL ANALYSIS
# ═══════════════════════════════════════════════════════════════════════

class FinancialStatementSignature(dspy.Signature):
    """Extract and format financial statement data from provided chunks."""
    
    query: str = dspy.InputField(desc="Original user query requesting financial statements")
    financial_chunks: str = dspy.InputField(desc="Financial data chunks containing statement information")
    companies: str = dspy.InputField(desc="Companies being analyzed")
    intent: str = dspy.InputField(desc="Query intent (statement or analysis)")
    feedback: str = dspy.InputField(desc="Feedback from previous attempts to improve output", required=False)
    
    formatted_statements: str = dspy.OutputField(desc="Complete financial statements in clean markdown tables with ALL line items, properly formatted with PKR MM units")
    used_chunks: str = dspy.OutputField(desc="List of chunk IDs actually used in the analysis")
    confidence: float = dspy.OutputField(desc="Confidence in completeness and accuracy (0.0-1.0)")

class FinancialAnalysisSignature(dspy.Signature):
    """Perform comprehensive financial analysis with banking ratios and insights."""
    
    query: str = dspy.InputField(desc="Original user query requesting financial analysis")
    financial_chunks: str = dspy.InputField(desc="Financial data chunks containing relevant information")
    companies: str = dspy.InputField(desc="Companies being analyzed")
    intent: str = dspy.InputField(desc="Query intent (statement or analysis)")
    feedback: str = dspy.InputField(desc="Feedback from previous attempts to improve analysis", required=False)
    
    comprehensive_analysis: str = dspy.OutputField(desc="Professional equity research analysis with tables, ratios, and non-obvious insights in investment banking report format")
    used_chunks: str = dspy.OutputField(desc="List of chunk IDs actually used in the analysis")
    insight_quality: float = dspy.OutputField(desc="Quality of insights provided (0.0-1.0)")

class QuarterlyAnalysisSignature(dspy.Signature):
    """Analyze quarterly financial data with Q4 calculations and trend analysis."""
    
    query: str = dspy.InputField(desc="Original user query requesting quarterly analysis")
    financial_chunks: str = dspy.InputField(desc="Financial data chunks with quarterly and annual data")
    companies: str = dspy.InputField(desc="Companies being analyzed")
    needs_q4_calculation: str = dspy.InputField(desc="Whether Q4 calculation is needed (true/false)")
    feedback: str = dspy.InputField(desc="Feedback from previous attempts", required=False)
    
    quarterly_analysis: str = dspy.OutputField(desc="Quarterly financial analysis with Q4 calculations and trend insights")
    used_chunks: str = dspy.OutputField(desc="List of chunk IDs actually used in the analysis")
    calculation_accuracy: float = dspy.OutputField(desc="Accuracy of Q4 calculations (0.0-1.0)")

class BankingRatiosSignature(dspy.Signature):
    """Calculate and analyze banking-specific financial ratios."""
    
    query: str = dspy.InputField(desc="Original user query requesting ratio analysis")
    financial_chunks: str = dspy.InputField(desc="Financial data chunks containing numerical data")
    companies: str = dspy.InputField(desc="Companies being analyzed")
    feedback: str = dspy.InputField(desc="Feedback on ratio calculations from previous attempts", required=False)
    
    banking_ratios: str = dspy.OutputField(desc="Banking ratios analysis with calculations, interpretations, and comparative insights")
    used_chunks: str = dspy.OutputField(desc="List of chunk IDs actually used in the analysis")
    ratio_accuracy: float = dspy.OutputField(desc="Accuracy of ratio calculations (0.0-1.0)")

class QueryParsingSignature(dspy.Signature):
    """Parse natural language financial queries into structured query plans."""
    
    user_query: str = dspy.InputField(desc="Natural language query about financial data")
    available_tickers: str = dspy.InputField(desc="Available bank ticker symbols")
    conversation_context: str = dspy.InputField(desc="Previous conversation context")
    
    query_plan: str = dspy.OutputField(desc="Structured QueryPlan JSON with companies, intent, and detailed queries")

# ═══════════════════════════════════════════════════════════════════════
# ADVANCED REWARD FUNCTIONS - The Heart of DSPy Refinement
# ═══════════════════════════════════════════════════════════════════════

class AdvancedRewardFunctions:
    """Sophisticated reward functions that guide DSPy refinement process."""
    
    @staticmethod
    def statement_completeness_reward(args, pred) -> float:
        """
        Advanced reward function for statement completeness.
        Shows how DSPy refinement works - this guides iterative improvement.
        """
        output = pred.formatted_statements
        completeness_score = 0.0
        feedback_points = []
        
        # 1. Table Format Check (30% of score)
        if '|' in output and '---' in output:
            table_count = output.count('|')
            if table_count > 20:  # Rich table content
                completeness_score += 0.30
            elif table_count > 10:
                completeness_score += 0.20
                feedback_points.append("Tables need more detail")
            else:
                completeness_score += 0.10
                feedback_points.append("Tables are too sparse")
        else:
            feedback_points.append("Missing proper markdown table format")
        
        # 2. Currency and Units (20% of score)
        if 'PKR MM' in output or 'PKR million' in output:
            completeness_score += 0.20
        elif 'PKR' in output:
            completeness_score += 0.10
            feedback_points.append("Currency units need to specify 'PKR MM'")
        else:
            feedback_points.append("Missing currency units (PKR MM)")
        
        # 3. Line Item Count (30% of score)
        lines = output.split('\n')
        table_lines = [line for line in lines if '|' in line and line.strip()]
        financial_terms = ['asset', 'liability', 'equity', 'revenue', 'expense', 'profit', 'cash']
        
        line_item_count = sum(1 for line in table_lines 
                             if any(term in line.lower() for term in financial_terms))
        
        if line_item_count >= 15:  # Comprehensive statement
            completeness_score += 0.30
        elif line_item_count >= 10:
            completeness_score += 0.20
            feedback_points.append(f"Need more line items (found {line_item_count}, aim for 15+)")
        elif line_item_count >= 5:
            completeness_score += 0.10
            feedback_points.append(f"Too few line items (found {line_item_count})")
        else:
            feedback_points.append("Critically low number of financial line items")
        
        # 4. Chunk Usage (20% of score)
        if hasattr(pred, 'used_chunks') and pred.used_chunks:
            try:
                chunk_numbers = re.findall(r'\d+', pred.used_chunks)
                if len(chunk_numbers) >= 3:
                    completeness_score += 0.20
                elif len(chunk_numbers) >= 1:
                    completeness_score += 0.10
                    feedback_points.append("Use more source chunks for comprehensive analysis")
                else:
                    feedback_points.append("Must specify which chunks were used")
            except:
                feedback_points.append("Invalid chunk reference format")
        else:
            feedback_points.append("Must specify used chunks")
        
        # Store feedback for next iteration (DSPy refinement mechanism)
        if hasattr(pred, 'feedback') and feedback_points:
            pred.feedback = "Issues to fix: " + "; ".join(feedback_points)
        
        return min(completeness_score, 1.0)
    
    @staticmethod
    def analysis_quality_reward(args, pred) -> float:
        """
        Advanced reward function for analysis quality.
        Demonstrates multi-dimensional scoring for DSPy BestOfN selection.
        """
        output = pred.comprehensive_analysis
        quality_score = 0.0
        feedback_points = []
        
        # 1. Structure and Organization (25% of score)
        if 'Section 1' in output and 'Section 2' in output:
            section_count = len(re.findall(r'Section \d+', output))
            if section_count >= 3:
                quality_score += 0.25
            else:
                quality_score += 0.15
                feedback_points.append(f"Add more sections (found {section_count}, recommend 3+)")
        else:
            feedback_points.append("Must structure analysis into clear sections")
        
        # 2. Banking Ratios and Calculations (25% of score)
        banking_terms = ['roe', 'roa', 'capital adequacy', 'tier 1', 'npl', 'cost.*income', 
                        'advance.*deposit', 'net interest margin', 'provision coverage']
        
        ratio_mentions = sum(1 for term in banking_terms 
                           if re.search(term, output, re.IGNORECASE))
        
        if ratio_mentions >= 5:
            quality_score += 0.25
        elif ratio_mentions >= 3:
            quality_score += 0.15
            feedback_points.append(f"Include more banking ratios (found {ratio_mentions}, aim for 5+)")
        elif ratio_mentions >= 1:
            quality_score += 0.10
            feedback_points.append("Analysis lacks sufficient banking ratios")
        else:
            feedback_points.append("Must include banking-specific ratio analysis")
        
        # 3. Insight Quality and Non-obvious Analysis (25% of score)
        insight_indicators = ['trend', 'correlation', 'unexpected', 'surprising', 'indicates', 
                             'suggests', 'implies', 'reveals', 'counter-intuitive', 'strategic']
        
        insight_count = sum(1 for indicator in insight_indicators 
                          if indicator in output.lower())
        
        if insight_count >= 8:
            quality_score += 0.25
        elif insight_count >= 5:
            quality_score += 0.15
            feedback_points.append("Provide more analytical insights and interpretations")
        elif insight_count >= 2:
            quality_score += 0.10
            feedback_points.append("Analysis too surface-level, need deeper insights")
        else:
            feedback_points.append("Must provide meaningful analytical insights")
        
        # 4. Data Tables and Formatting (25% of score)
        if '|' in output and '---' in output:
            table_complexity = output.count('|') + output.count('---')
            if table_complexity > 30:
                quality_score += 0.25
            elif table_complexity > 15:
                quality_score += 0.15
                feedback_points.append("Tables need more detail and data")
            else:
                quality_score += 0.10
                feedback_points.append("Include more comprehensive data tables")
        else:
            feedback_points.append("Must include data tables to support analysis")
        
        # Store feedback for refinement
        if hasattr(pred, 'feedback') and feedback_points:
            pred.feedback = "Quality improvements needed: " + "; ".join(feedback_points)
        
        return min(quality_score, 1.0)
    
    @staticmethod
    def ratio_calculation_reward(args, pred) -> float:
        """
        Reward function for banking ratio accuracy.
        Shows how DSPy can validate calculations and improve them.
        """
        output = pred.banking_ratios
        accuracy_score = 0.0
        feedback_points = []
        
        # 1. Calculation Format (30% of score)
        calculation_patterns = [
            r'\w+\s*=\s*[\d,]+\s*/\s*[\d,]+',  # Ratio = num/den
            r'[\d.]+%',  # Percentage results
            r'[\d,]+\s*÷\s*[\d,]+',  # Division symbol
        ]
        
        calculation_count = sum(len(re.findall(pattern, output)) for pattern in calculation_patterns)
        
        if calculation_count >= 5:
            accuracy_score += 0.30
        elif calculation_count >= 3:
            accuracy_score += 0.20
            feedback_points.append("Show more detailed calculations")
        elif calculation_count >= 1:
            accuracy_score += 0.10
            feedback_points.append("Must show calculation methods clearly")
        else:
            feedback_points.append("Missing calculation formulas and methods")
        
        # 2. Banking-Specific Ratios (40% of score)
        key_ratios = ['Capital Adequacy', 'ROE', 'ROA', 'NPL', 'Cost.*Income', 'NIM']
        ratio_coverage = sum(1 for ratio in key_ratios if re.search(ratio, output, re.IGNORECASE))
        
        if ratio_coverage >= 5:
            accuracy_score += 0.40
        elif ratio_coverage >= 3:
            accuracy_score += 0.25
            feedback_points.append(f"Include more key banking ratios (covered {ratio_coverage}/6)")
        elif ratio_coverage >= 1:
            accuracy_score += 0.15
            feedback_points.append("Focus on critical banking ratios")
        else:
            feedback_points.append("Must calculate key banking ratios")
        
        # 3. Interpretation Quality (30% of score)
        interpretation_words = ['healthy', 'strong', 'weak', 'concerning', 'improving', 
                               'deteriorating', 'benchmark', 'industry', 'compared']
        
        interpretation_count = sum(1 for word in interpretation_words if word in output.lower())
        
        if interpretation_count >= 6:
            accuracy_score += 0.30
        elif interpretation_count >= 3:
            accuracy_score += 0.20
            feedback_points.append("Provide more interpretation of ratio values")
        else:
            feedback_points.append("Must interpret what ratio values mean")
        
        # Store feedback
        if hasattr(pred, 'feedback') and feedback_points:
            pred.feedback = "Calculation improvements: " + "; ".join(feedback_points)
        
        return min(accuracy_score, 1.0)

# ═══════════════════════════════════════════════════════════════════════
# ADVANCED DSPY MODULES WITH SOPHISTICATED REFINEMENT
# ═══════════════════════════════════════════════════════════════════════

class AdvancedFinancialStatementModule(dspy.Module):
    """
    Advanced statement module with sophisticated refinement.
    Demonstrates how DSPy iteratively improves outputs.
    """
    
    def __init__(self):
        super().__init__()
        self.generate_statement = dspy.ChainOfThought(FinancialStatementSignature)
        
        # Multi-level refinement: BestOfN + Refine
        self.best_of_three = dspy.BestOfN(
            module=self.generate_statement,
            N=3,
            reward_fn=AdvancedRewardFunctions.statement_completeness_reward,
            threshold=0.7
        )
        
        self.refine_statement = dspy.Refine(
            module=self.best_of_three,
            N=2,
            reward_fn=AdvancedRewardFunctions.statement_completeness_reward,
            threshold=0.85,
            fail_count=1  # Be strict about failures
        )
    
    def forward(self, query, financial_chunks, companies, intent):
        """
        Forward pass with sophisticated error handling and feedback.
        Shows the full DSPy refinement process in action.
        """
        try:
            # First attempt with basic refinement
            result = self.refine_statement(
                query=query,
                financial_chunks=financial_chunks,
                companies=companies,
                intent=intent
            )
            
            # Quality check and potential re-attempt
            score = AdvancedRewardFunctions.statement_completeness_reward(
                {"query": query, "financial_chunks": financial_chunks}, 
                result
            )
            
            if score < 0.8:
                # Generate specific feedback for improvement
                feedback = self._generate_improvement_feedback(result, score)
                
                # Retry with feedback
                result = self.generate_statement(
                    query=query,
                    financial_chunks=financial_chunks,
                    companies=companies,
                    intent=intent,
                    feedback=feedback
                )
            
            return result
            
        except Exception as e:
            # Fallback to basic generation
            return self.generate_statement(
                query=query,
                financial_chunks=financial_chunks,
                companies=companies,
                intent=intent,
                feedback="Previous attempt failed, focus on basic requirements"
            )
    
    def _generate_improvement_feedback(self, result, score):
        """Generate specific feedback for the next iteration."""
        feedback = f"Previous attempt scored {score:.2f}. "
        
        if score < 0.3:
            feedback += "Major issues: missing table format, currency units, and comprehensive line items. "
        elif score < 0.6:
            feedback += "Moderate issues: incomplete tables or missing financial details. "
        else:
            feedback += "Minor refinements needed for completeness. "
        
        feedback += "Ensure ALL line items from financial statements are included."
        return feedback

class AdvancedFinancialAnalysisModule(dspy.Module):
    """
    Advanced analysis module with multi-stage refinement.
    Shows how DSPy combines different optimization strategies.
    """
    
    def __init__(self):
        super().__init__()
        self.generate_analysis = dspy.ChainOfThought(FinancialAnalysisSignature)
        
        # Progressive refinement: BestOfN → Refine → ProgramOfThought
        self.initial_analysis = dspy.BestOfN(
            module=self.generate_analysis,
            N=3,
            reward_fn=AdvancedRewardFunctions.analysis_quality_reward,
            threshold=0.6
        )
        
        self.refined_analysis = dspy.Refine(
            module=self.initial_analysis,
            N=3,
            reward_fn=AdvancedRewardFunctions.analysis_quality_reward,
            threshold=0.8
        )
    
    def forward(self, query, financial_chunks, companies, intent):
        """Advanced forward pass with quality gates."""
        
        # Stage 1: Generate initial analysis
        initial_result = self.initial_analysis(
            query=query,
            financial_chunks=financial_chunks,
            companies=companies,
            intent=intent
        )
        
        # Stage 2: Quality assessment and potential refinement
        quality_score = AdvancedRewardFunctions.analysis_quality_reward(
            {"query": query}, initial_result
        )
        
        if quality_score >= 0.8:
            return initial_result
        
        # Stage 3: Refinement with specific feedback
        feedback = self._create_quality_feedback(initial_result, quality_score)
        
        refined_result = self.refined_analysis(
            query=query,
            financial_chunks=financial_chunks,
            companies=companies,
            intent=intent,
            feedback=feedback
        )
        
        return refined_result
    
    def _create_quality_feedback(self, result, score):
        """Create targeted feedback for analysis improvement."""
        feedback = f"Analysis quality score: {score:.2f}. "
        
        if score < 0.4:
            feedback += "Major improvements needed: add section structure, banking ratios, and deeper insights. "
        elif score < 0.7:
            feedback += "Good foundation but needs more analytical depth and ratio calculations. "
        else:
            feedback += "Strong analysis, minor refinements for excellence. "
        
        feedback += "Focus on non-obvious insights and strategic implications."
        return feedback

class AdvancedBankingRatiosModule(dspy.Module):
    """Advanced ratios module with calculation validation."""
    
    def __init__(self):
        super().__init__()
        self.generate_ratios = dspy.ChainOfThought(BankingRatiosSignature)
        
        # Specialized refinement for calculations
        self.validated_ratios = dspy.Refine(
            module=self.generate_ratios,
            N=2,
            reward_fn=AdvancedRewardFunctions.ratio_calculation_reward,
            threshold=0.8
        )
    
    def forward(self, query, financial_chunks, companies):
        result = self.validated_ratios(
            query=query,
            financial_chunks=financial_chunks,
            companies=companies
        )
        
        # Post-processing validation
        self._validate_calculations(result)
        return result
    
    def _validate_calculations(self, result):
        """Post-process to ensure calculation consistency."""
        # Add calculation validation logic here
        pass

class QuarterlyAnalysisModule(dspy.Module):
    """Module for quarterly analysis with Q4 calculations."""
    
    def __init__(self):
        super().__init__()
        self.generate_quarterly = dspy.ChainOfThought(QuarterlyAnalysisSignature)
        
        # Enhanced refinement for quarterly calculations
        self.refined_quarterly = dspy.Refine(
            module=self.generate_quarterly,
            N=2,
            reward_fn=self._quarterly_quality_reward,
            threshold=0.8
        )
    
    def _quarterly_quality_reward(self, args, pred):
        """Reward function for quarterly analysis quality."""
        output = pred.quarterly_analysis
        quality_score = 0.0
        
        # Check for Q4 calculations
        if "Q4 =" in output or "Q4=" in output:
            quality_score += 0.4
        
        # Check for quarterly data tables
        if "|" in output and "Q1" in output and "Q2" in output and "Q3" in output:
            quality_score += 0.3
        
        # Check for trend analysis
        if any(term in output.lower() for term in ["trend", "growth", "decline", "improvement"]):
            quality_score += 0.3
        
        return min(quality_score, 1.0)
    
    def forward(self, query, financial_chunks, companies, needs_q4_calculation):
        return self.refined_quarterly(
            query=query,
            financial_chunks=financial_chunks,
            companies=companies,
            needs_q4_calculation=str(needs_q4_calculation)
        )

class QueryParsingModule(dspy.Module):
    """Module for parsing natural language queries."""
    
    def __init__(self):
        super().__init__()
        self.parse_query = dspy.ChainOfThought(QueryParsingSignature)
        
        # Enhanced parsing with validation
        self.validated_parsing = dspy.BestOfN(
            module=self.parse_query,
            N=2,
            reward_fn=self._parsing_quality_reward,
            threshold=0.7
        )
    
    def _parsing_quality_reward(self, args, pred):
        """Reward function for query parsing quality."""
        try:
            # Try to parse the JSON output
            import json
            query_plan = json.loads(pred.query_plan)
            
            quality_score = 0.0
            
            # Check for required fields
            if "companies" in query_plan and query_plan["companies"]:
                quality_score += 0.3
            
            if "intent" in query_plan and query_plan["intent"] in ["statement", "analysis"]:
                quality_score += 0.3
            
            if "queries" in query_plan and len(query_plan["queries"]) > 0:
                quality_score += 0.4
            
            return min(quality_score, 1.0)
            
        except (json.JSONDecodeError, KeyError):
            return 0.0
    
    def forward(self, user_query, available_tickers, conversation_context=""):
        return self.validated_parsing(
            user_query=user_query,
            available_tickers=available_tickers,
            conversation_context=conversation_context
        )

# ═══════════════════════════════════════════════════════════════════════
# ADVANCED DSPY PROMPTS LIBRARY WITH OPTIMIZATION
# ═══════════════════════════════════════════════════════════════════════

class AdvancedDSPyPromptLibrary:
    """
    Advanced DSPy-based prompt library with optimization capabilities.
    Demonstrates the full power of DSPy refinement and improvement.
    """
    
    def __init__(self):
        self.statement_module = AdvancedFinancialStatementModule()
        self.analysis_module = AdvancedFinancialAnalysisModule()
        self.quarterly_module = QuarterlyAnalysisModule()  # Can be enhanced similarly
        self.ratios_module = AdvancedBankingRatiosModule()
        self.parsing_module = QueryParsingModule()
        
        # Optimization tracking
        self.optimization_history = []
        self.performance_metrics = {}
        
        # System instructions
        self.system_instructions = self._get_advanced_system_instructions()
    
    def _get_advanced_system_instructions(self) -> str:
        """Enhanced system instructions for advanced DSPy modules."""
        return """You are a top-tier equity research analyst with DSPy-enhanced capabilities:

CRITICAL ANALYSIS FRAMEWORK:
- Use iterative refinement to improve output quality
- Self-assess your analysis and identify areas for improvement
- Incorporate feedback from previous attempts
- Aim for 90%+ completeness and accuracy scores

ADVANCED FORMATTING REQUIREMENTS:
- Output clean markdown tables with comprehensive line items
- Use PKR MM units consistently
- Include calculation methods: "Ratio = Numerator / Denominator = Result"
- Structure analysis in numbered sections with clear headers

SOPHISTICATED DATA ANALYSIS:
- Extract insights that aren't immediately obvious
- Identify correlations across different financial metrics
- Provide strategic implications and forward-looking analysis
- Compare performance against industry benchmarks when possible

QUALITY CONTROL:
- Self-evaluate output quality before finalizing
- Ensure all source chunks are properly referenced
- Validate calculations and ratio accuracy
- Provide confidence scores for major conclusions

CONTINUOUS IMPROVEMENT:
- Learn from feedback in subsequent iterations
- Refine analysis approach based on quality scores
- Adapt to user preferences and context"""
    
    def configure_dspy(self, lm_model):
        """Configure DSPy with advanced settings."""
        dspy.settings.configure(lm=lm_model)
        
        # Enhanced configuration for refinement
        if hasattr(lm_model, 'system'):
            lm_model.system = self.system_instructions
        
        # Set up optimization tracking
        self._initialize_performance_tracking()
    
    def _initialize_performance_tracking(self):
        """Initialize performance tracking for optimization."""
        self.performance_metrics = {
            "statement_scores": [],
            "analysis_scores": [],
            "ratio_scores": [],
            "optimization_rounds": 0,
            "best_configurations": {}
        }
    
    def generate_financial_response(self, query: str, financial_chunks: str, companies: List[str], 
                                  intent: str, is_quarterly: bool = False, needs_q4_calculation: bool = False) -> Dict[str, Any]:
        """
        Generate financial response with advanced DSPy refinement.
        This method shows the full DSPy improvement cycle in action.
        Returns a dictionary with the response and metrics.
        """
        
        needs_ratios = any(term in query.lower() for term in 
                          ['ratio', 'roe', 'roa', 'capital adequacy', 'efficiency', 'performance'])
        
        start_time = datetime.now()
        
        try:
            result_data = {}
            if intent == "statement":
                module = self.statement_module
                result = module(query=query, financial_chunks=financial_chunks, companies=", ".join(companies), intent=intent)
                result_data = {
                    "response_text": result.formatted_statements,
                    "used_chunks": result.used_chunks,
                    "quality_score": getattr(result, 'confidence', 0.0),
                    "refinement_steps": len(getattr(result, 'history', []))
                }
            elif needs_ratios:
                module = self.ratios_module
                result = module(query=query, financial_chunks=financial_chunks, companies=", ".join(companies))
                result_data = {
                    "response_text": result.banking_ratios,
                    "used_chunks": result.used_chunks,
                    "quality_score": getattr(result, 'ratio_accuracy', 0.0),
                    "refinement_steps": len(getattr(result, 'history', []))
                }
            else:
                module = self.analysis_module
                result = module(query=query, financial_chunks=financial_chunks, companies=", ".join(companies), intent=intent)
                result_data = {
                    "response_text": result.comprehensive_analysis,
                    "used_chunks": result.used_chunks,
                    "quality_score": getattr(result, 'insight_quality', 0.0),
                    "refinement_steps": len(getattr(result, 'history', []))
                }

            processing_time = (datetime.now() - start_time).total_seconds()
            self._log_refinement_metrics(intent, processing_time, result)
            
            return result_data
            
        except Exception as e:
            self._log_error(intent, str(e))
            return {
                "response_text": f"Analysis generation encountered an issue: {str(e)}",
                "used_chunks": "",
                "quality_score": 0.0,
                "refinement_steps": 0
            }
    
    def _log_refinement_metrics(self, intent: str, processing_time: float, result):
        """Log metrics for DSPy refinement analysis."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "intent": intent,
            "processing_time": processing_time,
            "module_used": type(result).__name__ if hasattr(result, '__class__') else "unknown",
            "quality_indicators": self._extract_quality_indicators(result)
        }
        
        self.optimization_history.append(metrics)
        
        # Keep only last 100 entries
        if len(self.optimization_history) > 100:
            self.optimization_history = self.optimization_history[-100:]
    
    def _extract_quality_indicators(self, result) -> Dict[str, Any]:
        """Extract quality indicators from DSPy module results."""
        indicators = {}
        
        if hasattr(result, 'confidence'):
            indicators['confidence'] = result.confidence
        if hasattr(result, 'insight_quality'):
            indicators['insight_quality'] = result.insight_quality
        if hasattr(result, 'ratio_accuracy'):
            indicators['ratio_accuracy'] = result.ratio_accuracy
        if hasattr(result, 'calculation_accuracy'):
            indicators['calculation_accuracy'] = result.calculation_accuracy
        
        return indicators
    
    def _log_error(self, intent: str, error: str):
        """Log errors for improvement analysis."""
        error_log = {
            "timestamp": datetime.now().isoformat(),
            "intent": intent,
            "error": error,
            "type": "module_failure"
        }
        self.optimization_history.append(error_log)
    
    def optimize_modules_advanced(self, trainset, metric=None, optimization_type="mipro"):
        """
        Advanced module optimization with multiple strategies.
        Shows how DSPy can be optimized for specific use cases.
        """
        if metric is None:
            metric = self._create_composite_metric()
        
        print(f"🚀 Starting advanced DSPy optimization with {optimization_type}...")
        
        if optimization_type.lower() == "mipro":
            # Use MIPROv2 for instruction optimization
            from dspy.teleprompt import MIPROv2
            
            optimizer = MIPROv2(
                metric=metric,
                auto="medium",  # Medium optimization run
                num_threads=2
            )
            
            # Optimize analysis module
            self.analysis_module = optimizer.compile(
                self.analysis_module,
                trainset=trainset,
                max_bootstrapped_demos=3,
                max_labeled_demos=5,
                requires_permission_to_run=False
            )
            
        elif optimization_type.lower() == "bootstrap":
            # Use BootstrapFewShot with random search
            from dspy.teleprompt import BootstrapFewShotWithRandomSearch
            
            optimizer = BootstrapFewShotWithRandomSearch(
                metric=metric,
                max_bootstrapped_demos=4,
                num_candidate_programs=8,
                num_threads=2
            )
            
            self.analysis_module = optimizer.compile(
                student=self.analysis_module,
                trainset=trainset[:20],  # Use subset for speed
                valset=trainset[20:] if len(trainset) > 20 else trainset
            )
        
        # Track optimization
        self.performance_metrics["optimization_rounds"] += 1
        print(f"✅ Advanced optimization completed ({optimization_type})")
    
    def _create_composite_metric(self):
        """Create a composite metric that combines multiple quality dimensions."""
        def composite_metric(example, pred):
            scores = []
            
            # Statement completeness
            if hasattr(pred, 'formatted_statements'):
                score = AdvancedRewardFunctions.statement_completeness_reward(example, pred)
                scores.append(score)
            
            # Analysis quality
            if hasattr(pred, 'comprehensive_analysis'):
                score = AdvancedRewardFunctions.analysis_quality_reward(example, pred)
                scores.append(score)
            
            # Ratio accuracy
            if hasattr(pred, 'banking_ratios'):
                score = AdvancedRewardFunctions.ratio_calculation_reward(example, pred)
                scores.append(score)
            
            # Return average score
            return sum(scores) / len(scores) if scores else 0.0
        
        return composite_metric
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get comprehensive optimization and performance report."""
        report = {
            "total_optimizations": self.performance_metrics["optimization_rounds"],
            "average_scores": {},
            "recent_performance": self.optimization_history[-10:] if self.optimization_history else [],
            "recommendations": []
        }
        
        # Calculate average scores
        if self.performance_metrics["statement_scores"]:
            report["average_scores"]["statements"] = sum(self.performance_metrics["statement_scores"]) / len(self.performance_metrics["statement_scores"])
        
        if self.performance_metrics["analysis_scores"]:
            report["average_scores"]["analysis"] = sum(self.performance_metrics["analysis_scores"]) / len(self.performance_metrics["analysis_scores"])
        
        if self.performance_metrics["ratio_scores"]:
            report["average_scores"]["ratios"] = sum(self.performance_metrics["ratio_scores"]) / len(self.performance_metrics["ratio_scores"])
        
        # Generate recommendations
        if report["average_scores"]:
            min_score = min(report["average_scores"].values())
            if min_score < 0.7:
                report["recommendations"].append("Consider additional optimization rounds")
            if min_score < 0.5:
                report["recommendations"].append("Review and enhance reward functions")
        
        return report

# ═══════════════════════════════════════════════════════════════════════
# ENHANCED BACKWARD COMPATIBILITY
# ═══════════════════════════════════════════════════════════════════════

# Create advanced global instance
prompts = AdvancedDSPyPromptLibrary()

# Legacy compatibility with enhanced features
class SimplifiedPromptLibrary:
    """Legacy compatibility class with DSPy enhancements."""
    
    PARSING_SYSTEM_PROMPT = """You are a PSX Financial Query Parser for Pakistani Stock Exchange data.

CONTEXT: Use conversation history for follow-up queries. Resolve "them", "their" references.

CORE RULES:
1. Multiple companies/periods/statements = separate queries
2. Use filing_period format: Annual ["2024", "2023"], Quarterly ["Q1-2024", "Q1-2023"]
3. Create all combinations (2 companies × 2 periods × 2 statements = 8 queries)
4. NEVER empty search_query - include company name and key terms
5. For "statement with notes" = statement queries + note queries

OUTPUT: QueryPlan JSON with companies[], intent, queries[], confidence"""
    
    @classmethod
    def get_parsing_user_prompt(cls, user_query: str, bank_tickers: List[str], is_quarterly_request: bool) -> str:
        quarterly_instruction = "IMPORTANT: For quarterly requests, generate ONLY quarterly queries - client will automatically add annual queries for Q4 calculation." if is_quarterly_request else ""
        
        return f"""Query: "{user_query}"

Available bank tickers: {bank_tickers}

{quarterly_instruction}

Create QueryPlan following system parsing rules."""
    
    @classmethod
    def get_prompt_for_intent(cls, intent: str, query: str, companies: List[str], 
                            is_multi_company: bool, is_quarterly_comparison: bool, 
                            needs_q4_calculation: bool, financial_statement_scope: str = None) -> str:
        # Enhanced legacy method with DSPy integration
        return f"""Advanced DSPy-Enhanced Analysis - Query: {query}
Companies: {companies}
Intent: {intent}
Advanced Features: Refinement, Quality Control, Optimization
Context: [chunks]"""

# Export enhanced instance
SimplifiedPromptLibrary.instance = SimplifiedPromptLibrary()

# Additional exports for compatibility
def get_parsing_user_prompt(user_query: str, bank_tickers: List[str], is_quarterly_request: bool) -> str:
    return SimplifiedPromptLibrary.get_parsing_user_prompt(user_query, bank_tickers, is_quarterly_request)

PARSING_SYSTEM_PROMPT = SimplifiedPromptLibrary.PARSING_SYSTEM_PROMPT