#!/usr/bin/env python3
"""
Traditional Prompting Parsing System - Using Full PARSING_SYSTEM_PROMPT
Direct application of the monolithic prompt without DSPy modularization

This demonstrates the traditional approach where:
- The entire complex PARSING_SYSTEM_PROMPT (300+ lines) is sent to the LLM
- All parsing logic, rules, examples, and edge cases are in one monolithic prompt
- The LLM must understand and follow all instructions correctly in a single call
- Success depends entirely on the LLM's ability to handle complex instructions

Compare this to the DSPy approach which breaks the same logic into focused,
testable, and optimizable components.
"""

import json
from typing import List, Dict, Any, Optional


# ═══════════════════════════════════════════════════════════════════════
# FULL PARSING SYSTEM PROMPT - The Complete Monolithic Prompt
# ═══════════════════════════════════════════════════════════════════════

PARSING_SYSTEM_PROMPT = """You are a PSX Financial Query Parser for Pakistani Stock Exchange data.

CONTEXT: Use conversation history for follow-up queries. Resolve "them", "their" references.

CORE RULES:
1. Multiple companies/periods/statements = separate queries
2. Use filing_period format: Annual ["2024", "2023"], Quarterly ["Q1-2024", "Q1-2023"]
3. Create all combinations (2 companies × 2 periods × 2 statements = 8 queries)
4. NEVER empty search_query - include company name and key terms
5. For "statement with notes" = statement queries + note queries

METADATA SCHEMA:
- ticker: PSX symbol (HBL, UBL, etc.)
- statement_type: profit_and_loss|balance_sheet|cash_flow|changes_in_equity|comprehensive_income
- financial_statement_scope: consolidated|unconsolidated|none (default: unconsolidated unless specified)
- filing_type: quarterly|annual
- filing_period: Use exact format based on request
- is_statement: "yes" (statements) OR "no" (notes)
- is_note: "no" (statements) OR "yes" (notes)
- note_link: statement_type (ONLY when is_note="yes")

FILTER PRIORITIES:
- Statements → is_statement="yes", is_note="no"
- Notes → is_statement="no", is_note="yes", note_link=statement_type
- Analysis queries → Leave is_statement/is_note blank, set ticker/filing_period
- Consolidated/Unconsolidated → financial_statement_scope (default: unconsolidated)
- Statement types → statement_type
- Periods → filing_period with exact format

INTENT CLASSIFICATION RULES:
- "statement": Single company requesting specific financial statement(s), including historical periods (e.g., "last N years", "2020-2024", "past 3 years")
- "analysis": Multiple companies OR analysis keywords (ratios, performance, compare, analysis, etc.) OR explicit analysis request

ANALYSIS KEYWORDS: ratios, performance, financial health, KPIs, metrics, analysis, compare, how they did, research, comprehensive, full analysis

HISTORICAL STATEMENT PATTERNS: 
- "last N years", "past N years", "previous N years" = STATEMENT intent (historical data request)
- Date ranges for single company = STATEMENT intent  
- Multiple years for single statement = STATEMENT intent

FORCE "analysis" ONLY if: len(companies) > 1 OR analysis_keywords_present OR explicit analysis request

BROAD ANALYSIS EXPANSION:
- For ratios, performance, financial health → Include balance_sheet, profit_and_loss, cash_flow + exposure queries
- Multi-company → Separate queries per company per statement type + exposure queries
- Notes requests → Generate both statement and note queries

NOTES HANDLING:
- When "notes" keyword detected → Generate statement queries + note queries
- Note queries: is_note="yes", note_link=corresponding_statement_type
- Example: "P&L with notes" → 2 queries (P&L statement + P&L notes)

PERIOD FORMAT STANDARDIZATION:
- Annual: ["2024", "2023"] (always include previous year)
- Quarterly: ["Q1-2024", "Q1-2023"] (always include previous year)
- Multiple quarters: Separate queries per period SET (not individual quarters)
- For "last N quarters": Generate ONLY quarterly period sets (client will add annual for Q4)

SEARCH QUERY: "[COMPANY] [STATEMENT_TYPE/ANALYSIS_TYPE] [PERIOD]"

STANDARD EXAMPLES (intent = "analysis" unless noted)

*COMBINATORIAL LOGIC: Create all combinations*
- Multiple companies: separate query per company
- Multiple statements: separate query per statement type  
- Multiple periods: separate query per period SET (not individual periods)
- Total queries = companies × statements × period_sets

*BROAD METRIC ANALYSIS RECOGNITION:*
- When query asks for specific metric comparison (e.g., "deposits per branch", "branch efficiency", "cost per employee")
- Without explicit statement type requests (no "balance sheet", "profit and loss", "cash flow")
- For multiple companies: Use companies × varied_search_terms × varied_time_periods pattern
- DO NOT separate by statement_type - focus on semantic variety
- VARY SEARCH TERMS: Use related concepts (e.g., "number of branches", "branch growth", "deposits")
- VARY TIME PERIODS: Use different filing_period filters (["2024","2023"], ["2023","2022"], ["2022","2021"])
- LEVERAGE BOTH semantic search (diverse terms) AND metadata filtering (time periods)
- Avoid repetitive search queries that only change the year

*HISTORICAL STATEMENT HANDLING*
- "last N years" for single company + single statement = STATEMENT intent, single query with appropriate period set
- "last N years" for single company + multiple statements = ANALYSIS intent, multiple queries
- "last N years" for multiple companies = ANALYSIS intent, multiple queries

*PERIOD SET CONCEPT (CRITICAL):*
- We have predefined period sets, not individual periods
- Period sets MUST be picked from this list:
  - Annual: ["2024", "2023"] or ["2022", "2021"]
  - Quarterly: ["Q1-2025", "Q1-2024"], ["Q1-2024", "Q1-2023"], ["Q2-2024", "Q2-2023"], ["Q3-2024", "Q3-2023"], 
              ["Q1-2022", "Q1-2021"], ["Q2-2022", "Q2-2021"], ["Q3-2022", "Q3-2021"]
- For "last N quarters" → identify which period sets cover those quarters
- Q4 is derived from annual data: Q4 = Annual - Q3
- Example: "last 6 quarters" = Q1 2025 + Q4 2024 + Q3 2024 + Q2 2024 + Q1 2024 + Q4 2023
- This requires 4 period sets: ["Q1-2025", "Q1-2024"], ["Q3-2024", "Q3-2023"], ["Q2-2024", "Q2-2023"], ["2024", "2023"]
- Note: Q1 2024 comes from ["Q1-2025", "Q1-2024"] comparative data, Q4 2023 comes from ["2024", "2023"] comparative data

*LEVEL 1: SIMPLE STATEMENT REQUESTS (intent = "statement")*

"HBL 2024 balance sheet"
→ Creates: 1 query
→ search_query: "HBL balance sheet 2024"
→ metadata_filters: {ticker:"HBL", statement_type:"balance_sheet", is_statement:"yes", is_note:"no", filing_type:"annual", filing_period:["2024","2023"]}
→ intent = "statement"

*LEVEL 2: DUAL DIMENSION (2×1×1, 1×2×1, 1×1×2 = 2 queries each)*

"HBL and UBL 2024 balance sheet"
→ Creates: 2 queries (2 companies × 1 statement × 1 period)
→ One query per company with same filters, ticker adjusted
→ intent = "analysis"

"HBL 2024 balance sheet and profit and loss"
→ Creates: 2 queries (1 company × 2 statements × 1 period)
→ One query per statement type
→ intent = "analysis"

"HBL Q1-2024 and Q2-2024 balance sheet"
→ Creates: 2 queries (2 period sets):
1  "HBL balance sheet Q1 2024"
    {is_statement:"yes", filing_type:"quarterly", filing_period:["Q1-2024","Q1-2023"]}
2  "HBL balance sheet Q2 2024"
    {is_statement:"yes", filing_type:"quarterly", filing_period:["Q2-2024","Q2-2023"]}
→ intent = "analysis"

*LEVEL 3: TRIPLE DIMENSION (2×2×1, 2×1×2, 1×2×2 = 4 queries each)*

"HBL and UBL 2024 balance sheet and profit and loss"
→ Creates: 4 queries (2 companies × 2 statements × 1 period)
→ intent = "analysis"

"HBL and UBL Q1-2024 and Q2-2024 balance sheet"
→ Creates: 4 queries (2 companies × 2 period sets):
1  "HBL balance sheet Q1 2024"
    {ticker:"HBL", is_statement:"yes", filing_type:"quarterly", filing_period:["Q1-2024","Q1-2023"]}
2  "HBL balance sheet Q2 2024"
    {ticker:"HBL", is_statement:"yes", filing_type:"quarterly", filing_period:["Q2-2024","Q2-2023"]}
3  "UBL balance sheet Q1 2024"
    {ticker:"UBL", is_statement:"yes", filing_type:"quarterly", filing_period:["Q1-2024","Q1-2023"]}
4  "UBL balance sheet Q2 2024"
    {ticker:"UBL", is_statement:"yes", filing_type:"quarterly", filing_period:["Q2-2024","Q2-2023"]}
→ intent = "analysis"

*LEVEL 4: FULL COMPLEXITY (2×2×2 = 8 queries)*

"HBL and UBL Q1-2024 and Q2-2024 balance sheet and profit and loss"
→ Creates: 8 queries (2 companies × 2 period sets × 2 statements):
1  "HBL balance sheet Q1 2024"
    {ticker:"HBL", statement_type:"balance_sheet", is_statement:"yes", filing_type:"quarterly", filing_period:["Q1-2024","Q1-2023"]}
2  "HBL balance sheet Q2 2024"
    {ticker:"HBL", statement_type:"balance_sheet", is_statement:"yes", filing_type:"quarterly", filing_period:["Q2-2024","Q2-2023"]}
3  "HBL profit and loss Q1 2024"
    {ticker:"HBL", statement_type:"profit_and_loss", is_statement:"yes", filing_type:"quarterly", filing_period:["Q1-2024","Q1-2023"]}
4  "HBL profit and loss Q2 2024"
    {ticker:"HBL", statement_type:"profit_and_loss", is_statement:"yes", filing_type:"quarterly", filing_period:["Q2-2024","Q2-2023"]}
5  "UBL balance sheet Q1 2024"
    {ticker:"UBL", statement_type:"balance_sheet", is_statement:"yes", filing_type:"quarterly", filing_period:["Q1-2024","Q1-2023"]}
6  "UBL balance sheet Q2 2024"
    {ticker:"UBL", statement_type:"balance_sheet", is_statement:"yes", filing_type:"quarterly", filing_period:["Q2-2024","Q2-2023"]}
7  "UBL profit and loss Q1 2024"
    {ticker:"UBL", statement_type:"profit_and_loss", is_statement:"yes", filing_type:"quarterly", filing_period:["Q1-2024","Q1-2023"]}
8  "UBL profit and loss Q2 2024"
    {ticker:"UBL", statement_type:"profit_and_loss", is_statement:"yes", filing_type:"quarterly", filing_period:["Q2-2024","Q2-2023"]}
→ intent = "analysis"

*CROSS-PERIOD PATTERNS*

"HBL 2024 and 2022 balance sheet"
→ Creates: 2 queries (2 annual period sets):
1  "HBL balance sheet 2024"
    {is_statement:"yes", filing_type:"annual", filing_period:["2024","2023"]}
2  "HBL balance sheet 2022"
    {is_statement:"yes", filing_type:"annual", filing_period:["2022","2021"]}
→ intent = "analysis"

*LAST N QUARTERS PATTERNS*

"HBL last 3 quarters balance sheet"
→ Creates: 3 queries (ONLY quarterly - client adds annual):
1  "HBL balance sheet Q1 2025"
    {is_statement:"yes", filing_type:"quarterly", filing_period:["Q1-2025","Q1-2024"]}
2  "HBL balance sheet Q3 2024"
    {is_statement:"yes", filing_type:"quarterly", filing_period:["Q3-2024","Q3-2023"]}
3  "HBL balance sheet Q2 2024"
    {is_statement:"yes", filing_type:"quarterly", filing_period:["Q2-2024","Q2-2023"]}
→ intent = "statement"

"UBL profit and loss for last 4 quarters with notes breakdown"
→ Creates: 4 queries (ONLY quarterly - client adds annual + notes):
1  "UBL profit and loss Q1 2025"
    {ticker:"UBL", statement_type:"profit_and_loss", is_statement:"yes", filing_type:"quarterly", filing_period:["Q1-2025","Q1-2024"]}
2  "UBL profit and loss Q3 2024"
    {ticker:"UBL", statement_type:"profit_and_loss", is_statement:"yes", filing_type:"quarterly", filing_period:["Q3-2024","Q3-2023"]}
3  "UBL profit and loss Q2 2024"
    {ticker:"UBL", statement_type:"profit_and_loss", is_statement:"yes", filing_type:"quarterly", filing_period:["Q2-2024","Q2-2023"]}
4  "UBL profit and loss Q1 2024"
    {ticker:"UBL", statement_type:"profit_and_loss", is_statement:"yes", filing_type:"quarterly", filing_period:["Q1-2024","Q1-2023"]}
→ intent = "statement"

"FABL, BIPL and MEBL last 4 quarters analysis"
→ Creates: 36 queries (3 companies × 3 statements × 4 period sets):
1  "FABL balance sheet Q1 2025"
    {ticker:"FABL", statement_type:"balance_sheet", is_statement:"yes", filing_type:"quarterly", filing_period:["Q1-2025","Q1-2024"]}
2  "FABL profit and loss Q1 2025"
    {ticker:"FABL", statement_type:"profit_and_loss", is_statement:"yes", filing_type:"quarterly", filing_period:["Q1-2025","Q1-2024"]}
3  "FABL cash flow Q1 2025"
    {ticker:"FABL", statement_type:"cash_flow", is_statement:"yes", filing_type:"quarterly", filing_period:["Q1-2025","Q1-2024"]}
4  "BIPL balance sheet Q1 2025"
    {ticker:"BIPL", statement_type:"balance_sheet", is_statement:"yes", filing_type:"quarterly", filing_period:["Q1-2025","Q1-2024"]}
5  "MEBL balance sheet Q1 2025"
    {ticker:"MEBL", statement_type:"balance_sheet", is_statement:"yes", filing_type:"quarterly", filing_period:["Q1-2025","Q1-2024"]}
6  "FABL balance sheet Q3 2024"
    {ticker:"FABL", statement_type:"balance_sheet", is_statement:"yes", filing_type:"quarterly", filing_period:["Q3-2024","Q3-2023"]}
7  "FABL balance sheet Q2 2024"
    {ticker:"FABL", statement_type:"balance_sheet", is_statement:"yes", filing_type:"quarterly", filing_period:["Q2-2024","Q2-2023"]}
8  "FABL balance sheet 2024"
    {ticker:"FABL", statement_type:"balance_sheet", is_statement:"yes", filing_type:"annual", filing_period:["2024","2023"]}
9  "BIPL balance sheet 2024"
    {ticker:"BIPL", statement_type:"balance_sheet", is_statement:"yes", filing_type:"annual", filing_period:["2024","2023"]}
10 "MEBL balance sheet 2024"
    {ticker:"MEBL", statement_type:"balance_sheet", is_statement:"yes", filing_type:"annual", filing_period:["2024","2023"]}
→ intent = "analysis"
→ Last 4 quarters: Q1 2025, Q4 2024, Q3 2024, Q2 2024 (for each company)
→ Total: 3 companies × 3 statements × 4 period sets = 36 queries

*NOTES PATTERNS*

"UBL profit and loss with notes 2024"
→ Creates: 2 queries (statement query + note query)
Statement query: {ticker:"UBL", statement_type:"profit_and_loss", is_statement:"yes", is_note:"no", filing_type:"annual", filing_period:["2024","2023"]}
Note query: {ticker:"UBL", note_link:"profit_and_loss", is_statement:"no", is_note:"yes", filing_type:"annual", filing_period:["2024","2023"]}
→ intent = "analysis"

*BROAD ANALYSIS PATTERNS*

"Ratios for FABL & MEBL 2024"
→ Creates: 8 queries (2 companies × 3 statements + 2 exposure queries)
Example (FABL):
• Statement query: {ticker:"FABL", statement_type:"balance_sheet", is_statement:"yes", filing_type:"annual", filing_period:["2024","2023"]}
• Exposure query: {ticker:"FABL", filing_type:"annual", filing_period:["2024","2023"]}  
→ intent = "analysis"

"financial ratios analysis for FABL and MEBL"
→ Creates: 6 queries (2 companies × 3 varied search terms + time periods)
1  "FABL capital adequacy ratio"
    {ticker:"FABL", filing_type:"annual", filing_period:["2024","2023"]}
2  "FABL liquidity ratios"
    {ticker:"FABL", filing_type:"annual", filing_period:["2023","2022"]}
3  "FABL profitability metrics"
    {ticker:"FABL", filing_type:"annual", filing_period:["2022","2021"]}
4  "MEBL capital adequacy ratio"
    {ticker:"MEBL", filing_type:"annual", filing_period:["2024","2023"]}
5  "MEBL liquidity ratios"
    {ticker:"MEBL", filing_type:"annual", filing_period:["2023","2022"]}
6  "MEBL profitability metrics"
    {ticker:"MEBL", filing_type:"annual", filing_period:["2022","2021"]}
→ intent = "analysis"

*BROAD METRIC ANALYSIS PATTERNS (NO STATEMENT TYPE SEPARATION)*

"deposits per branch comparison for FABL, BIPL and MEBL"
→ Creates: 9 queries (3 companies × 3 varied search terms + time periods)
→ No statement_type separation, vary both search terms AND time periods:
1  "FABL number of branches"
    {ticker:"FABL", filing_type:"annual", filing_period:["2024","2023"]}
2  "FABL branch growth"
    {ticker:"FABL", filing_type:"annual", filing_period:["2023","2022"]}
3  "FABL deposits"
    {ticker:"FABL", filing_type:"annual", filing_period:["2022","2021"]}
4  "BIPL number of branches"
    {ticker:"BIPL", filing_type:"annual", filing_period:["2024","2023"]}
5  "BIPL branch growth"
    {ticker:"BIPL", filing_type:"annual", filing_period:["2023","2022"]}
6  "BIPL deposits"
    {ticker:"BIPL", filing_type:"annual", filing_period:["2022","2021"]}
7  "MEBL number of branches"
    {ticker:"MEBL", filing_type:"annual", filing_period:["2024","2023"]}
8  "MEBL branch growth"
    {ticker:"MEBL", filing_type:"annual", filing_period:["2023","2022"]}
9  "MEBL deposits"
    {ticker:"MEBL", filing_type:"annual", filing_period:["2022","2021"]}
→ intent = "analysis"

"branch efficiency analysis for HBL and UBL"
→ Creates: 6 queries (2 companies × 3 varied search terms + time periods)
1  "HBL branch efficiency"
    {ticker:"HBL", filing_type:"annual", filing_period:["2024","2023"]}
2  "HBL cost per branch"
    {ticker:"HBL", filing_type:"annual", filing_period:["2023","2022"]}
3  "HBL branch productivity"
    {ticker:"HBL", filing_type:"annual", filing_period:["2022","2021"]}
4  "UBL branch efficiency"
    {ticker:"UBL", filing_type:"annual", filing_period:["2024","2023"]}
5  "UBL cost per branch"
    {ticker:"UBL", filing_type:"annual", filing_period:["2023","2022"]}
6  "UBL branch productivity"
    {ticker:"UBL", filing_type:"annual", filing_period:["2022","2021"]}
→ intent = "analysis"

"profitability comparison for MCB and FABL"
→ Creates: 6 queries (2 companies × 3 varied search terms + time periods)
1  "MCB return on assets"
    {ticker:"MCB", filing_type:"annual", filing_period:["2024","2023"]}
2  "MCB net interest margin"
    {ticker:"MCB", filing_type:"annual", filing_period:["2023","2022"]}
3  "MCB profitability ratios"
    {ticker:"MCB", filing_type:"annual", filing_period:["2022","2021"]}
4  "FABL return on assets"
    {ticker:"FABL", filing_type:"annual", filing_period:["2024","2023"]}
5  "FABL net interest margin"
    {ticker:"FABL", filing_type:"annual", filing_period:["2023","2022"]}
6  "FABL profitability ratios"
    {ticker:"FABL", filing_type:"annual", filing_period:["2022","2021"]}
→ intent = "analysis"

"cost analysis for HBL, UBL and MCB"
→ Creates: 9 queries (3 companies × 3 varied search terms + time periods)
1  "HBL operating expenses"
    {ticker:"HBL", filing_type:"annual", filing_period:["2024","2023"]}
2  "HBL cost to income ratio"
    {ticker:"HBL", filing_type:"annual", filing_period:["2023","2022"]}
3  "HBL administrative expenses"
    {ticker:"HBL", filing_type:"annual", filing_period:["2022","2021"]}
4  "UBL operating expenses"
    {ticker:"UBL", filing_type:"annual", filing_period:["2024","2023"]}
5  "UBL cost to income ratio"
    {ticker:"UBL", filing_type:"annual", filing_period:["2023","2022"]}
6  "UBL administrative expenses"
    {ticker:"UBL", filing_type:"annual", filing_period:["2022","2021"]}
7  "MCB operating expenses"
    {ticker:"MCB", filing_type:"annual", filing_period:["2024","2023"]}
8  "MCB cost to income ratio"
    {ticker:"MCB", filing_type:"annual", filing_period:["2023","2022"]}
9  "MCB administrative expenses"
    {ticker:"MCB", filing_type:"annual", filing_period:["2022","2021"]}
→ intent = "analysis"

OUTPUT: QueryPlan JSON with companies[], intent, queries[], confidence"""


# ═══════════════════════════════════════════════════════════════════════
# TRADITIONAL PARSING SYSTEM - Using Full String Prompt
# ═══════════════════════════════════════════════════════════════════════

class TraditionalParsingSystem:
    """
    Traditional parsing system using the full PARSING_SYSTEM_PROMPT.
    This demonstrates the monolithic approach vs DSPy's modular approach.
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize with optional LLM client for actual parsing.
        For demo purposes, we'll simulate responses.
        """
        self.llm_client = llm_client
        self.parsing_prompt = PARSING_SYSTEM_PROMPT
    
    def parse_query(self, user_query: str, available_tickers: List[str]) -> Dict[str, Any]:
        """
        Parse user query using the full PARSING_SYSTEM_PROMPT string.
        
        This is the traditional approach: send the entire complex prompt to the LLM.
        """
        
        # Simple user prompt
        user_prompt = f"""Query: "{user_query}"

Available bank tickers: {available_tickers}

Create QueryPlan following system parsing rules."""
        
        # For demonstration, we'll simulate the LLM response
        if self.llm_client:
            # Real LLM call would go here - sends the ENTIRE parsing prompt
            response = self._call_llm(self.parsing_prompt, user_prompt)
            return self._parse_llm_response(response)
        else:
            # Simulate response for demo
            return self._simulate_parsing_response(user_query, available_tickers)
    
    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call the LLM with the full PARSING_SYSTEM_PROMPT.
        
        This is where the traditional approach sends the entire monolithic prompt
        (with all rules, examples, and logic) to the LLM in one call.
        
        The LLM must understand and follow all the complex instructions to produce
        the structured output.
        """
        # Placeholder for actual LLM integration
        # Example with OpenAI:
        # response = self.llm_client.chat.completions.create(
        #     model="gpt-4",
        #     messages=[
        #         {"role": "system", "content": system_prompt},  # <- Full PARSING_SYSTEM_PROMPT
        #         {"role": "user", "content": user_prompt}
        #     ]
        # )
        # return response.choices[0].message.content
        
        raise NotImplementedError(f"LLM client not configured. Would send {len(system_prompt)} character prompt to LLM.")
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured format."""
        try:
            # Extract JSON from response (assuming it's in the response)
            # This would need proper JSON extraction logic
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback parsing logic
            return {"error": "Could not parse LLM response", "raw_response": response}
    
    def _simulate_parsing_response(self, user_query: str, available_tickers: List[str]) -> Dict[str, Any]:
        """
        Placeholder for what the LLM would return when given the full PARSING_SYSTEM_PROMPT.
        
        In the traditional approach, ALL the parsing logic (company extraction, intent classification,
        period parsing, combinatorial expansion) is handled by the LLM following the complex prompt.
        
        This is just a demo placeholder - in reality, you'd get a response from the LLM.
        """
        
        return {
            "message": "🤖 LLM Response Placeholder",
            "explanation": "In the traditional approach, the LLM would process this query using the full PARSING_SYSTEM_PROMPT",
            "prompt_size": f"{len(self.parsing_prompt)} characters",
            "approach": "Monolithic - All logic in one complex prompt",
            "query": user_query,
            "available_tickers": available_tickers,
            "note": "The LLM would follow all the rules and examples in the PARSING_SYSTEM_PROMPT to generate the structured output"
        }


# ═══════════════════════════════════════════════════════════════════════
# DEMONSTRATION AND TESTING
# ═══════════════════════════════════════════════════════════════════════

def demonstrate_traditional_parsing():
    """Demonstrate the traditional parsing system using the monolithic prompt."""
    
    print("🎯 Traditional Parsing System Demo")
    print("=" * 50)
    
    parser = TraditionalParsingSystem()
    
    print(f"📋 Monolithic Prompt: {len(parser.parsing_prompt):,} characters")
    print("💡 ALL parsing logic is in this one massive string")
    
    # Test queries that show different parsing challenges
    test_queries = [
        "HBL 2024 balance sheet",
        "HBL and UBL financial performance analysis", 
        "Compare MCB vs NBP last 3 quarters",
    ]
    
    available_tickers = ["HBL", "UBL", "MCB", "NBP", "BAFL"]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 50)
        
        result = parser.parse_query(
            user_query=query,
            available_tickers=available_tickers
        )
        
        print(f"🤖 {result['message']}")
        print(f"📏 Prompt Size: {result['prompt_size']}")
        print(f"🔧 {result['approach']}")
        print(f"💡 The LLM must extract companies, periods, intent, and generate")
        print(f"   structured output by following the complex prompt rules")

def show_full_prompt_structure():
    """Show the structure of the full PARSING_SYSTEM_PROMPT."""
    
    print("\n📖 PARSING_SYSTEM_PROMPT STRUCTURE")
    print("=" * 50)
    
    full_prompt = PARSING_SYSTEM_PROMPT
    
    # Extract sections
    sections = [
        "CONTEXT:", "CORE RULES:", "METADATA SCHEMA:", "FILTER PRIORITIES:",
        "INTENT CLASSIFICATION", "ANALYSIS KEYWORDS:", "BROAD ANALYSIS",
        "NOTES HANDLING:", "PERIOD FORMAT", "SEARCH QUERY:", "STANDARD EXAMPLES"
    ]
    
    for section in sections:
        if section in full_prompt:
            start = full_prompt.find(section)
            # Find next section or end
            next_section_start = len(full_prompt)
            for next_section in sections:
                if next_section != section and next_section in full_prompt:
                    next_start = full_prompt.find(next_section)
                    if next_start > start and next_start < next_section_start:
                        next_section_start = next_start
            
            section_content = full_prompt[start:next_section_start]
            lines = len(section_content.split('\n'))
            print(f"📝 {section:<20} {lines:>3} lines")
    
    print(f"\n📏 Total Length: {len(full_prompt)} characters")
    newline_count = len(full_prompt.split('\n'))
    print(f"📄 Total Lines: {newline_count} lines")
    print(f"💡 This entire prompt gets sent to LLM in one call")

if __name__ == "__main__":
    print("🔧 Traditional Parsing System - Using Full PARSING_SYSTEM_PROMPT")
    print("=" * 60)
    
    # Show prompt structure
    show_full_prompt_structure()
    
    # Demonstrate parsing
    demonstrate_traditional_parsing()
    
    print("\n🎯 KEY INSIGHT:")
    print("Traditional approach: Send entire complex prompt to LLM")
    print("- All parsing logic, rules, and examples in one monolithic prompt")
    print("- LLM must understand and follow all instructions correctly")
    print("- Success depends on LLM's ability to handle complex instructions")
    print("- Debugging issues requires analyzing the entire prompt") 