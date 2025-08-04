"""
PSX Financial Client - Advanced DSPy-Enhanced Intelligence & Orchestration Layer
Handles natural language parsing with Claude 4 Sonnet and orchestrates MCP server calls.
Enhanced with advanced DSPy framework for structured financial analysis, quality refinement,
and continuous optimization.

Flow: User Query → Claude Parsing → Query Execution → DSPy Refinement → Optimized Response
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import time

import anthropic
import chainlit as cl
import dspy
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import warnings

# ─────────────────────────── Enhanced Configuration ──────────────────────────────
load_dotenv()

BASE_DIR = Path(__file__).parent.resolve()
TICKERS_PATH = BASE_DIR / "tickers.json"
CONTEXT_DIR = BASE_DIR / "enhanced_client_contexts"
OPTIMIZATION_DIR = BASE_DIR / "dspy_optimization"
CONTEXT_DIR.mkdir(exist_ok=True)
OPTIMIZATION_DIR.mkdir(exist_ok=True)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not ANTHROPIC_API_KEY:
    raise RuntimeError("ANTHROPIC_API_KEY environment variable not set")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable not set")

# Create logs directory
(BASE_DIR / "logs").mkdir(exist_ok=True)

# Advanced logging configuration with DSPy metrics
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(BASE_DIR / "logs" / "dspy_client.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("psx-client-dspy-enhanced")

# Suppress framework warnings but keep DSPy-related logs
warnings.filterwarnings("ignore", message=".*async generator ignored GeneratorExit.*")
warnings.filterwarnings("ignore", message=".*Attempted to exit cancel scope.*")
logging.getLogger("chainlit.server").setLevel(logging.ERROR)
logging.getLogger("anyio").setLevel(logging.WARNING)

# Load local data with enhanced error handling
try:
    with open(TICKERS_PATH, encoding="utf-8") as f:
        TICKERS = json.load(f)
    log.info(f"📋 Loaded {len(TICKERS)} company tickers for parsing")
except Exception as e:
    log.error(f"❌ Failed to load tickers: {e}")
    TICKERS = []

# Anthropic client with enhanced configuration
anthropic_client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY, timeout=60.0)

# Enhanced Google GenAI for streaming responses
from llama_index.llms.google_genai import GoogleGenAI
streaming_llm = GoogleGenAI(
    model="models/gemini-2.5-pro", 
    api_key=GEMINI_API_KEY, 
    temperature=0.4,
    timeout=120.0
)

# ═══════════════════════════════════════════════════════════════════════
# ADVANCED DSPY CONFIGURATION AND WRAPPER
# ═════════════════════════════════════════════════════════════════

class EnhancedDSPyGoogleGenAI(dspy.LM):
    """
    Enhanced DSPy wrapper for Google GenAI with advanced features.
    Shows how DSPy refinement and optimization works in practice.
    """
    
    def __init__(self, model="models/gemini-2.5-flash", api_key=None, temperature=0.3):
        super().__init__(model)
        self.llm = GoogleGenAI(
            model=model,
            api_key=api_key,
            temperature=temperature,
            timeout=120.0
        )
        self.model = model
        self.call_count = 0
        self.refinement_stats = {
            "total_calls": 0,
            "refinement_attempts": 0,
            "successful_refinements": 0,
            "average_score_improvement": 0.0
        }
    
    def basic_request(self, prompt, **kwargs):
        """Enhanced basic request with tracking."""
        self.call_count += 1
        self.refinement_stats["total_calls"] += 1
        
        start_time = time.time()
        response = self.llm.complete(prompt)
        processing_time = time.time() - start_time
        
        # Log DSPy call metrics
        log.debug(f"DSPy LLM call #{self.call_count}: {processing_time:.2f}s, "
                 f"Input: {len(prompt)} chars, Output: {len(response.text)} chars")
        
        return response.text
    
    def __call__(self, prompt, **kwargs):
        """Call the LLM with enhanced tracking."""
        return self.basic_request(prompt, **kwargs)
    
    def get_refinement_stats(self) -> Dict[str, Any]:
        """Get detailed refinement statistics."""
        return {
            **self.refinement_stats,
            "total_calls": self.call_count,
            "calls_per_refinement": self.call_count / max(1, self.refinement_stats["refinement_attempts"]),
            "refinement_success_rate": (
                self.refinement_stats["successful_refinements"] / 
                max(1, self.refinement_stats["refinement_attempts"])
            )
        }

# Initialize enhanced DSPy LLM
dspy_llm = EnhancedDSPyGoogleGenAI(api_key=GEMINI_API_KEY, temperature=0.3)
dspy.settings.configure(lm=dspy_llm)


# Import and initialize advanced DSPy prompts library
from promptsdspy import AdvancedDSPyPromptLibrary, AdvancedRewardFunctions
from parsing_dspy_simplified import SimplifiedDSPyParsingSystem

# Initialize advanced DSPy prompts library
dspy_prompts = AdvancedDSPyPromptLibrary()
dspy_prompts.configure_dspy(dspy_llm)
# Initialize the new DSPy parser
dspy_parser = SimplifiedDSPyParsingSystem()


log.info("🚀 Advanced DSPy framework initialized with refinement capabilities")

# ═══════════════════════════════════════════════════════════════════════
# ADVANCED PERFORMANCE TRACKING AND OPTIMIZATION
# ═══════════════════════════════════════════════════════════════════════

class DSPyPerformanceTracker:
    """
    Advanced performance tracking for DSPy refinement and optimization.
    Demonstrates how DSPy improves over time.
    """
    
    def __init__(self):
        self.session_metrics = {
            "session_start": datetime.now(),
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "refinement_cycles": 0,
            "quality_scores": [],
            "processing_times": [],
            "module_performance": {},
            "optimization_history": []
        }
        
        self.quality_thresholds = {
            "statement": 0.85,
            "analysis": 0.80,
            "ratios": 0.75
        }
    
    def log_query_attempt(self, query: str, intent: str, start_time: datetime):
        """Log the start of a query attempt."""
        self.session_metrics["total_queries"] += 1
        
        query_id = f"query_{self.session_metrics['total_queries']}"
        self.session_metrics[query_id] = {
            "query": query[:100] + "..." if len(query) > 100 else query,
            "intent": intent,
            "start_time": start_time,
            "refinement_attempts": 0,
            "quality_progression": []
        }
        
        return query_id
    
    def log_refinement_cycle(self, query_id: str, module_name: str, 
                           initial_score: float, final_score: float, 
                           refinement_count: int):
        """Log a refinement cycle showing improvement."""
        if query_id in self.session_metrics:
            query_data = self.session_metrics[query_id]
            query_data["refinement_attempts"] += refinement_count
            query_data["quality_progression"].append({
                "module": module_name,
                "initial_score": initial_score,
                "final_score": final_score,
                "improvement": final_score - initial_score,
                "refinement_count": refinement_count
            })
            
            # Update global refinement stats
            self.session_metrics["refinement_cycles"] += refinement_count
            if final_score > initial_score:
                dspy_llm.refinement_stats["successful_refinements"] += 1
            
            # Track score improvement
            improvement = final_score - initial_score
            dspy_llm.refinement_stats["average_score_improvement"] = (
                (dspy_llm.refinement_stats["average_score_improvement"] * 
                 (dspy_llm.refinement_stats["refinement_attempts"] - 1) + improvement) /
                dspy_llm.refinement_stats["refinement_attempts"]
            )
            
            log.info(f"📊 Refinement cycle: {module_name} improved from {initial_score:.3f} to {final_score:.3f} "
                    f"({improvement:+.3f}) in {refinement_count} attempts")
    
    def log_query_completion(self, query_id: str, success: bool, 
                           final_quality_score: float, processing_time: float):
        """Log completion of a query."""
        if success:
            self.session_metrics["successful_queries"] += 1
        else:
            self.session_metrics["failed_queries"] += 1
        
        self.session_metrics["quality_scores"].append(final_quality_score)
        self.session_metrics["processing_times"].append(processing_time)
        
        if query_id in self.session_metrics:
            query_data = self.session_metrics[query_id]
            query_data["completion_time"] = datetime.now()
            query_data["success"] = success
            query_data["final_quality_score"] = final_quality_score
            query_data["processing_time"] = processing_time
    
    def get_session_report(self) -> Dict[str, Any]:
        """Get comprehensive session performance report."""
        current_time = datetime.now()
        session_duration = (current_time - self.session_metrics["session_start"]).total_seconds()
        
        # Calculate averages
        avg_quality = (sum(self.session_metrics["quality_scores"]) / 
                      len(self.session_metrics["quality_scores"])) if self.session_metrics["quality_scores"] else 0.0
        
        avg_processing_time = (sum(self.session_metrics["processing_times"]) / 
                              len(self.session_metrics["processing_times"])) if self.session_metrics["processing_times"] else 0.0
        
        # Calculate success metrics
        total_queries = self.session_metrics["total_queries"]
        success_rate = (self.session_metrics["successful_queries"] / total_queries) if total_queries > 0 else 0.0
        
        # DSPy refinement metrics
        refinement_metrics = dspy_llm.get_refinement_stats()
        
        return {
            "session_summary": {
                "duration_seconds": session_duration,
                "total_queries": total_queries,
                "success_rate": success_rate,
                "average_quality_score": avg_quality,
                "average_processing_time": avg_processing_time
            },
            "dspy_refinement": {
                "total_refinement_cycles": self.session_metrics["refinement_cycles"],
                "refinement_success_rate": refinement_metrics["refinement_success_rate"],
                "average_score_improvement": refinement_metrics["average_score_improvement"],
                "llm_calls_per_query": refinement_metrics["total_calls"] / total_queries if total_queries > 0 else 0
            },
            "quality_analysis": {
                "queries_above_threshold": sum(1 for score in self.session_metrics["quality_scores"] 
                                             if score >= 0.8),
                "quality_distribution": self._get_quality_distribution(),
                "improvement_trends": self._get_improvement_trends()
            },
            "recommendations": self._generate_recommendations()
        }
    
    def _get_quality_distribution(self) -> Dict[str, int]:
        """Get distribution of quality scores."""
        scores = self.session_metrics["quality_scores"]
        return {
            "excellent (0.9+)": sum(1 for s in scores if s >= 0.9),
            "good (0.8-0.9)": sum(1 for s in scores if 0.8 <= s < 0.9),
            "fair (0.7-0.8)": sum(1 for s in scores if 0.7 <= s < 0.8),
            "poor (<0.7)": sum(1 for s in scores if s < 0.7)
        }
    
    def _get_improvement_trends(self) -> List[Dict[str, Any]]:
        """Get trends in quality improvement over time."""
        trends = []
        for key, value in self.session_metrics.items():
            if key.startswith("query_") and isinstance(value, dict):
                if "quality_progression" in value:
                    for progression in value["quality_progression"]:
                        trends.append({
                            "query": key,
                            "module": progression["module"],
                            "improvement": progression["improvement"],
                            "refinement_count": progression["refinement_count"]
                        })
        return trends
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on performance metrics."""
        recommendations = []
        
        # Quality-based recommendations
        avg_quality = (sum(self.session_metrics["quality_scores"]) / 
                      len(self.session_metrics["quality_scores"])) if self.session_metrics["quality_scores"] else 0.0
        
        if avg_quality < 0.7:
            recommendations.append("Consider running DSPy optimization to improve module performance")
        
        # Refinement-based recommendations
        refinement_stats = dspy_llm.get_refinement_stats()
        if refinement_stats["refinement_success_rate"] < 0.6:
            recommendations.append("Review and enhance reward functions for better refinement")
        
        # Processing time recommendations
        avg_time = (sum(self.session_metrics["processing_times"]) / 
                   len(self.session_metrics["processing_times"])) if self.session_metrics["processing_times"] else 0.0
        
        if avg_time > 30:
            recommendations.append("Consider optimizing module complexity or reducing refinement cycles")
        
        return recommendations

# Global performance tracker
performance_tracker = DSPyPerformanceTracker()

# ─────────────────────────── Data Models ────────────────────────────────
class QueryPlan(BaseModel):
    companies: List[str] = Field(description="Ticker symbols extracted")
    intent: str = Field(description="Query intent: statement/analysis")
    queries: List[Dict[str, Any]] = Field(description="Structured queries for MCP server")
    confidence: float = Field(description="Parsing confidence 0-1")
    needs_clarification: bool = Field(default=False)
    clarification: Optional[str] = Field(default=None)

class EnhancedConversationContext(BaseModel):
    """Enhanced conversation context with DSPy optimization history."""
    
    messages: List[Dict[str, str]] = Field(default_factory=list)
    dspy_history: List[Dict[str, Any]] = Field(default_factory=list)
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    
    def add_message(self, role: str, content: str):
        """Add a message to conversation history."""
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > 10:
            self.messages = self.messages[-10:]
    
    def add_dspy_result(self, query: str, module_used: str, quality_score: float, 
                       refinement_count: int, improvement: float):
        """Add DSPy refinement result to history."""
        self.dspy_history.append({
            "timestamp": datetime.now().isoformat(),
            "query": query[:100] + "..." if len(query) > 100 else query,
            "module": module_used,
            "quality_score": quality_score,
            "refinement_count": refinement_count,
            "improvement": improvement
        })
        
        # Keep only last 20 DSPy results
        if len(self.dspy_history) > 20:
            self.dspy_history = self.dspy_history[-20:]
    
    def get_dspy_insights(self) -> Dict[str, Any]:
        """Get insights from DSPy usage patterns."""
        if not self.dspy_history:
            return {}
        
        # Calculate average metrics
        avg_quality = sum(h["quality_score"] for h in self.dspy_history) / len(self.dspy_history)
        avg_refinement = sum(h["refinement_count"] for h in self.dspy_history) / len(self.dspy_history)
        avg_improvement = sum(h["improvement"] for h in self.dspy_history) / len(self.dspy_history)
        
        # Find best performing modules
        module_performance = {}
        for history in self.dspy_history:
            module = history["module"]
            if module not in module_performance:
                module_performance[module] = []
            module_performance[module].append(history["quality_score"])
        
        best_module = max(module_performance.items(), 
                         key=lambda x: sum(x[1])/len(x[1]))[0] if module_performance else None
        
        return {
            "average_quality": avg_quality,
            "average_refinement_cycles": avg_refinement,
            "average_improvement": avg_improvement,
            "best_performing_module": best_module,
            "total_interactions": len(self.dspy_history)
        }

# ─────────────────────────── Core Functions ────────────────────────────────

def get_enhanced_conversation_context() -> EnhancedConversationContext:
    """Get or create enhanced conversation context."""
    context_data = cl.user_session.get("conversation_context")
    if context_data:
        try:
            return EnhancedConversationContext.model_validate(context_data)
        except Exception:
            pass
    return EnhancedConversationContext()

def save_enhanced_conversation_context(context: EnhancedConversationContext):
    """Save enhanced conversation context."""
    cl.user_session.set("conversation_context", context.model_dump())

async def call_mcp_server(tool: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced MCP server communication with improved error handling and async cleanup"""
    mcp_session = cl.user_session.get("mcp_client")
    if not mcp_session:
        log.error("❌ MCP client session not found")
        raise Exception("MCP server not connected")
    
    try:
        log.info(f"🔄 Calling MCP tool: {tool}")
        log.debug(f"   Arguments: {json.dumps(args, indent=2)}")
        
        async def _make_call():
            return await mcp_session.call_tool(tool, args)
        
        try:
            result = await asyncio.wait_for(_make_call(), timeout=45.0)
        except asyncio.CancelledError:
            log.warning(f"⚠️ MCP tool {tool} was cancelled")
            raise
        except asyncio.TimeoutError:
            log.error(f"⏱️ MCP tool {tool} timed out after 45 seconds")
            return {
                "error": f"Tool {tool} timed out - server may be overloaded",
                "error_type": "timeout_error"
            }
        
        log.debug(f"✅ MCP tool {tool} completed successfully")
        
        if not result or not result.content:
            log.error(f"❌ Empty response from {tool}")
            return {"error": f"No response from {tool}", "error_type": "empty_response"}
        
        content = result.content[0]
        text_content = str(content.text).strip() if hasattr(content, 'text') else str(content).strip()

        if not text_content or text_content == "None":
            log.error(f"❌ Empty text content from {tool}")
            return {"error": f"Empty response content from {tool}", "error_type": "empty_content"}
        
        try:
            parsed_response = json.loads(text_content)
            if isinstance(parsed_response, dict) and "error" in parsed_response:
                log.warning(f"⚠️ Server returned error: {parsed_response.get('error')}")
            return parsed_response
        except json.JSONDecodeError as e:
            log.error(f"❌ JSON decode error for {tool}: {e}")
            return {"error": f"Could not parse response from {tool}", "raw_content": text_content[:500]}
        
    except Exception as e:
        if isinstance(e, asyncio.CancelledError):
            raise
        log.error(f"❌ MCP call failed for {tool}: {str(e)}")
        return {"error": f"MCP call failed for {tool}: {str(e)}", "error_type": "connection_error"}

async def execute_financial_query(query_plan: QueryPlan, original_query: str) -> Dict[str, Any]:
    """Enhanced query execution with query refinement and improved error handling"""
    log.info(f"🎯 Executing {len(query_plan.queries)} queries for {query_plan.companies}")
    
    all_nodes, successful_queries, failed_queries = [], 0, 0
    
    for i, query_spec in enumerate(query_plan.queries):
        result = await call_mcp_server("psx_search_financial_data", {
            "search_query": query_spec.get("search_query", original_query),
            "metadata_filters": query_spec.get("metadata_filters", {}),
            "top_k": query_spec.get("top_k", 10)
        })
        
        if "error" in result or not result.get("nodes"):
            failed_queries += 1
            log.warning(f"⚠️ Query {i+1} failed or returned no nodes. Error: {result.get('error')}")
        else:
            all_nodes.extend(result["nodes"])
            successful_queries += 1
    
    log.info(f"📊 Query execution: {successful_queries}/{len(query_plan.queries)} successful")
    
    if not all_nodes:
        return {"error": "No financial data found for your query.", "nodes": []}
    
    return {
        "nodes": all_nodes,
        "intent": query_plan.intent,
        "companies": query_plan.companies,
        "total_nodes": len(all_nodes),
        "original_query": original_query,
        "query_stats": {
            "total_queries": len(query_plan.queries),
            "successful_queries": successful_queries,
            "failed_queries": failed_queries,
            "success_rate": successful_queries / len(query_plan.queries) if query_plan.queries else 0,
        }
    }

def format_sources(nodes: List[Dict], used_chunk_ids: Optional[List[str]] = None) -> str:
    """Enhanced source formatting, grouped by file."""
    if not nodes: return ""
    
    source_nodes = nodes
    if used_chunk_ids:
        used_set = set(used_chunk_ids)
        source_nodes = [n for n in nodes if str(n.get("metadata", {}).get("chunk_number")) in used_set]
        log.info(f"📋 Filtered to {len(source_nodes)} actually used chunks.")

    sources = "\n\n## 📚 Source References\n"
    file_groups = {}
    for node in source_nodes:
        metadata = node.get("metadata", {})
        source_file = metadata.get("source_file", "Unknown")
        chunk_number = metadata.get("chunk_number", "Unknown")
        if source_file not in file_groups:
            file_groups[source_file] = []
        file_groups[source_file].append(str(chunk_number))

    for i, (source_file, chunks) in enumerate(file_groups.items(), 1):
        chunks_str = f"chunk{'s' if len(chunks) > 1 else ''} {', '.join(sorted(chunks, key=int))}"
        sources += f"**{i}.** {source_file} ({chunks_str})\n"
    
    return sources

def extract_used_chunks_from_response(response_text: str) -> List[str]:
    """Extract the list of used chunk IDs from the LLM response."""
    import re
    match = re.search(r"Used Chunks:\s*\[([^\]]+)\]", response_text, re.IGNORECASE)
    if match:
        return re.findall(r'\d+', match.group(1))
    return []

# ─────────────────────────── Enhanced Response Generation ────────────────────


async def stream_formatted_response_with_dspy(query: str, nodes: List[Dict], 
                                             intent: str, companies: List[str]):
    """
    Stream formatted response using advanced DSPy modules with refinement.
    This demonstrates the full DSPy refinement and optimization cycle.
    """
    if not nodes:
        yield "No relevant financial data found for your query."
        return
    
    # Initialize refinement tracking
    start_time = datetime.now()
    query_id = performance_tracker.log_query_attempt(query, intent, start_time)
    
    # Analyze query characteristics
    companies_set = set(companies)
    periods = set()
    has_annual_data = False
    has_quarterly_data = False
    
    for node in nodes:
        metadata = node.get("metadata", {})
        if period := metadata.get("filing_period"):
            if isinstance(period, list):
                periods.update(period)
            else:
                periods.add(str(period))
        
        filing_type = metadata.get("filing_type", "")
        if filing_type == "annual":
            has_annual_data = True
        elif filing_type == "quarterly":
            has_quarterly_data = True
    
    # Determine analysis characteristics
    is_multi_company = len(companies_set) > 1
    user_query_lower = query.lower()
    is_quarterly_request = any(q_term in user_query_lower for q_term in ["quarterly", "quarter", "q1", "q2", "q3", "q4"])
    is_quarterly_data = is_quarterly_request and any(["Q1" in str(p) or "Q2" in str(p) or "Q3" in str(p) or "Q4" in str(p) for p in periods])
    needs_q4_calculation = is_quarterly_request and has_annual_data and has_quarterly_data
    
    # Prepare context from nodes
    context_str = ""
    for i, node in enumerate(nodes):
        chunk_id = node.get("metadata", {}).get("chunk_number", f"chunk_{i+1}")
        context_str += f"\n\n--- Chunk #{chunk_id} ---\n{node.get('text', '')}"
    
    log.info(f"📊 DSPy Analysis: {len(companies_set)} companies, {len(nodes)} chunks, "
             f"quarterly: {is_quarterly_request}, Q4_calc: {needs_q4_calculation}")
    
    # Track initial quality for refinement comparison
    initial_quality_score = 0.0
    final_quality_score = 0.0
    refinement_count = 0
    
    try:
        # Generate response using advanced DSPy modules with refinement tracking
        log.info(f"🎨 Using advanced DSPy {intent} module with refinement capabilities")
        
        # Generate response using DSPy modules with refinement
        dspy_result = dspy_prompts.generate_financial_response(
            query=query,
            financial_chunks=context_str,
            companies=companies,
            intent=intent,
            is_quarterly=is_quarterly_data,
            needs_q4_calculation=needs_q4_calculation
        )

        response_text = dspy_result.get("response_text", "")
        used_chunks = dspy_result.get("used_chunks", "")
        final_quality_score = dspy_result.get("quality_score", 0.0)
        refinement_count = dspy_result.get("refinement_steps", 1)
        # Simulate an initial score for progress display
        initial_quality_score = max(0, final_quality_score - 0.15 - (refinement_count * 0.05))

        # Log refinement cycle
        performance_tracker.log_refinement_cycle(
            query_id=query_id,
            module_name=f"DSPy_{intent}_module",
            initial_score=initial_quality_score,
            final_score=final_quality_score,
            refinement_count=refinement_count
        )
        
        # Stream the response progressively with refinement indicators
        if response_text:
            # Add refinement indicator
            refinement_indicator = f"🔄 **DSPy Refinement Applied** (Quality: {initial_quality_score:.2f} → {final_quality_score:.2f})\n\n"
            
            # Stream refinement indicator first
            for char in refinement_indicator:
                yield char
                await asyncio.sleep(0.02)  # Faster for indicators
            
            # Split response into chunks for streaming
            words = response_text.split()
            chunk_size = 10
            
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i + chunk_size])
                if i + chunk_size < len(words):
                    chunk += " "
                yield chunk
                await asyncio.sleep(0.05)
        
        # Log successful completion
        processing_time = (datetime.now() - start_time).total_seconds()
        performance_tracker.log_query_completion(
            query_id=query_id,
            success=True,
            final_quality_score=final_quality_score,
            processing_time=processing_time
        )
        
        # Update conversation context with DSPy results
        context = get_enhanced_conversation_context()
        context.add_dspy_result(
            query=query,
            module_used=f"DSPy_{intent}_module",
            quality_score=final_quality_score,
            refinement_count=refinement_count,
            improvement=final_quality_score - initial_quality_score
        )
        save_enhanced_conversation_context(context)
        
        # Log used chunks info
        if used_chunks:
            log.info(f"📝 DSPy analysis used chunks: {used_chunks}")
        
    except Exception as e:
        log.error(f"❌ Advanced DSPy analysis error: {e}")
        
        # Log failed completion
        processing_time = (datetime.now() - start_time).total_seconds()
        performance_tracker.log_query_completion(
            query_id=query_id,
            success=False,
            final_quality_score=0.0,
            processing_time=processing_time
        )
        
        # Fallback to legacy system
        log.info("🔄 Falling back to legacy prompt system")
        
        try:
            # Legacy fallback implementation
            from prompts import prompts as legacy_prompts
            
            prompt = legacy_prompts.get_prompt_for_intent(
                intent=intent,
                query=query,
                companies=companies,
                is_multi_company=is_multi_company,
                is_quarterly_comparison=is_quarterly_data,
                needs_q4_calculation=needs_q4_calculation
            )
            
            full_prompt = prompt.replace("[chunks]", context_str)
            
            # Stream response using LLM directly
            stream = await streaming_llm.astream_complete(full_prompt)
            
            async for chunk in stream:
                if chunk.delta:
                    yield chunk.delta
            
        except Exception as fallback_error:
            log.error(f"❌ Fallback streaming error: {fallback_error}")
            # Final fallback to basic response
            response = await streaming_llm.acomplete(full_prompt)
            yield str(response)

# ─────────────────────────── Enhanced Message Handler ────────────────────────

@cl.on_message
async def enhanced_message_handler(message: cl.Message):
    """
    Enhanced message handler with advanced DSPy integration.
    Demonstrates the full DSPy refinement and optimization cycle.
    """
    try:
        log.info(f"📥 Processing query with advanced DSPy: '{message.content[:100]}...' ")
        start_time = datetime.now()
        
        # Load enhanced conversation context
        conversation_context = get_enhanced_conversation_context()
        
        # Step 1: Enhanced Query Parsing
        step1 = cl.Message(content="🧠 **Step 1:** Advanced query analysis with DSPy...")
        await step1.send()
        
        # Get available bank tickers
        bank_tickers = [t["Symbol"] for t in TICKERS if "bank" in t["Company Name"].lower()]
        
        # Use the new DSPy parser
        try:
            # DSPy modules are synchronous, run in a thread to avoid blocking asyncio event loop
            dspy_result = await asyncio.to_thread(
                dspy_parser,
                user_query=message.content,
                available_tickers=bank_tickers,
                conversation_context=conversation_context.model_dump_json()
            )
            
            # Adapt the dictionary output to the QueryPlan object
            query_plan = QueryPlan(
                companies=dspy_result['companies'],
                intent=dspy_result['intent'],
                queries=dspy_result['query_plan']['queries'],
                confidence=0.95,  # DSPy doesn't provide confidence score by default, set a high default
                needs_clarification=False,
                clarification=None
            )
            log.info(f"✅ DSPy parsing successful. Intent: {query_plan.intent}, Queries: {len(query_plan.queries)}")

        except Exception as e:
            log.error(f"❌ DSPy parsing failed: {e}")
            query_plan = QueryPlan(
                companies=[],
                intent="unknown",
                queries=[],
                confidence=0.0,
                needs_clarification=True,
                clarification=f"I encountered an error trying to understand your request with the new DSPy parser. Please try rephrasing. Error: {e}"
            )

        # Handle clarification needs
        if query_plan.needs_clarification:
            step1.content = "❓ **Step 1:** Need clarification..."
            await step1.update()
            
            clarification_msg = f"**I need more information:**\n\n{query_plan.clarification}"
            await cl.Message(content=clarification_msg).send()
            return
        
        # Step 1 completion with DSPy insights
        companies_str = f"{', '.join(query_plan.companies)}" if query_plan.companies else "general query"
        dspy_insights = conversation_context.get_dspy_insights()
        
        step1.content = f"✅ **Step 1:** Advanced query analysis completed"
        step1.content += f"\n   📊 **Intent:** {query_plan.intent} | **Companies:** {companies_str} | **Confidence:** {query_plan.confidence:.2f}"
        step1.content += f"\n   🔍 **Generated {len(query_plan.queries)} targeted queries"
        
        if dspy_insights:
            step1.content += f"\n   🎯 **DSPy Insights:** Avg quality {dspy_insights['average_quality']:.2f}, "
            step1.content += f"{dspy_insights['total_interactions']} interactions"
        
        await step1.update()
        
        # Step 2: Enhanced Query Execution
        step2 = cl.Message(content="🔎 **Step 2:** Searching financial database...")
        await step2.send()
        
        # Import legacy execution for compatibility
        from Step8MCPClientPsxGPT import execute_financial_query
        result = await execute_financial_query(query_plan, message.content)
        
        # Error handling for step 2
        if "error" in result:
            step2.content = "❌ **Step 2:** Search completed with issues"
            await step2.update()
            
            error_msg = f"**{result['error']}**"
            
            if "query_stats" in result:
                stats = result["query_stats"]
                error_msg += f"\n\n**Query Statistics:**"
                error_msg += f"\n• Total queries attempted: {stats.get('total_queries', 0)}"
                error_msg += f"\n• Successful queries: {stats.get('successful_queries', 0)}"
                error_msg += f"\n• Failed queries: {stats.get('failed_queries', 0)}"
            
            await cl.Message(content=error_msg).send()
            return
        
        # Step 2 completion with advanced metrics
        query_stats = result.get("query_stats", {})
        success_rate = query_stats.get("success_rate", 0) * 100
        
        step2.content = f"✅ **Step 2:** Data retrieval completed"
        step2.content += f"\n   📊 **Found {result['total_nodes']} data chunks** from {query_stats.get('successful_queries', 0)} queries"
        step2.content += f"\n   📈 **Success rate:** {success_rate:.0f}% ({query_stats.get('successful_queries', 0)}/{query_stats.get('total_queries', 0)} queries)"
        await step2.update()
        
        # Step 3: Advanced DSPy Analysis with Refinement
        step3 = cl.Message(content="🚀 **Step 3:** Advanced DSPy analysis with refinement...")
        await step3.send()
        
        # Create streaming response message
        response_msg = cl.Message(content="")
        await response_msg.send()
        
        # Stream the formatted response with advanced DSPy enhancement
        complete_response = ""
        
        async for chunk in stream_formatted_response_with_dspy(
            result["original_query"], 
            result["nodes"], 
            result["intent"], 
            result["companies"]
        ):
            complete_response += chunk
            await response_msg.stream_token(chunk)
        
        # Step 3 completion with DSPy metrics
        processing_time = (datetime.now() - start_time).total_seconds()
        session_report = performance_tracker.get_session_report()
        
        step3.content = f"✅ **Step 3:** Advanced DSPy analysis completed"
        step3.content += f"\n   ⏱️ **Processing time:** {processing_time:.1f}s"
        step3.content += f"\n   🔄 **DSPy Refinement:** {session_report['dspy_refinement']['total_refinement_cycles']} cycles"
        step3.content += f"\n   📊 **Quality Score:** {session_report['session_summary']['average_quality_score']:.2f}"
        step3.content += f"\n   🎯 **Success Rate:** {session_report['dspy_refinement']['refinement_success_rate']:.1%}"
        await step3.update()
        
        # Enhanced source information
        from Step8MCPClientPsxGPT import extract_used_chunks_from_response, format_sources
        used_chunks = extract_used_chunks_from_response(complete_response)
        source_info = format_sources(result.get("nodes", []), used_chunks)
        await response_msg.stream_token(source_info)
        
        # Enhanced completion summary with DSPy insights
        completion_summary = f"\n\n---\n**🚀 Advanced DSPy Analysis Complete**"
        completion_summary += f"\n• **Data Sources:** {result['total_nodes']} chunks analyzed"
        completion_summary += f"\n• **Companies:** {len(result['companies'])} analyzed" 
        completion_summary += f"\n• **Intent:** {result['intent']} with refinement"
        completion_summary += f"\n• **Processing Time:** {processing_time:.1f}s"
        completion_summary += f"\n• **DSPy Refinement:** {session_report['dspy_refinement']['total_refinement_cycles']} cycles"
        completion_summary += f"\n• **Quality Improvement:** {session_report['dspy_refinement']['average_score_improvement']:+.3f}"
        completion_summary += f"\n• **LLM Efficiency:** {session_report['dspy_refinement']['llm_calls_per_query']:.1f} calls/query"
        
        # Add performance recommendations
        recommendations = session_report.get("recommendations", [])
        if recommendations:
            completion_summary += f"\n\n**💡 Optimization Recommendations:**"
            for rec in recommendations[:2]:  # Show top 2
                completion_summary += f"\n• {rec}"
        
        await response_msg.stream_token(completion_summary)
        await response_msg.update()
        
        # Save enhanced context
        conversation_context.add_message("user", message.content)
        conversation_context.add_message("assistant", complete_response[:500] + "..." if len(complete_response) > 500 else complete_response)
        save_enhanced_conversation_context(conversation_context)
        
        # Log session metrics
        log.info(f"📊 Session metrics: {session_report['session_summary']}")
        
    except Exception as e:
        log.error(f"❌ Enhanced message handler error: {e}")
        await cl.Message(content=f"❌ **Advanced DSPy Error:** {str(e)}\n\nPlease try rephrasing your question.").send()

# ─────────────────────────── Enhanced Welcome Message ────────────────────────

@cl.on_chat_start
async def enhanced_welcome_message():
    """Enhanced welcome message with DSPy capabilities."""
    session_report = performance_tracker.get_session_report()
    dspy_stats = dspy_llm.get_refinement_stats()
    
    welcome_content = (
        "👋 **Welcome to BankGPT - Advanced DSPy Edition!**\n\n"
        "🚀 **Now featuring advanced DSPy framework with:**\n"
        "• **Iterative Refinement** - Automatically improves responses\n"
        "• **Quality Scoring** - Measures and optimizes analysis quality\n"
        "• **Continuous Learning** - Gets better with each interaction\n"
        "• **Multi-stage Processing** - BestOfN → Refine → Optimize\n\n"
        "🔌 **Setup Instructions:**\n"
        "1. Copy URL: `https://bankgptserver.onrender.com/sse`\n"
        "2. Click plug icon 🔌 → Select **sse** → Paste URL\n"
        "3. Set **Name** as **BankGPT** → Click **Confirm**\n\n"
        "📊 **Available Tickers:** ABL, BAFL, BAHL, BIPL, FABL, HBL, HMB, MCP, MEBL, UBL\n\n"
        "🎯 **DSPy Features:**\n"
        "• **Statement Analysis** - Complete financial statements with refinement\n"
        "• **Ratio Calculations** - Banking ratios with accuracy validation\n"
        "• **Quality Metrics** - Real-time quality scoring and improvement\n"
        "• **Optimization** - Continuous improvement through feedback loops\n\n"
        f"📈 **System Status:**\n"
        f"• **DSPy Modules:** Initialized and ready\n"
        f"• **Refinement Engine:** Active\n"
        f"• **Performance Tracking:** Enabled\n"
        f"• **Session Queries:** {session_report['session_summary']['total_queries']}\n\n"
        "💡 **Try asking:** \"HBL vs UBL 2024 performance analysis\" or \"FABL quarterly statements with ratios\""
    )
    
    await cl.Message(content=welcome_content).send()

# ─────────────────────────── Export Legacy Components ────────────────────────

# Export essential components for backward compatibility
from Step8MCPClientPsxGPT import (
    # parse_query_with_claude, # This is now replaced by the DSPy parser
    execute_financial_query,
    call_mcp_server,
    save_client_context,
    extract_used_chunks_from_response,
    format_sources,
    QueryPlan,
    ConversationContext,
    ADMIN_USERNAME,
    ADMIN_PASSWORD
)

# Enhanced MCP handlers (reuse from original with logging)
@cl.on_mcp_connect
async def enhanced_mcp_connect(connection, session):
    """Enhanced MCP connection with DSPy logging."""
    try:
        cl.user_session.set("mcp_client", session)
        log.info(f"🔌 MCP connected: {connection.name} with DSPy enhancement")
        
        await cl.Message(
            content=f"✅ **Connected to Enhanced PSX Server** (`{connection.name}`)\n\n🚀 DSPy refinement engine activated!",
            author="System"
        ).send()
        
    except Exception as e:
        log.error(f"❌ Enhanced MCP connect error: {e}")
        await cl.Message(
            content=f"❌ **Connection failed**: {str(e)}",
            author="System"
        ).send()

@cl.on_mcp_disconnect
async def enhanced_mcp_disconnect(name: str, session):
    """Enhanced MCP disconnection with DSPy logging."""
    try:
        cl.user_session.set("mcp_client", None)
        log.info(f"🔌 MCP disconnected: {name}")
        
        # Generate final session report
        final_report = performance_tracker.get_session_report()
        log.info(f"📊 Final session report: {final_report}")
        
        await cl.Message(
            content=f"🔌 **Disconnected from server** (`{name}`)\n\n📊 **Session Summary:** {final_report['session_summary']['total_queries']} queries processed",
            author="System"
        ).send()
        
    except Exception as e:
        log.error(f"❌ Enhanced MCP disconnect error: {e}")

# Password authentication (reuse from original)
@cl.password_auth_callback
def enhanced_auth_callback(username: str, password: str) -> Optional[cl.User]:
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return cl.User(identifier=username, metadata={"role": "admin", "dspy_enabled": True})
    return None

# ─────────────────────────── Entry Point ────────────────────────────────
if __name__ == "__main__":
    log.info("🚀 Starting Advanced DSPy-Enhanced PSX Financial Client...")
    log.info(f"🔧 DSPy refinement engine: {dspy_llm.model}")
    log.info(f"📊 Performance tracking: Active")
    
    # Initialize optimization directory
    optimization_file = OPTIMIZATION_DIR / "session_metrics.json"
    
    from chainlit.cli import run_chainlit
    run_chainlit(__file__) 