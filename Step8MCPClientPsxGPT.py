"""
PSX Financial Client - Enhanced Intelligence & Orchestration Layer
Handles natural language parsing with Claude 4 Sonnet and orchestrates MCP server calls.
Enhanced with improved error handling, logging, and user experience.

Flow: User Query → Claude Parsing → Query Execution → Response Synthesis
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

import anthropic
import chainlit as cl
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# ─────────────────────────── Configuration ──────────────────────────────
load_dotenv()

BASE_DIR = Path(__file__).parent.resolve()
TICKERS_PATH = BASE_DIR / "tickers.json"
CONTEXT_DIR = BASE_DIR / "enhanced_client_contexts"
CONTEXT_DIR.mkdir(exist_ok=True)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not ANTHROPIC_API_KEY:
    raise RuntimeError("ANTHROPIC_API_KEY environment variable not set")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable not set")

# Enhanced logging configuration with framework error suppression
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("psx-client-enhanced")

# Suppress known framework-level async errors that don't affect functionality
import warnings
warnings.filterwarnings("ignore", message=".*async generator ignored GeneratorExit.*")
warnings.filterwarnings("ignore", message=".*Attempted to exit cancel scope.*")

# Configure specific loggers to reduce noise from framework issues
logging.getLogger("chainlit.server").setLevel(logging.ERROR)  # Reduce chainlit server noise
logging.getLogger("anyio").setLevel(logging.WARNING)  # Reduce anyio async warnings

# Load local data with error handling
try:
    with open(TICKERS_PATH, encoding="utf-8") as f:
        TICKERS = json.load(f)
    log.info(f"📋 Loaded {len(TICKERS)} company tickers for parsing")
except Exception as e:
    log.error(f"❌ Failed to load tickers: {e}")
    TICKERS = []

# Anthropic client with enhanced configuration
anthropic_client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY, timeout=60.0)

# Google GenAI for streaming responses (uses maximum token limits by default)
from llama_index.llms.google_genai import GoogleGenAI
streaming_llm = GoogleGenAI(
    model="models/gemini-2.5-pro", 
    api_key=GEMINI_API_KEY, 
    temperature=0.4,
    timeout=120.0
)

# Google GenAI streaming LLM initialized

# Import prompts library
from prompts import prompts

# ─────────────────────────── Conversation Context Management ─────────────────
class ConversationContext(BaseModel):
    """Simple conversation context following Claude's stateless API pattern"""
    messages: List[Dict[str, str]] = Field(default_factory=list, description="Conversation history in Claude format")
    
    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        self.messages.append({"role": role, "content": content})
        # Keep only last 10 messages for token efficiency (following industry best practices)
        if len(self.messages) > 10:
            self.messages = self.messages[-10:]
    
    def get_messages_for_claude(self) -> List[Dict[str, str]]:
        """Get conversation history in Claude's required format"""
        return self.messages.copy()
    
    def get_context_summary(self) -> str:
        """Get a brief context summary for follow-up queries"""
        if not self.messages:
            return ""
        
        # Extract companies and intents from recent messages
        recent_content = " ".join([msg["content"] for msg in self.messages[-3:]])
        
        # Simple context extraction (could be enhanced with NLP)
        companies = []
        for ticker_data in TICKERS:
            if ticker_data["Symbol"].upper() in recent_content.upper():
                companies.append(ticker_data["Symbol"])
        
        context = "Previous conversation context:\n"
        if companies:
            context += f"Companies discussed: {', '.join(companies)}\n"
        if self.messages:
            context += f"Recent queries: {len(self.messages)} messages\n"
        
        return context

def get_conversation_context() -> ConversationContext:
    """Get or create conversation context from user session"""
    context_data = cl.user_session.get("conversation_context")
    if context_data:
        try:
            return ConversationContext.model_validate(context_data)
        except Exception:
            pass  # Create new context if validation fails
    
    return ConversationContext()

def save_conversation_context(context: ConversationContext):
    """Save conversation context to user session"""
    cl.user_session.set("conversation_context", context.model_dump())

# ─────────────────────────── Data Models ────────────────────────────────
class QueryPlan(BaseModel):
    companies: List[str] = Field(description="Ticker symbols extracted")
    intent: str = Field(description="Query intent: statement/analysis")
    queries: List[Dict[str, Any]] = Field(description="Structured queries for MCP server")
    confidence: float = Field(description="Parsing confidence 0-1")
    needs_clarification: bool = Field(default=False)
    clarification: Optional[str] = Field(default=None)

# ─────────────────────────── Context & Source Management ─────────────────
def format_sources(nodes: List[Dict], used_chunk_ids: Optional[List[str]] = None) -> str:
    """Enhanced source formatting with filtering for actually used chunks, grouped by file"""
    if not nodes:
        return ""
    
    # Filter nodes based on used chunk IDs if provided
    if used_chunk_ids:
        filtered_nodes = []
        for node in nodes:
            chunk_id = str(node.get("metadata", {}).get("chunk_number", "unknown"))
            if chunk_id in used_chunk_ids:
                filtered_nodes.append(node)
        
        if filtered_nodes:
            nodes = filtered_nodes
            log.info(f"📋 Filtered to {len(filtered_nodes)} actually used chunks out of {len(nodes)} retrieved")
        else:
            log.warning("⚠️ No chunks matched the used chunk IDs, showing all retrieved chunks")
    
    sources = "\n\n## 📚 Source References\n\n"
    
    if used_chunk_ids:
        sources += f"**Showing {len(nodes)} chunks actually used in the analysis** (filtered from original results)\n\n"
    
    # Group nodes by source file
    file_groups = {}
    for node in nodes:
        try:
            metadata = node.get("metadata", {})
            source_file = metadata.get("source_file", "Unknown")
            chunk_number = metadata.get("chunk_number", "Unknown")
            
            if source_file not in file_groups:
                file_groups[source_file] = []
            
            file_groups[source_file].append(chunk_number)
            
        except Exception as e:
            log.warning(f"Error processing node for grouping: {e}")
    
    # Format grouped sources
    for i, (source_file, chunk_numbers) in enumerate(file_groups.items(), 1):
        # Sort chunk numbers numerically
        try:
            chunk_numbers = sorted(chunk_numbers, key=lambda x: int(x) if str(x).isdigit() else 0)
        except:
            pass  # Keep original order if sorting fails
        
        # Format chunk numbers list
        if len(chunk_numbers) == 1:
            chunks_str = f"chunk {chunk_numbers[0]}"
        else:
            chunks_str = f"chunks {', '.join(map(str, chunk_numbers))}"
        
        sources += f"**{i}.** File name: {source_file}; {chunks_str} used\n\n"
    
    return sources

def extract_used_chunks_from_response(response_text: str) -> List[str]:
    """Extract the list of used chunk IDs from the LLM response"""
    try:
        # Look for the "Used Chunks:" section at the end of the response
        import re
        
        # Pattern to match "Used Chunks: [chunk1, chunk2, ...]" or similar variations
        patterns = [
            r"Used Chunks:\s*\[([^\]]+)\]",
            r"Used Chunks:\s*([0-9,\s]+)",
            r"Actually used chunks?:\s*\[([^\]]+)\]",
            r"Referenced chunks?:\s*\[([^\]]+)\]"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                chunk_text = match.group(1)
                # Extract numbers from the matched text
                chunk_numbers = re.findall(r'\d+', chunk_text)
                if chunk_numbers:
                    log.info(f"📝 Extracted {len(chunk_numbers)} used chunk IDs: {chunk_numbers}")
                    return chunk_numbers
        
        log.warning("⚠️ Could not extract used chunk IDs from response")
        return []
        
    except Exception as e:
        log.error(f"❌ Error extracting used chunks: {e}")
        return []

async def save_client_context(query: str, query_plan: QueryPlan, result: Dict) -> str:
    """Enhanced client-side context saving with detailed metadata"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = CONTEXT_DIR / f"client_context_{timestamp}.json"
        
        # Enhanced context with more detailed information
        context = {
            "timestamp": timestamp,
            "original_query": query,
            "query_plan": {
                "companies": query_plan.companies,
                "intent": query_plan.intent,
                "confidence": query_plan.confidence,
                "queries_count": len(query_plan.queries),
                "needs_clarification": query_plan.needs_clarification,
                "sample_query": query_plan.queries[0] if query_plan.queries else None
            },
            "execution_result": {
                "total_nodes": result.get("total_nodes", 0),
                "response_length": len(result.get("response", "")),
                "companies": result.get("companies", []),
                "intent": result.get("intent", ""),
                "query_stats": result.get("query_stats", {}),
                "error": result.get("error", None)
            },
            "sample_nodes": result.get("nodes", [])[:3],
            "client_version": "enhanced"
        }
        
        filename.write_text(json.dumps(context, indent=2, default=str))
        log.info(f"📁 Client context saved: {filename.name}")
        return str(filename)
    except Exception as e:
        log.warning(f"⚠️ Failed to save client context: {e}")
        return ""

# ─────────────────────────── Core Functions ──────────────────────────────

def find_best_ticker_match(query_ticker: str) -> str:
    """Find best ticker match from tickers.json data"""
    query_lower = query_ticker.lower()
    
    # First try exact symbol match
    for ticker_data in TICKERS:
        if ticker_data["Symbol"].lower() == query_lower:
            return ticker_data["Symbol"]
    
    # Then try company name matching
    for ticker_data in TICKERS:
        company_name = ticker_data["Company Name"].lower()
        # Check if query is contained in company name or vice versa
        if query_lower in company_name or any(word in company_name for word in query_lower.split()):
            return ticker_data["Symbol"]
    
    # Return original if no match found
    return query_ticker

async def parse_query_with_claude(user_query: str, conversation_context: Optional[ConversationContext] = None) -> QueryPlan:
    """Use Claude 4 Sonnet to parse user query into structured query plan with conversation context"""
    log.info(f"Parsing query with Claude: {user_query[:100]}...")
    
    # Create ticker context for Claude - only banks
    bank_tickers = [t["Symbol"] for t in TICKERS if "bank" in t["Company Name"].lower()]
    
    # Detect quarterly requests for Q4 calculation logic
    is_quarterly_request = any(q_term in user_query.lower() for q_term in ["quarterly", "quarter", "q1", "q2", "q3", "q4"])
    
    # Build messages array for Claude's stateless API
    messages = []
    
    # Add conversation history if available (Claude's native format)
    if conversation_context:
        context_messages = conversation_context.get_messages_for_claude()
        if context_messages:
            messages.extend(context_messages)
            log.info(f"📝 Added {len(context_messages)} previous messages to conversation context")
    
    # Add current user query
    user_prompt = prompts.get_parsing_user_prompt(user_query, bank_tickers, is_quarterly_request)
    messages.append({"role": "user", "content": user_prompt})

    try:
        response = await anthropic_client.messages.create(
            model="claude-4-sonnet-20250514",
            max_tokens=30000,
            temperature=0.1,
            system=prompts.PARSING_SYSTEM_PROMPT,
            messages=messages,  # Use Claude's native message format
            tools=[{
                "name": "create_query_plan",
                "description": "Create structured query plan for PSX financial data",
                "input_schema": QueryPlan.model_json_schema()
            }],
            tool_choice={"type": "tool", "name": "create_query_plan"}
        )
        
        if response.content[0].type == "tool_use":
            parsed_data = response.content[0].input
            query_plan = QueryPlan.model_validate(parsed_data)
            
            # Enhanced quarterly processing: automatically add annual queries for Q4 calculation
            if is_quarterly_request:
                log.info("🔢 Quarterly request detected - adding annual queries for Q4 calculation")
                
                # Extract unique companies and statement types from quarterly queries
                companies_for_annual = set()
                statement_types_for_annual = set()
                
                for query_spec in query_plan.queries:
                    filters = query_spec.get("metadata_filters", {})
                    if "ticker" in filters:
                        companies_for_annual.add(filters["ticker"])
                    if "statement_type" in filters:
                        statement_types_for_annual.add(filters["statement_type"])
                
                # Add annual queries for Q4 calculation - keep search flexible for year matching
                annual_queries = []
                for company in companies_for_annual:
                    for stmt_type in statement_types_for_annual:
                        annual_query = {
                            "search_query": f"{company} {stmt_type.replace('_', ' ')} annual",
                            "metadata_filters": {
                                "ticker": company,
                                "statement_type": stmt_type,
                                "is_statement": "yes",
                                "filing_type": "annual"
                            }
                        }
                        annual_queries.append(annual_query)
                
                # Add annual queries to the plan
                query_plan.queries.extend(annual_queries)
                log.info(f"🎯 Enhanced quarterly plan: {len(query_plan.queries)} total queries (including annual for Q4)")
            
            # Validate and fix empty search queries - keep metadata filters minimal 
            valid_queries = []
            for query_spec in query_plan.queries:
                search_query = query_spec.get("search_query", "").strip()
                metadata_filters = query_spec.get("metadata_filters", {})
                
                # Ensure quarterly requests have proper filing_type
                if is_quarterly_request and "filing_type" not in metadata_filters:
                    # Check if this is a quarterly-specific query (not annual)
                    if "annual" not in search_query.lower():
                        metadata_filters["filing_type"] = "quarterly"
                        log.info("🔧 Added filing_type=quarterly for quarterly request")
                
                # Validate and correct ticker symbols using tickers.json
                if "ticker" in metadata_filters:
                    original_ticker = metadata_filters["ticker"]
                    
                    # Find best match from actual tickers.json data
                    corrected_ticker = find_best_ticker_match(original_ticker)
                    if corrected_ticker != original_ticker:
                        metadata_filters["ticker"] = corrected_ticker
                        log.info(f"Corrected ticker using tickers.json: {original_ticker} → {corrected_ticker}")
                
                # Ensure critical metadata filters are present based on intent
                if query_plan.intent == "statement" or "statement" in user_query.lower():
                    metadata_filters["is_statement"] = "yes"
                    # Don't set is_note for statement requests
                    log.info("Added is_statement=yes for statement request")
                
                # Enhanced statement detection for common phrases
                statement_keywords = ["balance sheet", "profit and loss", "cash flow", "income statement", "p&l", "p & l"]
                if any(keyword in user_query.lower() for keyword in statement_keywords):
                    metadata_filters["is_statement"] = "yes"
                    # Don't set is_note for statement keywords
                    log.info(f"Added is_statement=yes filter for statement keywords in query")
                
                # Handle explicit note requests - but don't override statement requests
                if "note" in user_query.lower():
                    # If this is ONLY a note request (no statement keywords), make it a note query
                    if not any(keyword in user_query.lower() for keyword in statement_keywords):
                        metadata_filters["is_note"] = "yes"
                        metadata_filters["is_statement"] = "no"
                        log.info("Added is_note=yes filter for note-only request")
                    # If it's a combined statement + notes request, this query stays as statement
                    # (We'll add note queries separately later)
                
                if not search_query:
                    # Create a fallback search query using available information
                    ticker = metadata_filters.get("ticker", "")
                    statement_type = metadata_filters.get("statement_type", "").replace("_", " ")
                    
                    if ticker or statement_type:
                        fallback_query = f"{ticker} {statement_type} {user_query}".strip()
                        query_spec["search_query"] = fallback_query
                        log.info(f"Generated fallback search query: '{fallback_query}'")
                    else:
                        # If we can't create a meaningful query, use the original user query
                        query_spec["search_query"] = user_query
                        log.info(f"Using original query as fallback: '{user_query}'")
                
                # CRITICAL VALIDATION: Ensure mutual exclusivity between is_statement and is_note
                if metadata_filters.get("is_statement") == "yes" and metadata_filters.get("is_note") == "yes":
                    log.error(f"❌ MUTUAL EXCLUSIVITY VIOLATION: Both is_statement and is_note are 'yes' - fixing...")
                    
                    # Determine which one should be kept based on query content
                    if "note" in user_query.lower() and not any(keyword in user_query.lower() for keyword in ["balance sheet", "profit and loss", "cash flow", "income statement", "p&l", "p & l"]):
                        # Pure note request
                        metadata_filters["is_statement"] = "no"
                        metadata_filters["is_note"] = "yes"
                        log.info("Fixed to note-only query: is_statement=no, is_note=yes")
                    else:
                        # Statement request (possibly with notes to be handled separately)
                        metadata_filters["is_statement"] = "yes"
                        metadata_filters["is_note"] = "no"
                        log.info("Fixed to statement query: is_statement=yes, is_note=no")
                
                # CRITICAL VALIDATION: Ensure note_link is only present when is_note="yes" 
                if metadata_filters.get("is_statement") == "yes" and "note_link" in metadata_filters:
                    log.warning(f"⚠️ Removing note_link from statement query - note_link should only exist for notes")
                    del metadata_filters["note_link"]
                
                # Update the query spec with validated metadata filters
                query_spec["metadata_filters"] = metadata_filters
                valid_queries.append(query_spec)
            
            # Update the query plan with validated queries
            query_plan.queries = valid_queries
            
            # Handle combined statement + notes requests
            # If user asked for notes AND we have statement queries, add corresponding note queries
            user_query_lower = user_query.lower()
            if "note" in user_query_lower and any("is_statement" in q.get("metadata_filters", {}) and 
                                                 q["metadata_filters"]["is_statement"] == "yes" 
                                                 for q in valid_queries):
                
                log.info("🗒️ Combined statement + notes request detected - adding note queries")
                statement_keywords = ["balance sheet", "profit and loss", "cash flow", "income statement", "p&l", "p & l"]
                
                # Find statement queries and create corresponding note queries
                additional_note_queries = []
                for query_spec in valid_queries:
                    metadata_filters = query_spec.get("metadata_filters", {})
                    if metadata_filters.get("is_statement") == "yes":
                        # Create corresponding note query
                        note_query = {
                            "search_query": query_spec["search_query"].replace("account", "notes").replace("statement", "notes"),
                            "metadata_filters": {
                                **{k: v for k, v in metadata_filters.items() 
                                   if k not in ["is_statement", "is_note", "statement_type"]},
                                "is_statement": "no",
                                "is_note": "yes"
                            }
                        }
                        
                        # Set note_link based on statement_type
                        if "statement_type" in metadata_filters:
                            note_query["metadata_filters"]["note_link"] = metadata_filters["statement_type"]
                        else:
                            # Try to infer from search query
                            search_lower = query_spec["search_query"].lower()
                            if any(kw in search_lower for kw in ["profit and loss", "p&l", "p & l"]):
                                note_query["metadata_filters"]["note_link"] = "profit_and_loss"
                            elif "balance sheet" in search_lower:
                                note_query["metadata_filters"]["note_link"] = "balance_sheet"
                            elif "cash flow" in search_lower:
                                note_query["metadata_filters"]["note_link"] = "cash_flow"
                        
                        additional_note_queries.append(note_query)
                        log.info(f"📝 Added note query for {metadata_filters.get('ticker', 'company')}: note_link={note_query['metadata_filters'].get('note_link')}")
                
                # Add note queries to the plan
                query_plan.queries.extend(additional_note_queries)
                log.info(f"🎯 Enhanced plan: {len(query_plan.queries)} total queries ({len(valid_queries)} statements + {len(additional_note_queries)} notes)")
            
            log.info(f"Claude parsing successful - Companies: {query_plan.companies}, Intent: {query_plan.intent}, Confidence: {query_plan.confidence}, Queries: {len(query_plan.queries)}")
            return query_plan
        else:
            raise ValueError("Claude didn't use the expected tool")
            
    except Exception as e:
        log.error(f"Claude parsing failed: {e}")
        # Return a clarification request instead of failing
        return QueryPlan(
            companies=[],
            intent="analysis",
            queries=[],
            confidence=0.0,
            needs_clarification=True,
            clarification=f"I couldn't understand your query. Please specify the company name, time period, and statement type. Example: 'HBL 2024 annual balance sheet'"
        )

async def call_mcp_server(tool: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced MCP server communication with improved error handling and async cleanup"""
    mcp_session = cl.user_session.get("mcp_client")
    if not mcp_session:
        log.error("❌ MCP client session not found")
        raise Exception("MCP server not connected")
    
    try:
        log.info(f"🔄 Calling MCP tool: {tool}")
        log.debug(f"   Arguments: {json.dumps(args, indent=2)}")
        
        # Enhanced timeout handling with proper async cleanup
        async def _make_call():
            return await mcp_session.call_tool(tool, args)
        
        # Use asyncio.wait_for with shield to handle cancellation properly
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
            return {
                "error": f"No response from {tool}",
                "error_type": "empty_response"
            }
        
        content = result.content[0]
        
        # Get text content with error handling
        text_content = ""
        try:
            if hasattr(content, 'text') and content.text:
                text_content = content.text.strip()
            else:
                text_content = str(content).strip()
        except Exception as content_error:
            log.error(f"❌ Error extracting content from {tool}: {content_error}")
            return {
                "error": f"Failed to extract content from {tool}",
                "error_type": "content_extraction_error"
            }
            
        if not text_content or text_content == "None":
            log.error(f"❌ Empty text content from {tool}")
            return {
                "error": f"Empty response content from {tool}",
                "error_type": "empty_content"
            }
        
        # Parse JSON with enhanced error handling
        try:
            parsed_response = json.loads(text_content)
            
            # Enhanced error detection and logging
            if isinstance(parsed_response, dict):
                if "error" in parsed_response:
                    error_msg = parsed_response.get("error", "Unknown error")
                    error_type = parsed_response.get("error_type", "server_error")
                    log.warning(f"⚠️ Server returned {error_type}: {error_msg}")
                    return parsed_response
                else:
                    # Log successful response details
                    if "nodes" in parsed_response:
                        node_count = len(parsed_response.get("nodes", []))
                        log.info(f"✅ {tool} returned {node_count} nodes successfully")
                    else:
                        log.info(f"✅ {tool} completed successfully")
            
            return parsed_response
            
        except json.JSONDecodeError as e:
            log.error(f"❌ JSON decode error for {tool}: {e}")
            log.debug(f"   Raw content: '{text_content[:200]}...'")
            return {
                "error": f"Could not parse response from {tool}: {str(e)}", 
                "error_type": "json_decode_error",
                "raw_content": text_content[:500]  # Limit size for logging
            }
        
    except Exception as e:
        if isinstance(e, asyncio.CancelledError):
            raise  # Re-raise cancellation
        log.error(f"❌ MCP call failed for {tool}: {str(e)}")
        return {
            "error": f"MCP call failed for {tool}: {str(e)}",
            "error_type": "connection_error"
        }

async def execute_financial_query(query_plan: QueryPlan, original_query: str) -> Dict[str, Any]:
    """Enhanced query execution with query refinement and improved error handling"""
    log.info(f"🎯 Executing {len(query_plan.queries)} queries for {query_plan.companies}")
    
    all_nodes = []
    successful_queries = 0
    failed_queries = 0
    query_attempts = []
    
    # Execute all queries in the plan with refinement logic
    for i, query_spec in enumerate(query_plan.queries):
        query_successful = False
        attempt_count = 0
        max_attempts = 3
        
        # Try multiple search strategies for each query
        while not query_successful and attempt_count < max_attempts:
            try:
                attempt_count += 1
                current_search_query = query_spec.get("search_query", "").strip()
                metadata_filters = query_spec.get("metadata_filters", {})
                
                # Skip empty queries
                if not current_search_query and not metadata_filters:
                    log.warning(f"⚠️ Skipping empty query {i+1}")
                    failed_queries += 1
                    break
                
                # Query refinement strategies for subsequent attempts
                if attempt_count > 1:
                    company_ticker = metadata_filters.get("ticker", "")
                    statement_type = metadata_filters.get("statement_type", "")
                    
                    if attempt_count == 2:
                        # Attempt 2: Simplify search query, focus on company and statement type
                        if company_ticker and statement_type:
                            current_search_query = f"{company_ticker} {statement_type.replace('_', ' ')}"
                    elif attempt_count == 3:
                        # Attempt 3: Use broader search terms
                        if company_ticker:
                            current_search_query = f"{company_ticker} financial statement"
                            # Remove specific statement type filter to broaden search
                            if "statement_type" in metadata_filters:
                                metadata_filters = {k: v for k, v in metadata_filters.items() if k != "statement_type"}
                
                # If search_query is empty but we have metadata filters, use original query as fallback
                if not current_search_query and metadata_filters:
                    current_search_query = original_query
                
                result = await call_mcp_server("psx_search_financial_data", {
                    "search_query": current_search_query,
                    "metadata_filters": metadata_filters,
                    "top_k": query_spec.get("top_k", 10)
                })
                
                # Error handling for server responses
                if isinstance(result, dict) and "error" in result:
                    error_msg = result.get("error", "Unknown error")
                    error_type = result.get("error_type", "unknown")
                    
                    # Record the attempt
                    query_attempts.append({
                        "query_index": i+1,
                        "attempt": attempt_count,
                        "search_query": current_search_query,
                        "filters": metadata_filters,
                        "result": "error",
                        "error": error_msg
                    })
                    continue
                
                nodes = result.get("nodes", [])
                
                # Check if we got meaningful results
                if nodes:
                    # Check relevance scores - if all scores are very low, consider it a failed attempt
                    relevant_nodes = [n for n in nodes if n.get("score", 0) > 0.5]
                    if relevant_nodes or attempt_count == max_attempts:  # Accept any results on final attempt
                        all_nodes.extend(nodes)
                        successful_queries += 1
                        query_successful = True
                        
                        # Record successful attempt
                        query_attempts.append({
                            "query_index": i+1,
                            "attempt": attempt_count,
                            "search_query": current_search_query,
                            "filters": metadata_filters,
                            "result": "success",
                            "nodes_count": len(nodes),
                            "relevant_nodes": len(relevant_nodes)
                        })
                    else:
                        query_attempts.append({
                            "query_index": i+1,
                            "attempt": attempt_count,
                            "search_query": current_search_query,
                            "filters": metadata_filters,
                            "result": "low_relevance",
                            "nodes_count": len(nodes),
                            "relevant_nodes": len(relevant_nodes)
                        })
                        continue
                else:
                    query_attempts.append({
                        "query_index": i+1,
                        "attempt": attempt_count,
                        "search_query": current_search_query,
                        "filters": metadata_filters,
                        "result": "no_results"
                    })
                    continue
                
            except Exception as e:
                log.error(f"❌ Query {i+1} attempt {attempt_count} failed: {e}")
                query_attempts.append({
                    "query_index": i+1,
                    "attempt": attempt_count,
                    "search_query": current_search_query if 'current_search_query' in locals() else "unknown",
                    "filters": metadata_filters if 'metadata_filters' in locals() else {},
                    "result": "exception",
                    "error": str(e)
                })
                continue
        
        if not query_successful:
            failed_queries += 1
    
    # Result summary
    total_queries = len(query_plan.queries)
    log.info(f"📊 Query execution: {successful_queries}/{total_queries} successful")
    
    if not all_nodes:
        error_msg = "No financial data found for your query"
        if failed_queries == total_queries:
            error_msg += f" - all {total_queries} queries failed after multiple attempts"
        elif failed_queries > 0:
            error_msg += f" - {failed_queries}/{total_queries} queries failed"
        
        return {
            "error": error_msg, 
            "nodes": [],
            "query_stats": {
                "total_queries": total_queries,
                "successful_queries": successful_queries,
                "failed_queries": failed_queries,
                "total_attempts": len(query_attempts),
                "query_attempts": query_attempts
            }
        }
    
    # Return result with statistics
    result_data = {
        "nodes": all_nodes,
        "intent": query_plan.intent,
        "companies": query_plan.companies,
        "total_nodes": len(all_nodes),
        "original_query": original_query,
        "query_stats": {
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "failed_queries": failed_queries,
            "success_rate": successful_queries / total_queries if total_queries > 0 else 0,
            "total_attempts": len(query_attempts),
            "query_attempts": query_attempts
        }
    }
    
    log.info(f"🎉 Found {len(all_nodes)} total nodes from {successful_queries} queries")
    return result_data

async def stream_formatted_response(query: str, nodes: List[Dict], intent: str, companies: List[str]):
    """Stream formatted response using simplified prompts library"""
    if not nodes:
        yield "No relevant financial data found for your query."
        return
    
    # Analyze the nodes to detect multi-company scenario
    companies_set = set(companies)
    periods = set()
    has_annual_data = False
    has_quarterly_data = False
    
    for node in nodes:
        metadata = node.get("metadata", {})
        if period := metadata.get("filing_period"):
            # Handle filing_period which can be a list or string
            if isinstance(period, list):
                periods.update(period)
            else:
                periods.add(str(period))
        
        # Check filing types
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
    
    log.info(f"Response analysis: {len(companies_set)} companies, quarterly: {is_quarterly_request}, Q4_calc: {needs_q4_calculation}")
    
    # Get appropriate prompt using the simplified prompts library
    prompt = prompts.get_prompt_for_intent(
        intent=intent,
        query=query,
        companies=companies,
        is_multi_company=is_multi_company,
        is_quarterly_comparison=is_quarterly_data,
        needs_q4_calculation=needs_q4_calculation
    )
    
    log.info(f"🎨 Using {intent} prompt for {len(companies_set)} companies")
    
    # Prepare context from nodes with chunk identification
    context_str = ""
    for i, node in enumerate(nodes):
        chunk_id = node.get("metadata", {}).get("chunk_number", f"chunk_{i+1}")
        context_str += f"\n\n--- Chunk #{chunk_id} ---\n{node.get('text', '')}"
    
    log.info(f"📊 Context prepared: {len(context_str)} characters from {len(nodes)} nodes")
    
    # Replace the [chunks] placeholder with actual context
    full_prompt = prompt.replace("[chunks]", context_str)
    
    # Stream response using LLM directly
    try:
        stream = await streaming_llm.astream_complete(full_prompt)
        
        async for chunk in stream:
            if chunk.delta:
                yield chunk.delta
        
    except Exception as e:
        log.error(f"Streaming error: {e}")
        # Fallback to regular completion
        response = await streaming_llm.acomplete(full_prompt)
        yield str(response)

# ─────────────────────────── Chainlit UI ────────────────────────────────
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

@cl.password_auth_callback
def auth_callback(username: str, password: str) -> Optional[cl.User]:
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return cl.User(identifier=username, metadata={"role": "admin"})
    return None

@cl.on_chat_start
async def welcome_message():
    await cl.Message(
        content=(
            "👋 **Welcome to BankGPT!**\n\n"
            "To get started, first copy this URL: `https://bankgptserver.onrender.com/sse`\n\n"
            "1. Click the plug icon 🔌 in the chatbox (MCP Servers)\n"
            "2. Under **Type*** click the dropdown and select **sse**\n"
            "3. Paste the URL above and set **Name** as **BankGPT**\n"
            "4. Click **Confirm** to connect\n\n"
            "5. Tickers included: ABL, BAFL, BAHL, BIPL, FABL, HBL, HMB, MCP, MEBL and UBL. \n\n"
            "6. For best results, always specify ticker and time period (e.g. 2022, Q1-2024, last 6 quarters)\n\n"
        )
    ).send()

@cl.on_message
async def on_message(message: cl.Message):
    """Enhanced message handler with improved logging and error handling"""
    try:
        log.info(f"📥 Processing user query: '{message.content[:100]}...'")
        start_time = datetime.now()
        
        # Load conversation context
        conversation_context = get_conversation_context()
        
        # Step 1: Parse query with Claude
        step1 = cl.Message(content="🧠 **Step 1:** Analyzing your query...")
        await step1.send()
        
        query_plan = await parse_query_with_claude(message.content, conversation_context)
        
        # Handle clarification needs
        if query_plan.needs_clarification:
            step1.content = "❓ **Step 1:** Need clarification..."
            await step1.update()
            
            clarification_msg = f"**I need more information:**\n\n{query_plan.clarification}"
            await cl.Message(content=clarification_msg).send()
            return
        
        # Step 1 completion message
        companies_str = f"{', '.join(query_plan.companies)}" if query_plan.companies else "general query"
        step1.content = f"✅ **Step 1:** Query parsed successfully"
        step1.content += f"\n   📊 **Intent:** {query_plan.intent} | **Companies:** {companies_str} | **Confidence:** {query_plan.confidence:.2f}"
        step1.content += f"\n   🔍 **Generated {len(query_plan.queries)} targeted queries**"
        await step1.update()
        
        # Step 2: Execute query plan
        step2 = cl.Message(content="🔎 **Step 2:** Searching financial database...")
        await step2.send()
        
        result = await execute_financial_query(query_plan, message.content)
        
        # Error handling for step 2
        if "error" in result:
            step2.content = "❌ **Step 2:** Search completed with issues"
            await step2.update()
            
            error_msg = f"**{result['error']}**"
            
            # Add query statistics if available
            if "query_stats" in result:
                stats = result["query_stats"]
                error_msg += f"\n\n**Query Statistics:**"
                error_msg += f"\n• Total queries attempted: {stats.get('total_queries', 0)}"
                error_msg += f"\n• Successful queries: {stats.get('successful_queries', 0)}"
                error_msg += f"\n• Failed queries: {stats.get('failed_queries', 0)}"
            
            error_msg += f"\n\n**Suggestions:**\n"
            error_msg += f"• Try being more specific about company, time period, and statement type\n"
            error_msg += f"• Verify company ticker symbols (e.g., HBL, MCB, UBL)\n"
            error_msg += f"• Check if the requested period exists in our database"
            
            await cl.Message(content=error_msg).send()
            return
        
        # Step 2 completion message
        query_stats = result.get("query_stats", {})
        success_rate = query_stats.get("success_rate", 0) * 100
        
        step2.content = f"✅ **Step 2:** Data retrieval completed"
        step2.content += f"\n   📊 **Found {result['total_nodes']} data chunks** from {query_stats.get('successful_queries', 0)} queries"
        step2.content += f"\n   📈 **Success rate:** {success_rate:.0f}% ({query_stats.get('successful_queries', 0)}/{query_stats.get('total_queries', 0)} queries)"
        await step2.update()
        
        # Step 3: Stream the analysis
        step3 = cl.Message(content="📊 **Step 3:** Generating financial analysis...")
        await step3.send()
        
        # Create streaming response message
        response_msg = cl.Message(content="")
        await response_msg.send()
        
        # Stream the formatted response (simple and reliable)
        complete_response = ""
        
        async for chunk in stream_formatted_response(
            result["original_query"], 
            result["nodes"], 
            result["intent"], 
            result["companies"]
        ):
            complete_response += chunk
            await response_msg.stream_token(chunk)
        
        # Step 3 completion
        processing_time = (datetime.now() - start_time).total_seconds()
        step3.content = f"✅ **Step 3:** Analysis generated successfully"
        step3.content += f"\n   ⏱️ **Total processing time:** {processing_time:.1f}s"
        await step3.update()
        
        # Add source info and completion summary
        used_chunks = extract_used_chunks_from_response(complete_response)
        source_info = format_sources(result.get("nodes", []), used_chunks)
        await response_msg.stream_token(source_info)
        
        # Save context for debugging
        context_file = await save_client_context(message.content, query_plan, {
            **result,
            "response": complete_response
        })
        
        completion_summary = f"\n\n---\n**📈 Analysis Complete**"
        completion_summary += f"\n• **Data Sources:** {result['total_nodes']} chunks"
        completion_summary += f"\n• **Companies:** {len(result['companies'])} analyzed" 
        completion_summary += f"\n• **Intent:** {result['intent']}"
        completion_summary += f"\n• **Processing Time:** {processing_time:.1f}s"
        completion_summary += f"\n• **Query Success Rate:** {success_rate:.0f}%"
        
        if context_file:
            completion_summary += f"\n• **Debug Context:** `{Path(context_file).name}`"
        
        await response_msg.stream_token(completion_summary)
        await response_msg.update()
        
        # Save conversation context for future messages
        conversation_context.add_message("user", message.content)
        conversation_context.add_message("assistant", complete_response[:500] + "..." if len(complete_response) > 500 else complete_response)
        save_conversation_context(conversation_context)
        
    except Exception as e:
        log.error(f"❌ Error processing message: {e}")
        await cl.Message(content=f"❌ **Unexpected Error:** {str(e)}\n\nPlease try rephrasing your question or check server connectivity.").send()

@cl.on_mcp_connect
async def on_mcp_connect(connection, session):
    """Enhanced MCP connection handler with framework error resilience"""
    try:
        log.info(f"🔌 MCP server connecting: {connection.name}")
        
        # Check if we already have a connection to prevent duplicates
        existing_session = cl.user_session.get("mcp_client")
        if existing_session:
            log.warning(f"⚠️ MCP session already exists, replacing with new connection: {connection.name}")
        
        # Store session with proper error handling
        cl.user_session.set("mcp_client", session)
        cl.user_session.set("mcp_connection_name", connection.name)
        cl.user_session.set("mcp_connection_time", datetime.now().isoformat())
        
        # Test connection health with enhanced error handling
        try:
            # Simple health check to verify connection
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")  # Suppress framework warnings during health check
                await asyncio.wait_for(session.list_tools(), timeout=5.0)
            log.info(f"✅ MCP session established and verified for: {connection.name}")
        except asyncio.TimeoutError:
            log.warning("⚠️ MCP connection timeout during health check (connection may still work)")
        except Exception as health_error:
            log.warning(f"⚠️ MCP health check failed (connection may still work): {health_error}")
        
        await cl.Message(
            content=f"✅ **Connected to PSX Financial Server** (`{connection.name}`)\n\n🎯 Ready for enhanced financial analysis!",
            author="System"
        ).send()
        
    except Exception as e:
        log.error(f"❌ Error in MCP connect handler: {e}")
        # Clear any partial session data
        cl.user_session.set("mcp_client", None)
        cl.user_session.set("mcp_connection_name", None)
        cl.user_session.set("mcp_connection_time", None)
        
        await cl.Message(
            content=f"❌ **Failed to connect to MCP server**: {str(e)}\n\nPlease check server status and try again.",
            author="System"
        ).send()

@cl.on_mcp_disconnect
async def on_mcp_disconnect(name: str, session):
    """Enhanced MCP disconnection handler with framework error resilience"""
    try:
        log.warning(f"🔌 MCP server disconnecting: {name}")
        
        # Clean up session data
        stored_name = cl.user_session.get("mcp_connection_name")
        if stored_name == name:
            cl.user_session.set("mcp_client", None)
            cl.user_session.set("mcp_connection_name", None)
            cl.user_session.set("mcp_connection_time", None)
            log.info(f"✅ Cleaned up session data for: {name}")
        else:
            log.warning(f"⚠️ Disconnect event for unknown connection: {name} (stored: {stored_name})")
        
        # Attempt graceful cleanup with framework error suppression
        try:
            if session and hasattr(session, 'close'):
                # Suppress framework warnings during cleanup
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    await asyncio.wait_for(session.close(), timeout=2.0)
                log.info(f"✅ Session closed gracefully for: {name}")
        except (asyncio.TimeoutError, AttributeError):
            # Session cleanup timeout or no close method - this is expected
            log.debug(f"Session cleanup timeout/unavailable for: {name} (normal)")
        except Exception as cleanup_error:
            # Log but don't fail on cleanup errors - suppress framework noise
            log.debug(f"Session cleanup completed with framework noise for {name} (non-critical)")
        
        await cl.Message(
            content=f"🔌 **Disconnected from server** (`{name}`)\n\n⚠️ Please restart the server to continue analysis.",
            author="System"
        ).send()
        
    except Exception as e:
        log.error(f"❌ Error in MCP disconnect handler for {name}: {e}")
        # Ensure session is cleared even if cleanup fails
        cl.user_session.set("mcp_client", None)
        cl.user_session.set("mcp_connection_name", None)
        cl.user_session.set("mcp_connection_time", None)

# ─────────────────────────── Entry Point ────────────────────────────────
if __name__ == "__main__":
    log.info("Starting PSX Financial Client...")
    from chainlit.cli import run_chainlit
    run_chainlit(__file__) 