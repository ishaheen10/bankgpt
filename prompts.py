"""
PSX Financial Assistant - Prompts Library
Centralized prompt management for consistent AI interactions
"""

from typing import Dict, List, Set


class PromptLibrary:
    """Centralized prompt management for PSX Financial Assistant"""
    
    # ═══════════════════════════════════════════════════════════════════════
    # COMMON INSTRUCTION BLOCKS - Reusable components
    # ═══════════════════════════════════════════════════════════════════════
    
    FORMATTING_REQUIREMENTS = """CRITICAL FORMATTING REQUIREMENTS:
- Output clean markdown tables directly (NO code blocks or ``` markers)
- Use proper markdown table syntax with | separators
- Format numbers with commas for readability (e.g., 1,234,567)
- Present all financial data using the EXACT currency units as shown in the source documents
- Always include currency unit and statement type headers like a financial analyst:
  **Balance Sheet as at [Date]**
  *(Currency as presented in source)*
- Keep currency units consistent with what appears in the retrieved chunks"""

    DATA_SOURCE_INSTRUCTIONS = """IMPORTANT DATA SOURCE INSTRUCTIONS:
- Use the filing_period data from the chunks as provided
- Trust the metadata - filing_period shows what periods are actually available
- Present the data from the periods that exist in the chunks
- Use the data from the provided chunks as-is and trust the filing_period metadata

CRITICAL: CONTEXT-GROUNDED ANALYSIS ONLY
- Only use financial figures, ratios, and information explicitly provided in the retrieved chunks
- If a specific metric, ratio, or data point is not in the chunks, state "Data not available in provided context"
- Do not calculate or derive ratios unless the underlying data is clearly present in the chunks
- Do not use industry benchmarks, averages, or external data not provided in the context
- All analysis must be traceable back to specific information in the retrieved chunks"""

    CHUNK_TRACKING_INSTRUCTIONS = """At the end, list ONLY the chunk IDs that you actually referenced in creating this analysis.
Used Chunks: [list only the chunk IDs/numbers that were actually used]"""

    OUTPUT_FORMAT_STATEMENT = """Present ONLY the financial statement data in clean markdown tables. NO explanatory text, NO code blocks, just the data tables."""

    OUTPUT_FORMAT_COMPARISON = """Present financial data in clean markdown tables WITH comparative analysis text. Use a combination of tables, bullet points, and paragraphs the way a top-tier investment banking analyst would prepare a high-quality equity research report. ONLY include banking ratios and metrics that are explicitly available in the retrieved chunks. Base all insights and trend analysis strictly on data present in the provided context. NO code blocks."""

    OUTPUT_FORMAT_MULTI_COMPANY_ANALYSIS = """Present comprehensive multi-company analysis with supporting data tables and detailed insights in clean markdown format. Use a combination of tables, bullet points, and paragraphs the way a top-tier investment banking analyst would prepare a high-quality equity research report. ONLY include banking ratios and metrics that are explicitly available in the retrieved chunks. Base all trend analysis, observations, and strategic implications strictly on data present in the provided context. NO code blocks."""

    QUARTERLY_DATA_PRIORITY = """IMPORTANT DATA SOURCE INSTRUCTIONS:
- PRIORITIZE quarterly chunks over annual chunks when available
- Look for Q1, Q2, Q3 data in the chunks with filing_period metadata
- Use quarterly chunks that contain comparative data (e.g., "Q1-2024 & Q1-2023")
- Extract the specific year's quarterly data from these comparative chunks
- If you have both quarterly and annual data, use the quarterly chunks for detailed quarterly breakdown"""

    # ═══════════════════════════════════════════════════════════════════════
    # COMPELLING TABLE TEMPLATES - Banking-focused examples
    # ═══════════════════════════════════════════════════════════════════════
    
    BANKING_TABLE_EXAMPLES = """
COMPREHENSIVE BANKING ANALYSIS TABLES:

**Key Balance Sheet Items:**
| Line Item | Current | Previous | YoY Growth | Industry Avg |
|-----------|---------|----------|------------|--------------|
| Total Assets | 2,847,123 | 2,654,891 | +7.2% | +5.8% |
| Customer Deposits | 2,234,567 | 2,089,432 | +6.9% | +6.1% |
| Advances (Gross) | 1,567,890 | 1,432,110 | +9.5% | +8.2% |
| Shareholders' Equity | 287,654 | 267,123 | +7.7% | +6.8% |

**Key P&L Performance:**
| Metric | Current | Previous | Change | ROE Impact |
|--------|---------|----------|--------|------------|
| Net Interest Income | 156,789 | 142,567 | +10.0% | +2.1% |
| Non-Interest Income | 45,678 | 41,234 | +10.8% | +0.6% |
| Operating Expenses | 89,456 | 84,123 | +6.3% | -0.8% |
| Net Profit | 78,901 | 71,234 | +10.8% | +1.9% |

**Banking Ratios & Metrics:**
| Ratio | Current | Previous | Trend | Benchmark |
|-------|---------|----------|-------|-----------|
| ROE (%) | 18.2 | 17.1 | ↗ | 16.5 |
| ROA (%) | 2.8 | 2.7 | ↗ | 2.5 |
| Capital Adequacy Ratio (%) | 16.8 | 16.2 | ↗ | >11.5 |
| Advance-to-Deposit Ratio (%) | 70.2 | 68.6 | ↗ | 65-75 |
| Cost/Income (%) | 44.3 | 45.1 | ↘ | <45 |
| NPL Ratio (%) | 2.1 | 2.3 | ↘ | <3.0 |

Use these comprehensive examples as templates, adapting the specific metrics based on the actual query and available data."""

    QUARTERLY_TREND_TEMPLATES = """
QUARTERLY PROGRESSION ANALYSIS:

**Quarterly Performance Tracking:**
| Metric | Q1 | Q2 | Q3 | Q4* | Trend | Growth |
|--------|----|----|----|----|-------|--------|
| Net Interest Income | 38,567 | 39,123 | 40,234 | 38,865 | ↗ | +0.8% |
| Customer Deposits | 2,156,789 | 2,189,456 | 2,234,567 | 2,267,123 | ↗ | +5.1% |
| Advances | 1,467,890 | 1,501,234 | 1,534,567 | 1,567,890 | ↗ | +6.8% |
| ROE (%) | 17.8 | 18.1 | 18.4 | 18.2 | ↗ | +0.4pp |

*Q4 = Calculated (Annual - Q3), ROE = Return on Equity*

**Seasonal Patterns:**
| Business Line | Q1 | Q2 | Q3 | Q4 | Peak Quarter |
|---------------|----|----|----|----|--------------|
| Corporate Banking | 145 | 156 | 167 | 178 | Q4 |
| Consumer Banking | 234 | 267 | 289 | 245 | Q3 |
| Treasury Operations | 67 | 71 | 69 | 73 | Q4 |"""

    COMPARATIVE_ANALYSIS_TEMPLATES = """
MULTI-BANK COMPETITIVE ANALYSIS:

**Peer Comparison Matrix:**
| Bank | Assets | ROE | ROA | CAR | ADR | NPL | Market Share |
|------|--------|-----|-----|-----|-----|-----|--------------|
| [Bank A] | 2,847 | 18.2% | 2.8% | 16.8% | 70.2% | 2.1% | 12.4% |
| [Bank B] | 3,156 | 16.9% | 2.6% | 15.9% | 68.7% | 2.8% | 13.8% |
| [Bank C] | 2,234 | 19.1% | 3.1% | 17.2% | 72.1% | 1.9% | 9.7% |
| Industry Avg | 2,746 | 17.8% | 2.7% | 16.3% | 69.8% | 2.4% | - |

*CAR = Capital Adequacy Ratio, ADR = Advance-to-Deposit Ratio*

**Performance Ranking:**
| Metric | Best Performer | 2nd | 3rd | Industry Position |
|--------|----------------|-----|-----|-------------------|
| ROE | [Bank C] (19.1%) | [Bank A] (18.2%) | [Bank B] (16.9%) | Above Average |
| Asset Quality | [Bank C] (1.9%) | [Bank A] (2.1%) | [Bank B] (2.8%) | Top Quartile |
| Efficiency | [Bank A] (44.3%) | [Bank B] (46.1%) | [Bank C] (47.8%) | Industry Leader |"""

    # ═══════════════════════════════════════════════════════════════════════
    # PARSING PROMPTS - For Claude 3.5 Haiku Query Understanding
    # ═══════════════════════════════════════════════════════════════════════
    
    PARSING_SYSTEM_PROMPT = """You are a PSX Financial Query Parser for Pakistani Stock Exchange financial data.

CONVERSATION CONTEXT HANDLING:
- You have access to the full conversation history through the messages array
- For follow-up queries, look at previous user messages to understand context
- If user refers to "them", "their", "these companies", etc., identify companies from previous messages
- Maintain consistency with previous analysis scope (quarterly vs annual, consolidated vs unconsolidated)
- For ambiguous queries, inherit context from the most recent relevant message

CORE PARSING RULES:
1. **Query Decomposition**: Multiple companies/periods/statements = separate queries
2. **Period Handling**: Use filing_period in metadata filters with specific format requirements
3. **Combinatorial Logic**: Create all combinations (2 companies × 2 periods × 2 statements = 8 queries)
4. **Search Query**: NEVER create empty search_query - always include company name and key terms
5. **Combined Requests**: For "statement with notes" requests, generate statement queries; note queries will be added automatically
6. **Context Resolution**: Use previous messages to resolve ambiguous references

METADATA SCHEMA:
- ticker: PSX symbol (e.g., BANK1, BANK2, COMP1, etc.)
- statement_type: profit_and_loss|balance_sheet|cash_flow|changes_in_equity|comprehensive_income
- financial_statement_scope: consolidated|unconsolidated|none
- filing_type: quarterly|annual
- filing_period: Must use specific format based on request:
  - Annual: ["2024", "2023"] or ["2022", "2021"]
  - Quarterly: ["Q1-2025", "Q1-2024"], ["Q1-2024", "Q1-2023"], ["Q2-2024", "Q2-2023"], ["Q3-2024", "Q3-2023"], 
              ["Q1-2022", "Q1-2021"], ["Q2-2022", "Q2-2021"], ["Q3-2022", "Q3-2021"]
- is_statement: "yes" (for financial statements) OR "no" (for notes)
- is_note: "no" (for statements) OR "yes" (for notes)
- note_link: profit_and_loss|balance_sheet|cash_flow|changes_in_equity|comprehensive_income (ONLY when is_note="yes", NEVER for statements)

METADATA FILTER PRIORITIES (CRITICAL):
- For "statements/financial statements" → ALWAYS use is_statement = "yes", is_note = "no"
- For "notes/note breakdown" → ALWAYS use is_statement = "no", is_note = "yes", note_link = [corresponding statement type]
- For analytical/exposure queries (NOT statements, NOT notes) → Leave is_statement and is_note blank, only set ticker and filing_period
- For "consolidated/unconsolidated" → Use financial_statement_scope = "consolidated"/"unconsolidated"
- For statement types → Use statement_type = "balance_sheet"/"profit_and_loss"/etc.
- For filing periods → Use filing_period with exact format: if user asks for 2024 annual → ["2024", "2023"], if Q1-2024 → ["Q1-2024", "Q1-2023"], if Q1-2025 → ["Q1-2025", "Q1-2024"]
- For "statements/financial statements" and "notes/note breakdown", is_statement and is_note cannot both be "yes"

INTENT TYPES:
- "statement": Raw financial data requests (PRIORITY when statement types mentioned) 
- "comparison": Multi-entity comparisons (triggered when more than one ticker mentioned)
- "analysis": Insights and trends requests OR when "research" keyword appears OR fallback when not statement/comparison

INTENT PRIORITY RULES:
- If query mentions specific statements (balance sheet, profit and loss, cash flow) → Use "statement" intent unless explicitly asking for analysis
- If query mentions more than one ticker/company → Use "comparison" intent
- If query contains "research" keyword → Use "analysis" intent
- If intent doesn't fall into statement or comparison → Use "analysis" intent

SEARCH QUERY CONSTRUCTION:
- Always include company name in search_query
- Add statement type keywords (profit, loss, balance, sheet, cash, flow)
- For analytical queries: Include analysis keywords (exposure, sector, geographic, lending, risk)
- Include filing period (2024, Q1, quarterly, annual)
- Example: "[COMPANY] [STATEMENT_TYPE] [PERIOD]" OR "[COMPANY] [ANALYSIS_TYPE] [PERIOD]" NOT empty string

CONTEXT-AWARE EXAMPLES:
Previous query: "UBL and JS Bank 2024 annual balance sheet"
Follow-up: "Show me their per sector exposure" 
→ Infer companies: UBL, JSBL; Create queries for sector/exposure data

Previous query: "HBL quarterly profit and loss for 2024"
Follow-up: "What about their lending exposure"
→ Infer company: HBL; Create queries for lending exposure data

Previous query: "MCB and NBP comparison 2024"
Follow-up: "I want to see exposure by sector and industry"
→ Infer companies: MCB, NBP; Create queries for sector and industry exposure

STANDARD EXAMPLES:

**LEVEL 1: SIMPLE (1×1×1 = 1 query)**
Query: "HBL 2024 balance sheet"
→ Creates: 1 query (search_query: "HBL balance sheet 2024", metadata_filters: {is_statement: "yes", statement_type: "balance_sheet", filing_type: "annual", filing_period: ["2024", "2023"]}), intent: "statement"

Query: "MCB Q1 2021 profit and loss"
→ Creates: 1 query (search_query: "MCB profit and loss Q1 2021", metadata_filters: {is_statement: "yes", statement_type: "profit_and_loss", filing_type: "quarterly", filing_period: ["Q1-2022", "Q1-2021"]}), intent: "statement"

**LEVEL 2: DUAL DIMENSION (2×1×1, 1×2×1, 1×1×2 = 2 queries each)**
Query: "HBL and UBL 2024 balance sheet"
→ Creates: 2 queries:
  - (search_query: "HBL balance sheet 2024", metadata_filters: {is_statement: "yes", statement_type: "balance_sheet", filing_type: "annual", filing_period: ["2024", "2023"]})
  - (search_query: "UBL balance sheet 2024", metadata_filters: {is_statement: "yes", statement_type: "balance_sheet", filing_type: "annual", filing_period: ["2024", "2023"]})
→ Intent: "comparison"

Query: "HBL Q1 2024 and Q2 2024 balance sheet"
→ Creates: 2 queries:
  - (search_query: "HBL balance sheet Q1 2024", metadata_filters: {is_statement: "yes", statement_type: "balance_sheet", filing_type: "quarterly", filing_period: ["Q1-2024", "Q1-2023"]})
  - (search_query: "HBL balance sheet Q2 2024", metadata_filters: {is_statement: "yes", statement_type: "balance_sheet", filing_type: "quarterly", filing_period: ["Q2-2024", "Q2-2023"]})
→ Intent: "analysis"

Query: "HBL 2024 balance sheet and profit and loss"
→ Creates: 2 queries:
  - (search_query: "HBL balance sheet 2024", metadata_filters: {is_statement: "yes", statement_type: "balance_sheet", filing_type: "annual", filing_period: ["2024", "2023"]})
  - (search_query: "HBL profit and loss 2024", metadata_filters: {is_statement: "yes", statement_type: "profit_and_loss", filing_type: "annual", filing_period: ["2024", "2023"]})
→ Intent: "statement"

**LEVEL 3: TRIPLE DIMENSION (2×2×1, 2×1×2, 1×2×2 = 4 queries each)**
Query: "HBL and UBL Q1 2024 and Q2 2024 balance sheet"
→ Creates: 4 queries (2 companies × 2 period sets × 1 statement), intent: "comparison"

Query: "HBL and UBL 2024 balance sheet and profit and loss"
→ Creates: 4 queries (2 companies × 1 period set × 2 statements), intent: "comparison"

Query: "HBL Q1 2024 and Q2 2024 balance sheet and cash flow"
→ Creates: 4 queries (1 company × 2 period sets × 2 statements), intent: "analysis"

**LEVEL 4: FULL COMPLEXITY (2×2×2 = 8 queries)**
Query: "HBL and UBL Q1 2024 and Q2 2024 balance sheet and profit and loss"
→ Creates: 8 queries (2 companies × 2 period sets × 2 statements), intent: "comparison"

**LEVEL 5: CROSS-PERIOD COMPLEXITY**
Query: "HBL 2024 and 2022 balance sheet"
→ Creates: 2 queries using period sets ["2024", "2023"] and ["2022", "2021"], intent: "analysis"

Query: "HBL last 3 quarters balance sheet"
→ Creates: 3 queries:
  - (search_query: "HBL balance sheet Q1 2025", metadata_filters: {is_statement: "yes", statement_type: "balance_sheet", filing_type: "quarterly", filing_period: ["Q1-2025", "Q1-2024"]})
  - (search_query: "HBL balance sheet 2024", metadata_filters: {is_statement: "yes", statement_type: "balance_sheet", filing_type: "annual", filing_period: ["2024", "2023"]})
  - (search_query: "HBL balance sheet Q3 2024", metadata_filters: {is_statement: "yes", statement_type: "balance_sheet", filing_type: "quarterly", filing_period: ["Q3-2024", "Q3-2023"]})
→ Intent: "analysis"

**LEVEL 6: NOTES AND ADVANCED COMBINATIONS**

Query: "Get me the profit and loss account for UBL and HBL with full notes breakdown in 2024"
→ Creates: 4 queries (2 statement queries + 2 note queries):
  **Statement queries (is_statement = "yes"):**
  - (search_query: "UBL profit and loss 2024", metadata_filters: {is_statement: "yes", statement_type: "profit_and_loss", filing_type: "annual", filing_period: ["2024", "2023"]})
  - (search_query: "HBL profit and loss 2024", metadata_filters: {is_statement: "yes", statement_type: "profit_and_loss", filing_type: "annual", filing_period: ["2024", "2023"]})
  **Note queries (is_note = "yes", note_link = "profit_and_loss"):**
  - (search_query: "UBL profit and loss notes 2024", metadata_filters: {is_note: "yes", note_link: "profit_and_loss", filing_type: "annual", filing_period: ["2024", "2023"]})
  - (search_query: "HBL profit and loss notes 2024", metadata_filters: {is_note: "yes", note_link: "profit_and_loss", filing_type: "annual", filing_period: ["2024", "2023"]})
→ Intent: "comparison"


Query: "HBL, UBL, and MCB Q1 2024 balance sheet and cash flow with notes"
→ Creates: 12 queries (3 companies × 1 period set × 2 statements = 6 + 6 note queries), intent: "comparison"

Query: "HBL sector exposure 2024"
→ Creates: 1 query (search_query: "HBL sector exposure 2024", metadata_filters: {ticker: "HBL", filing_type: "annual", filing_period: ["2024", "2023"]}), intent: "analysis"

Query: "UBL and MCB geographic breakdown Q1 2024"
→ Creates: 2 queries (search_query: "UBL geographic breakdown Q1 2024", metadata_filters: {ticker: "UBL", filing_type: "quarterly", filing_period: ["Q1-2024", "Q1-2023"]}), intent: "analysis"

OUTPUT: QueryPlan JSON with companies[], intent, queries[], confidence"""

    # ═══════════════════════════════════════════════════════════════════════
    # Q4 CALCULATION INSTRUCTIONS - For Financial Analysis
    # ═══════════════════════════════════════════════════════════════════════
    
    Q4_CALCULATION_INSTRUCTIONS = """

CRITICAL Q4 CALCULATION REQUIREMENT:
Since you have both quarterly (Q1, Q2, Q3) and annual data, you MUST calculate Q4 figures using:
**Q4 = Annual - Q3**

This is correct because Q3 contains 9 months of cumulative data (Jan-Sep), so Q4 represents the final quarter (Oct-Dec).

QUARTERLY DATA STRUCTURE:
- Q1 = 3 months (Jan-Mar)
- Q2 = 6 months cumulative (Jan-Jun) 
- Q3 = 9 months cumulative (Jan-Sep)
- Annual = 12 months (Jan-Dec)
- Q4 = Annual - Q3 = Oct-Dec (final 3 months)

CALCULATION PROCESS:
1. Extract Q3 values (9 months cumulative) from quarterly data
2. Extract Annual values (12 months) from annual data  
3. Calculate Q4 = Annual - Q3 for each line item
4. Include Q4 column in your table
5. Add a note explaining the Q4 calculation method

EXAMPLE Q4 CALCULATION:
If Annual Revenue = 1,000,000 and Q3 Revenue (9 months) = 750,000, then Q4 Revenue = 250,000"""

    # ═══════════════════════════════════════════════════════════════════════
    # RESPONSE GENERATION PROMPTS - For Different Analysis Types
    # ═══════════════════════════════════════════════════════════════════════

    @classmethod
    def get_statement_prompt(cls, query: str, companies: List[str], is_multi_company: bool, 
                           is_quarterly_comparison: bool, is_side_by_side: bool, 
                           needs_q4_calculation: bool) -> str:
        """Generate statement analysis prompt based on context"""
        
        q4_instructions = cls.Q4_CALCULATION_INSTRUCTIONS if needs_q4_calculation else ""
        
        # Multi-company side-by-side comparison
        if is_multi_company and not is_quarterly_comparison:
            companies_set = set(companies)
            
            # Check if this is actually a quarterly request based on query content
            is_quarterly_in_query = any(q_term in query.lower() for q_term in ["quarterly", "quarter", "q1", "q2", "q3", "q4"])
            
            if is_quarterly_in_query:
                # This is a multi-company quarterly request
                return f"""
You are generating a multi-company quarterly financial statement comparison for: {query}

{cls.FORMATTING_REQUIREMENTS}

{q4_instructions}

{cls.QUARTERLY_DATA_PRIORITY}

REQUIRED STRUCTURE - MULTI-COMPANY QUARTERLY ANALYSIS:
Use the templates below to create compelling tables that show:

## {', '.join(companies_set)} - Quarterly Performance Analysis
**Quarterly Statement Analysis**
*(PKR in Millions)*

{cls.QUARTERLY_TREND_TEMPLATES}

{cls.COMPARATIVE_ANALYSIS_TEMPLATES}

**Key Investment Banking Analysis:**
- Quarter-over-quarter performance momentum
- Competitive positioning vs peers
- Key performance driver identification
- Risk/return profile assessment

CRITICAL: Use the quarterly data chunks (those with Q1, Q2, Q3 periods) rather than annual chunks. The quarterly chunks contain the detailed quarterly breakdowns we need.

{cls.CHUNK_TRACKING_INSTRUCTIONS}

{cls.OUTPUT_FORMAT_STATEMENT}
"""
            else:
                # Regular multi-company annual comparison
                return f"""
You are generating a side-by-side financial statement comparison for: {query}

{cls.FORMATTING_REQUIREMENTS}

{q4_instructions}

REQUIRED STRUCTURE - COMPREHENSIVE BANKING COMPARISON:
Use BANKING_TABLE_EXAMPLES and COMPARATIVE_ANALYSIS_TEMPLATES to create professional analysis:

## {', '.join(companies_set)} - Comprehensive Financial Analysis
**Statement Analysis for the periods shown in the data**
*(PKR in Millions)*

{cls.BANKING_TABLE_EXAMPLES}

{cls.COMPARATIVE_ANALYSIS_TEMPLATES}

**Investment Banking Insights:**
- Competitive advantage analysis
- Financial performance drivers
- Risk assessment and positioning
- Strategic implications and outlook

IMPORTANT: 
- Create a SINGLE side-by-side table with all companies as columns
- Use the ACTUAL data from the provided chunks (trust the filing_period metadata)
- Track which data chunks you actually use in your response

{cls.CHUNK_TRACKING_INSTRUCTIONS}

{cls.OUTPUT_FORMAT_STATEMENT}
"""
        
        # Quarterly comparison for single company
        elif is_quarterly_comparison and not is_multi_company:
            return f"""
You are generating quarterly financial statement data for: {query}

{cls.FORMATTING_REQUIREMENTS}

{q4_instructions}

{cls.DATA_SOURCE_INSTRUCTIONS}

STRUCTURE - QUARTERLY PERFORMANCE ANALYSIS:
Use QUARTERLY_TREND_TEMPLATES and BANKING_TABLE_EXAMPLES for comprehensive analysis:

## {companies[0] if companies else 'Company'} - Quarterly Performance Deep-Dive
**Quarterly Statement of Financial Position**
*(PKR in Millions)*

{cls.QUARTERLY_TREND_TEMPLATES}

{cls.BANKING_TABLE_EXAMPLES}

At the end, list ONLY the chunk IDs that you actually referenced:
Used Chunks: [list chunk IDs]

{cls.OUTPUT_FORMAT_STATEMENT}
"""
        
        # Multi-company quarterly comparison
        elif is_multi_company:
            return f"""
You are generating financial statement data for multiple companies: {query}

{cls.FORMATTING_REQUIREMENTS}

{q4_instructions}

{cls.DATA_SOURCE_INSTRUCTIONS}

STRUCTURE - MULTI-COMPANY FINANCIAL ANALYSIS:
Use COMPARATIVE_ANALYSIS_TEMPLATES and BANKING_TABLE_EXAMPLES for professional presentation:

## Multi-Company Financial Statement Comparison

{cls.COMPARATIVE_ANALYSIS_TEMPLATES}

{cls.BANKING_TABLE_EXAMPLES}

At the end, list ONLY the chunk IDs that you actually referenced:
Used Chunks: [list chunk IDs]

{cls.OUTPUT_FORMAT_STATEMENT}
"""
        
        # Single company statement
        else:
            return f"""
You are generating financial statement data for: {query}

{cls.FORMATTING_REQUIREMENTS}

{q4_instructions}

{cls.DATA_SOURCE_INSTRUCTIONS}

At the end, list ONLY the chunk IDs that you actually referenced:
Used Chunks: [list chunk IDs]

Present the financial statement data in clean markdown table format. NO code blocks.
"""

    @classmethod
    def get_comparison_prompt(cls, query: str, companies: List[str], is_quarterly_comparison: bool, 
                            needs_q4_calculation: bool) -> str:
        """Generate comparison analysis prompt"""
        
        q4_instructions = cls.Q4_CALCULATION_INSTRUCTIONS if needs_q4_calculation else ""
        companies_set = set(companies)
        
        if is_quarterly_comparison:
            return f"""
You are creating a quarterly comparative analysis for: {query}

{cls.FORMATTING_REQUIREMENTS}
- Show trends and growth patterns

{q4_instructions}

{cls.DATA_SOURCE_INSTRUCTIONS}

STRUCTURE - QUARTERLY COMPARATIVE ANALYSIS:
Use QUARTERLY_TREND_TEMPLATES for sophisticated quarterly analysis:

## Quarterly Performance Comparison

{cls.QUARTERLY_TREND_TEMPLATES}

{cls.BANKING_TABLE_EXAMPLES}

## Investment Banking Quarterly Insights
- Seasonality patterns and business cycle analysis
- Growth momentum and trend sustainability  
- Performance drivers and operational efficiency
- Quarterly volatility and risk assessment

At the end, list ONLY the chunk IDs that you actually referenced:
Used Chunks: [list chunk IDs]

{cls.OUTPUT_FORMAT_COMPARISON}
"""
        else:
            return f"""
You are creating a side-by-side comparative analysis for: {query}

Companies involved: {', '.join(companies_set)}

{cls.FORMATTING_REQUIREMENTS}

{q4_instructions}

{cls.DATA_SOURCE_INSTRUCTIONS}

STRUCTURE - SIDE-BY-SIDE COMPETITIVE ANALYSIS:
Use COMPARATIVE_ANALYSIS_TEMPLATES and BANKING_TABLE_EXAMPLES for investment banking quality analysis:

## Side-by-Side Financial Comparison
**{', '.join(companies_set)} - Comprehensive Performance Analysis**

{cls.COMPARATIVE_ANALYSIS_TEMPLATES}

{cls.BANKING_TABLE_EXAMPLES}

## Investment Banking Key Insights
- Competitive positioning and market share analysis
- Financial performance and operational efficiency comparison
- Risk profile and capital strength assessment
- Strategic outlook and investment recommendations

At the end, list ONLY the chunk IDs that you actually referenced:
Used Chunks: [list chunk IDs]

{cls.OUTPUT_FORMAT_COMPARISON}
"""

    @classmethod
    def get_analysis_prompt(cls, query: str, companies: List[str], is_multi_company: bool, 
                          is_quarterly_comparison: bool, needs_q4_calculation: bool) -> str:
        """Generate general analysis prompt"""
        
        q4_instructions = cls.Q4_CALCULATION_INSTRUCTIONS if needs_q4_calculation else ""
        
        if is_multi_company:
            return f"""
You are analyzing financial data for multiple companies: {query}

Companies: {', '.join(set(companies))}

{cls.FORMATTING_REQUIREMENTS}

{q4_instructions}

{cls.DATA_SOURCE_INSTRUCTIONS}

At the end, list ONLY the chunk IDs that you actually referenced:
Used Chunks: [list chunk IDs]

{cls.OUTPUT_FORMAT_MULTI_COMPANY_ANALYSIS}
"""
        elif is_quarterly_comparison:
            return f"""
You are analyzing quarterly financial performance for: {query}

{cls.FORMATTING_REQUIREMENTS}
- Show trends and growth patterns

{q4_instructions}

{cls.DATA_SOURCE_INSTRUCTIONS}

At the end, list ONLY the chunk IDs that you actually referenced:
Used Chunks: [list chunk IDs]

Present quarterly analysis with data tables in clean markdown format. NO code blocks.
"""
        else:
            return f"""
You are analyzing financial data for: {query}

{cls.FORMATTING_REQUIREMENTS}

{q4_instructions}

{cls.DATA_SOURCE_INSTRUCTIONS}

At the end, list ONLY the chunk IDs that you actually referenced:
Used Chunks: [list chunk IDs]

Present financial analysis with supporting data in clean markdown format. NO code blocks.
"""

    # ═══════════════════════════════════════════════════════════════════════
    # QUARTERLY ENHANCEMENT INSTRUCTIONS - For Query Planning
    # ═══════════════════════════════════════════════════════════════════════
    
    QUARTERLY_ENHANCEMENT_INSTRUCTIONS = """

IMPORTANT: For quarterly requests, include BOTH quarterly AND annual queries for Q4 calculation:
- Add quarterly queries for Q1, Q2, Q3 data
- Add annual queries for the same companies and statement types
- The annual data will be used to calculate Q4 = Annual - Q3"""

    # ═══════════════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ═══════════════════════════════════════════════════════════════════════
    
    @classmethod
    def get_prompt_for_intent(cls, intent: str, query: str, companies: List[str], 
                            is_multi_company: bool, is_quarterly_comparison: bool, 
                            is_side_by_side: bool, needs_q4_calculation: bool) -> str:
        """
        Main method to get appropriate prompt based on intent and context
        
        Args:
            intent: "statement", "comparison", or "analysis"
            query: Original user query
            companies: List of company tickers
            is_multi_company: Whether multiple companies are involved
            is_quarterly_comparison: Whether quarterly data is requested
            is_side_by_side: Whether side-by-side comparison is requested
            needs_q4_calculation: Whether Q4 calculation is needed
        """
        
        # Override intent for side-by-side requests
        if intent == "statement" or (is_side_by_side and is_multi_company):
            return cls.get_statement_prompt(query, companies, is_multi_company, 
                                          is_quarterly_comparison, is_side_by_side, 
                                          needs_q4_calculation)
        
        elif intent == "comparison" or is_side_by_side:
            return cls.get_comparison_prompt(query, companies, is_quarterly_comparison, 
                                           needs_q4_calculation)
        
        else:  # intent == "analysis" or default
            return cls.get_analysis_prompt(query, companies, is_multi_company, 
                                         is_quarterly_comparison, needs_q4_calculation)

    @classmethod
    def get_parsing_user_prompt(cls, user_query: str, bank_tickers: List[str], 
                              is_quarterly_request: bool) -> str:
        """Generate user prompt for Claude parsing"""
        
        quarterly_instruction = cls.QUARTERLY_ENHANCEMENT_INSTRUCTIONS if is_quarterly_request else ""
        
        return f"""Query: "{user_query}"

Available bank tickers: {bank_tickers}

{quarterly_instruction}

Create QueryPlan following system parsing rules."""

# ═══════════════════════════════════════════════════════════════════════
# CONVENIENCE INSTANCE FOR EASY IMPORTING
# ═══════════════════════════════════════════════════════════════════════

prompts = PromptLibrary() 