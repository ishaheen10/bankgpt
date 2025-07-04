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
    
    EQUITY_RESEARCH_ANALYST_FRAMING = """You are a top tier equity research analyst focused on analyzing banks. You have a deep expertise in extracting meaningful ratios and benchmarks from data. Your client sent you this question: {query}

Respond to their query while keeping in mind:"""

    FORMATTING_REQUIREMENTS = """CRITICAL FORMATTING REQUIREMENTS:
- Output clean markdown tables directly (NO code blocks or ``` markers)
- Use proper markdown table syntax with | separators
- Format numbers with commas for readability (e.g., 1,234,567)
- Present all financial data in PKR MM (millions) unless it's a ratio or percentage
- Always include currency unit and statement type headers like a financial analyst:
  **Balance Sheet as at [Date]**
  *(All amounts in PKR MM unless otherwise specified)*
- Convert all financial figures to PKR MM format for consistency
- Ratios and percentages should remain as calculated (no unit conversion needed)
- Use PKR MM as the standard unit for all monetary values"""

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
- All analysis must be traceable back to specific information in the retrieved chunks

CURRENCY FORMAT REQUIREMENTS:
- Convert all financial figures to PKR MM (millions) for consistency
- Extract the raw numbers from source documents and convert to PKR MM format
- Use PKR MM as the standard unit for all monetary values in tables and analysis
- Ratios and percentages should remain as calculated (no unit conversion needed)
- Always specify "PKR MM" in table headers and descriptions"""

    CHUNK_TRACKING_INSTRUCTIONS = """At the end, list ONLY the chunk IDs that you actually referenced in creating this analysis.
Used Chunks: [list only the chunk IDs/numbers that were actually used]"""

    RATIO_ANALYSIS_GUIDANCE = """BANKING RATIO ANALYSIS GUIDANCE:
- When ratios are explicitly requested, identify and calculate the most relevant banking ratios based on available data
- Focus on ratios that top-tier investment banking analysts would pay attention to for bank analysis, including but not limited to:
  * Profitability: ROE, ROA, Net Interest Margin, Cost-to-Income Ratio
  * Asset Quality: NPL Ratio, Provision Coverage Ratio, Asset Quality Ratio
  * Liquidity: Advance-to-Deposit Ratio, Liquid Assets Ratio, Loan-to-Deposit Ratio
  * Capital Strength: Capital Adequacy Ratio, Tier 1 Capital Ratio, Leverage Ratio
  * Efficiency: Operating Efficiency, Asset Utilization, Revenue per Employee
- Focus on ratios where you have complete data and that provide meaningful insights for the specific query
- Show calculation method: "Ratio = Numerator / Denominator" for each ratio you calculate
- If certain ratios cannot be calculated due to missing data, focus on what can be meaningfully analyzed
- Structure your analysis based on what data is actually available rather than following rigid templates
- Prioritize ratios that are most relevant to the user's specific query focus (e.g., efficiency, profitability, asset quality)"""

    OUTPUT_FORMAT_STATEMENT = """Present ONLY the financial statement data in clean markdown tables. NO explanatory text, NO code blocks, just the data tables."""

    CHAIN_OF_THOUGHT_INSTRUCTIONS = """CRITICAL: Follow this structured thinking process step-by-step. Show your reasoning explicitly:

## STEP 1: CONTEXT ANALYSIS & REASONING
**Let me analyze the provided financial data context:**

**Companies Identified:** [List companies found in context]
**Time Periods Available:** [List periods found in context]
**Statement Types:** [List statement types found in context]
**Currency Format:** [Note the currency format used]
**Data Completeness Assessment:** [Note what data is complete vs. missing]
**Calculable Ratios:** [List ratios that can be calculated with available data]

**Key Observations:**
- [Observation 1 about data quality/availability]
- [Observation 2 about trends/patterns]
- [Observation 3 about limitations]

## STEP 2: REPORT STRUCTURE PLANNING
**Based on my analysis, I will structure the report as follows:**

**Executive Summary:** [Brief overview of key findings]
**Financial Performance Overview:** [Main metrics and trends]
**Ratio Analysis:** [If applicable - which ratios to include]
**Comparative Analysis:** [If multiple companies - comparison approach]
**Investment Insights:** [Key takeaways for investors]
**Risk Assessment:** [Risk factors and considerations]

## STEP 3: SYSTEMATIC SECTION DEVELOPMENT
**Now I will develop each section systematically:**

[Proceed to write each section following the planned structure]

## STEP 4: QUALITY VERIFICATION
**Before finalizing, I verify:**
- ✅ All data sourced from provided context only
- ✅ Proper currency formatting maintained
- ✅ Ratios calculated correctly
- ✅ Professional investment banking tone achieved

**Final Report Structure:**
[Present the complete report with all sections]"""

    REPORT_STRUCTURE_TEMPLATE = """REPORT STRUCTURE REQUIREMENTS:

After the Executive Summary, describe how you will structure the report:

**This report is divided into:**

**Section 1: [Title based on your analysis focus]**
- [Brief description of what this section will cover]

**Section 2: [Title based on your analysis focus]**
- [Brief description of what this section will cover]

**Section 3: [Title based on your analysis focus]**
- [Brief description of what this section will cover]

[Continue with additional sections as needed based on the analysis requirements]

**Key areas to consider including in your sections:**
- Financial performance metrics and trends
- Balance sheet health and strength assessment
- Sector exposure and geographic breakdown
- One-time costs and exceptional items
- Banking ratios and efficiency metrics
- Risk assessment and capital adequacy
- Comparative analysis (if multiple companies)
- Investment insights and strategic implications

Let the analysis requirements guide your section structure, but always provide this upfront overview."""

    ENHANCED_REASONING_FRAMEWORK = """ADVANCED REASONING APPROACH - Use this for complex analysis:

**REASONING PROCESS:**
1. **Data Comprehension:** First, thoroughly understand what financial data is available
2. **Pattern Recognition:** Identify trends, anomalies, and relationships in the data
3. **Hypothesis Formation:** Develop hypotheses about performance drivers and risks
4. **Evidence Evaluation:** Test hypotheses against the available data
5. **Conclusion Drawing:** Form evidence-based conclusions and recommendations

**ANALYTICAL THINKING:**
- **Comparative Analysis:** When comparing companies, identify key differentiators
- **Trend Analysis:** Look for patterns over time periods
- **Risk Assessment:** Evaluate both quantitative and qualitative risk factors
- **Strategic Implications:** Consider what the data means for investment decisions

**QUALITY CHECKS:**
- **Data Integrity:** Ensure all numbers are accurately extracted from context
- **Logical Consistency:** Verify that conclusions follow from the data
- **Professional Standards:** Maintain investment banking level analysis quality
- **Context Grounding:** All insights must be traceable to provided data"""

    OUTPUT_FORMAT_ANALYSIS = """Present financial data in clean markdown tables WITH comprehensive analysis text. Use a combination of tables, bullet points, and paragraphs the way a top-tier investment banking analyst would prepare a high-quality equity research report. 

{cls.RATIO_ANALYSIS_GUIDANCE}

{cls.REPORT_STRUCTURE_TEMPLATE}

{cls.CHAIN_OF_THOUGHT_INSTRUCTIONS}

ONLY include banking ratios and metrics that are explicitly available in the retrieved chunks. Base all insights and trend analysis strictly on data present in the provided context. NO code blocks."""

    OUTPUT_FORMAT_MULTI_COMPANY_ANALYSIS = """Present comprehensive multi-company analysis with supporting data tables and detailed insights in clean markdown format. Use a combination of tables, bullet points, and paragraphs the way a top-tier investment banking analyst would prepare a high-quality equity research report. 

{cls.RATIO_ANALYSIS_GUIDANCE}

{cls.REPORT_STRUCTURE_TEMPLATE}

{cls.CHAIN_OF_THOUGHT_INSTRUCTIONS}

ONLY include banking ratios and metrics that are explicitly available in the retrieved chunks. Base all trend analysis, observations, and strategic implications strictly on data present in the provided context. NO code blocks."""

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
FLEXIBLE BANKING ANALYSIS TABLES:

Create tables that effectively present the available data. Use the most appropriate format based on what data you have and what insights it provides. Examples of table structures:

**Key Financial Metrics:**
| Line Item | Current | Previous | YoY Growth |
|-----------|---------|----------|------------|
| [Use actual line items from your data] | [Value] | [Value] | [%] |

**Performance Ratios:**
| Ratio | Current | Previous | Trend | Calculation |
|-------|---------|----------|-------|-------------|
| [Calculate ratios based on available data] | [Value] | [Value] | [↗/↘] | [Formula] |

**Comparative Analysis:**
| Bank | [Metric 1] | [Metric 2] | [Metric 3] |
|------|------------|------------|------------|
| [Bank A] | [Value] | [Value] | [Value] |
| [Bank B] | [Value] | [Value] | [Value] |

Focus on presenting the most relevant data in the most effective format. Adapt table structures based on what data is actually available and what insights it provides."""

    QUARTERLY_TREND_TEMPLATES = """
FLEXIBLE QUARTERLY ANALYSIS:

Create quarterly analysis tables based on the available data. Focus on the most relevant metrics for the specific analysis:

**Quarterly Performance Tracking:**
| Metric | Q1 | Q2 | Q3 | Q4* | Trend | Growth |
|--------|----|----|----|----|-------|--------|
| [Use actual metrics from your data] | [Value] | [Value] | [Value] | [Value] | [↗/↘] | [%] |

*Q4 = Calculated (Annual - Q3) where applicable*

**Seasonal Patterns (if relevant data available):**
| Business Line | Q1 | Q2 | Q3 | Q4 | Peak Quarter |
|---------------|----|----|----|----|--------------|
| [Use actual business lines from your data] | [Value] | [Value] | [Value] | [Value] | [Quarter] |

Focus on presenting the most meaningful quarterly trends based on available data rather than forcing specific metrics."""

    COMPARATIVE_ANALYSIS_TEMPLATES = """
FLEXIBLE MULTI-BANK COMPETITIVE ANALYSIS:

Create comparative analysis tables based on the available data. Focus on the most relevant metrics for the specific analysis:

**Peer Comparison Matrix:**
| Bank | [Key Metric 1] | [Key Metric 2] | [Key Metric 3] | [Key Metric 4] |
|------|----------------|----------------|----------------|----------------|
| [Bank A] | [Value] | [Value] | [Value] | [Value] |
| [Bank B] | [Value] | [Value] | [Value] | [Value] |

*Include only metrics where you have complete data for meaningful comparison*

**Performance Ranking:**
| Metric | Best Performer | 2nd Best | Key Insight |
|--------|----------------|----------|-------------|
| [Metric 1] | [Bank] ([Value]) | [Bank] ([Value]) | [Brief insight] |
| [Metric 2] | [Bank] ([Value]) | [Bank] ([Value]) | [Brief insight] |

Focus on presenting the most meaningful comparisons based on available data rather than forcing specific metrics."""

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
7. **Broad Analysis Expansion**: For broad analysis queries (ratios, performance, analysis), automatically include key statement types

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
- "analysis": Insights and trends requests, multi-entity/multi-company queries, or when "research" keyword appears, or fallback when not statement

INTENT PRIORITY RULES:
- If query mentions specific statements (balance sheet, profit and loss, cash flow) → Use "statement" intent unless explicitly asking for analysis
- If query mentions more than one ticker/company → Use "analysis" intent
- If query contains "research" keyword → Use "analysis" intent
- If intent doesn't fall into statement → Use "analysis" intent

BROAD ANALYSIS QUERY EXPANSION RULES:
- For broad analysis queries (ratios, performance, financial health, comparison), automatically include key statement types
- Key statement types for comprehensive analysis: balance_sheet, profit_and_loss, cash_flow
- For ratio analysis: Include balance sheet (asset/liability ratios), profit & loss (profitability ratios), and cash flow (liquidity ratios)
- For performance analysis: Include profit & loss (income/expense), balance sheet (asset utilization), and cash flow (cash generation)
- For financial health: Include balance sheet (solvency), profit & loss (profitability), and cash flow (liquidity)
- For comprehensive analysis: Also include sector exposure data
- For multi-company comparisons: Generate separate queries for each company with each statement type and exposure data

BROAD ANALYSIS TRIGGER KEYWORDS:
- "ratios", "ratio", "performance", "financial health", "financial performance"
- "key performance indicators", "KPIs", "metrics", "analysis", "compare"
- "how they did", "performance analysis", "financial analysis"
- "set of ratios", "financial ratios", "banking ratios"
- "comprehensive analysis", "full analysis", "complete analysis"

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
→ Intent: "analysis"

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
→ Creates: 4 queries (2 companies × 2 period sets × 1 statement), intent: "analysis"

Query: "HBL and UBL 2024 balance sheet and profit and loss"
→ Creates: 4 queries (2 companies × 1 period set × 2 statements), intent: "analysis"

Query: "HBL Q1 2024 and Q2 2024 balance sheet and cash flow"
→ Creates: 4 queries (1 company × 2 period sets × 2 statements), intent: "analysis"

**LEVEL 4: FULL COMPLEXITY (2×2×2 = 8 queries)**
Query: "HBL and UBL Q1 2024 and Q2 2024 balance sheet and profit and loss"
→ Creates: 8 queries (2 companies × 2 period sets × 2 statements), intent: "analysis"

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
→ Intent: "analysis"


Query: "HBL, UBL, and MCB Q1 2024 balance sheet and cash flow with notes"
→ Creates: 12 queries (3 companies × 1 period set × 2 statements = 6 + 6 note queries), intent: "analysis"

Query: "HBL sector exposure 2024"
→ Creates: 1 query (search_query: "HBL sector exposure 2024", metadata_filters: {ticker: "HBL", filing_type: "annual", filing_period: ["2024", "2023"]}), intent: "analysis"

Query: "UBL and MCB geographic breakdown Q1 2024"
→ Creates: 2 queries (search_query: "UBL geographic breakdown Q1 2024", metadata_filters: {ticker: "UBL", filing_type: "quarterly", filing_period: ["Q1-2024", "Q1-2023"]}), intent: "analysis"

**LEVEL 7: BROAD ANALYSIS QUERY EXPANSION**

Query: "Get me a set of ratios for FABL and MEBL in 2024"
→ Creates: 8 queries (2 companies × 3 statement types + 2 exposure queries):
  **Statement queries (is_statement = "yes"):**
  - (search_query: "FABL balance sheet 2024", metadata_filters: {is_statement: "yes", statement_type: "balance_sheet", filing_type: "annual", filing_period: ["2024", "2023"]})
  - (search_query: "FABL profit and loss 2024", metadata_filters: {is_statement: "yes", statement_type: "profit_and_loss", filing_type: "annual", filing_period: ["2024", "2023"]})
  - (search_query: "FABL cash flow 2024", metadata_filters: {is_statement: "yes", statement_type: "cash_flow", filing_type: "annual", filing_period: ["2024", "2023"]})
  - (search_query: "MEBL balance sheet 2024", metadata_filters: {is_statement: "yes", statement_type: "balance_sheet", filing_type: "annual", filing_period: ["2024", "2023"]})
  - (search_query: "MEBL profit and loss 2024", metadata_filters: {is_statement: "yes", statement_type: "profit_and_loss", filing_type: "annual", filing_period: ["2024", "2023"]})
  - (search_query: "MEBL cash flow 2024", metadata_filters: {is_statement: "yes", statement_type: "cash_flow", filing_type: "annual", filing_period: ["2024", "2023"]})
  **Exposure queries (no metadata filters):**
  - (search_query: "FABL sector exposure 2024", metadata_filters: {ticker: "FABL", filing_type: "annual", filing_period: ["2024", "2023"]})
  - (search_query: "MEBL sector exposure 2024", metadata_filters: {ticker: "MEBL", filing_type: "annual", filing_period: ["2024", "2023"]})
→ Intent: "analysis"

Query: "Analyze HBL performance over the last 4 years"
→ Creates: 6 queries (1 company × 3 statement types × 2 period sets):
  **Statement queries (is_statement = "yes"):**
  - (search_query: "HBL balance sheet 2024", metadata_filters: {is_statement: "yes", statement_type: "balance_sheet", filing_type: "annual", filing_period: ["2024", "2023"]})
  - (search_query: "HBL profit and loss 2024", metadata_filters: {is_statement: "yes", statement_type: "profit_and_loss", filing_type: "annual", filing_period: ["2024", "2023"]})
  - (search_query: "HBL cash flow 2024", metadata_filters: {is_statement: "yes", statement_type: "cash_flow", filing_type: "annual", filing_period: ["2024", "2023"]})
  - (search_query: "HBL balance sheet 2022", metadata_filters: {is_statement: "yes", statement_type: "balance_sheet", filing_type: "annual", filing_period: ["2022", "2021"]})
  - (search_query: "HBL profit and loss 2022", metadata_filters: {is_statement: "yes", statement_type: "profit_and_loss", filing_type: "annual", filing_period: ["2022", "2021"]})
  - (search_query: "HBL cash flow 2022", metadata_filters: {is_statement: "yes", statement_type: "cash_flow", filing_type: "annual", filing_period: ["2022", "2021"]})
→ Intent: "analysis"

Query: "Compare UBL performance in 2024 and 2022"
→ Creates: 6 queries (1 company × 3 statement types × 2 period sets):
  **Statement queries (is_statement = "yes"):**
  - (search_query: "UBL balance sheet 2024", metadata_filters: {is_statement: "yes", statement_type: "balance_sheet", filing_type: "annual", filing_period: ["2024", "2023"]})
  - (search_query: "UBL profit and loss 2024", metadata_filters: {is_statement: "yes", statement_type: "profit_and_loss", filing_type: "annual", filing_period: ["2024", "2023"]})
  - (search_query: "UBL cash flow 2024", metadata_filters: {is_statement: "yes", statement_type: "cash_flow", filing_type: "annual", filing_period: ["2024", "2023"]})
  - (search_query: "UBL balance sheet 2022", metadata_filters: {is_statement: "yes", statement_type: "balance_sheet", filing_type: "annual", filing_period: ["2022", "2021"]})
  - (search_query: "UBL profit and loss 2022", metadata_filters: {is_statement: "yes", statement_type: "profit_and_loss", filing_type: "annual", filing_period: ["2022", "2021"]})
  - (search_query: "UBL cash flow 2022", metadata_filters: {is_statement: "yes", statement_type: "cash_flow", filing_type: "annual", filing_period: ["2022", "2021"]})
→ Intent: "analysis"

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
                           needs_q4_calculation: bool, financial_statement_scope: str = None) -> str:
        """Generate statement analysis prompt based on context"""
        
        # Determine scope label
        scope_label = financial_statement_scope if financial_statement_scope else "unconsolidated"
        if scope_label == "consolidated":
            scope_display = "Consolidated"
        elif scope_label == "unconsolidated":
            scope_display = "Unconsolidated"
        else:
            scope_display = "Unconsolidated"  # Default
        
        q4_instructions = cls.Q4_CALCULATION_INSTRUCTIONS if needs_q4_calculation else ""
        
        # Multi-company side-by-side comparison
        if is_multi_company and not is_quarterly_comparison:
            companies_set = set(companies)
            
            # Check if this is actually a quarterly request based on query content
            is_quarterly_in_query = any(q_term in query.lower() for q_term in ["quarterly", "quarter", "q1", "q2", "q3", "q4"])
            
            if is_quarterly_in_query:
                # This is a multi-company quarterly request
                return f"""
{cls.EQUITY_RESEARCH_ANALYST_FRAMING.format(query=query)}

{cls.FORMATTING_REQUIREMENTS}

{q4_instructions}

{cls.QUARTERLY_DATA_PRIORITY}

REQUIRED STRUCTURE - MULTI-COMPANY QUARTERLY ANALYSIS:
Use the templates below to create compelling tables that show:

## {', '.join(companies_set)} - Quarterly Performance Analysis ({scope_display})
**Quarterly Statement Analysis**
*(All amounts in PKR MM unless otherwise specified)*

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

and using ONLY the following context which was retrieved from financial reports:

[chunks]
"""
            else:
                # Regular multi-company annual comparison
                return f"""
{cls.EQUITY_RESEARCH_ANALYST_FRAMING.format(query=query)}

{cls.FORMATTING_REQUIREMENTS}

{q4_instructions}

REQUIRED STRUCTURE - COMPREHENSIVE BANKING COMPARISON:
Use BANKING_TABLE_EXAMPLES and COMPARATIVE_ANALYSIS_TEMPLATES to create professional analysis:

## {', '.join(companies_set)} - Comprehensive Financial Analysis ({scope_display})
**Statement Analysis for the periods shown in the data**
*(All amounts in PKR MM unless otherwise specified)*

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

and using ONLY the following context which was retrieved from financial reports:

[chunks]
"""
        
        # Quarterly comparison for single company
        elif is_quarterly_comparison and not is_multi_company:
            return f"""
{cls.EQUITY_RESEARCH_ANALYST_FRAMING.format(query=query)}

{cls.FORMATTING_REQUIREMENTS}

{q4_instructions}

{cls.DATA_SOURCE_INSTRUCTIONS}

STRUCTURE - QUARTERLY PERFORMANCE ANALYSIS:
Use QUARTERLY_TREND_TEMPLATES and BANKING_TABLE_EXAMPLES for comprehensive analysis:

## {companies[0] if companies else 'Company'} - Quarterly Performance Deep-Dive ({scope_display})
**Quarterly Statement of Financial Position**
*(All amounts in PKR MM unless otherwise specified)*

{cls.QUARTERLY_TREND_TEMPLATES}

{cls.BANKING_TABLE_EXAMPLES}

At the end, list ONLY the chunk IDs that you actually referenced:
Used Chunks: [list chunk IDs]

{cls.OUTPUT_FORMAT_STATEMENT}

and using ONLY the following context which was retrieved from financial reports:

[chunks]
"""
        
        # Multi-company quarterly comparison
        elif is_multi_company:
            return f"""
{cls.EQUITY_RESEARCH_ANALYST_FRAMING.format(query=query)}

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

and using ONLY the following context which was retrieved from financial reports:

[chunks]
"""
        
        # Single company statement
        else:
            return f"""
{cls.EQUITY_RESEARCH_ANALYST_FRAMING.format(query=query)}

{cls.FORMATTING_REQUIREMENTS}

{q4_instructions}

{cls.DATA_SOURCE_INSTRUCTIONS}

At the end, list ONLY the chunk IDs that you actually referenced:
Used Chunks: [list chunk IDs]

Present the financial statement data in clean markdown table format. NO code blocks.

and using ONLY the following context which was retrieved from financial reports:

[chunks]
"""

    @classmethod
    def get_analysis_prompt(cls, query: str, companies: List[str], is_multi_company: bool, 
                          is_quarterly_comparison: bool, needs_q4_calculation: bool, 
                          financial_statement_scope: str = None) -> str:
        """Generate comprehensive analysis prompt for all non-statement requests"""
        
        # Determine scope label
        scope_label = financial_statement_scope if financial_statement_scope else "unconsolidated"
        if scope_label == "consolidated":
            scope_display = "Consolidated"
        elif scope_label == "unconsolidated":
            scope_display = "Unconsolidated"
        else:
            scope_display = "Unconsolidated"  # Default
        
        q4_instructions = cls.Q4_CALCULATION_INSTRUCTIONS if needs_q4_calculation else ""
        companies_set = set(companies)
        
        if is_quarterly_comparison:
            return f"""
{cls.EQUITY_RESEARCH_ANALYST_FRAMING.format(query=query)}

{cls.FORMATTING_REQUIREMENTS}
- Show trends and growth patterns

{q4_instructions}

{cls.DATA_SOURCE_INSTRUCTIONS}

{cls.ENHANCED_REASONING_FRAMEWORK}

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

{cls.OUTPUT_FORMAT_ANALYSIS}

and using ONLY the following context which was retrieved from financial reports:

[chunks]
"""
        elif is_multi_company:
            return f"""
{cls.EQUITY_RESEARCH_ANALYST_FRAMING.format(query=query)}

Companies involved: {', '.join(companies_set)}

{cls.FORMATTING_REQUIREMENTS}

{q4_instructions}

{cls.DATA_SOURCE_INSTRUCTIONS}

{cls.ENHANCED_REASONING_FRAMEWORK}

STRUCTURE - COMPREHENSIVE MULTI-COMPANY ANALYSIS:
Use COMPARATIVE_ANALYSIS_TEMPLATES and BANKING_TABLE_EXAMPLES for investment banking quality analysis:

## Multi-Company Financial Analysis
**{', '.join(companies_set)} - Comprehensive Performance Analysis ({scope_display})**

{cls.COMPARATIVE_ANALYSIS_TEMPLATES}

{cls.BANKING_TABLE_EXAMPLES}

## Investment Banking Key Insights
- Competitive positioning and market share analysis
- Financial performance and operational efficiency comparison
- Risk profile and capital strength assessment
- Strategic outlook and investment recommendations

## Banking Ratio Analysis Approach
{cls.RATIO_ANALYSIS_GUIDANCE}

At the end, list ONLY the chunk IDs that you actually referenced:
Used Chunks: [list chunk IDs]

{cls.OUTPUT_FORMAT_ANALYSIS}

and using ONLY the following context which was retrieved from financial reports:

[chunks]
"""
        else:
            return f"""
{cls.EQUITY_RESEARCH_ANALYST_FRAMING.format(query=query)}

{cls.FORMATTING_REQUIREMENTS}

{q4_instructions}

{cls.DATA_SOURCE_INSTRUCTIONS}

STRUCTURE - COMPREHENSIVE FINANCIAL ANALYSIS:
Use BANKING_TABLE_EXAMPLES for professional analysis:

## Financial Analysis

{cls.BANKING_TABLE_EXAMPLES}

## Investment Banking Insights
- Financial performance drivers and trends
- Operational efficiency and risk assessment
- Strategic implications and outlook

At the end, list ONLY the chunk IDs that you actually referenced:
Used Chunks: [list chunk IDs]

{cls.OUTPUT_FORMAT_ANALYSIS}

and using ONLY the following context which was retrieved from financial reports:

[chunks]
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
                            is_side_by_side: bool, needs_q4_calculation: bool, 
                            financial_statement_scope: str = None) -> str:
        """
        Main method to get appropriate prompt based on intent and context
        
        Args:
            intent: "statement", "analysis"
            query: Original user query
            companies: List of company tickers
            is_multi_company: Whether multiple companies are involved
            is_quarterly_comparison: Whether quarterly data is requested
            is_side_by_side: Whether this is a statement request (simplified logic)
            needs_q4_calculation: Whether Q4 calculation is needed
            financial_statement_scope: "consolidated", "unconsolidated", or None (defaults to "unconsolidated")
        """
        
        # Simplified routing logic: Check if this is a pure statement request
        is_statement_request = any(stmt_term in query.lower() for stmt_term in [
            "statement", "balance sheet", "profit and loss", "cash flow", 
            "income statement", "financial statement", "p&l", "p & l"
        ])
        
        if is_statement_request:
            prompt = cls.get_statement_prompt(query, companies, is_multi_company, 
                                          is_quarterly_comparison, is_side_by_side, 
                                          needs_q4_calculation, financial_statement_scope)
        else:
            # Everything else gets comprehensive analysis (including ratios)
            prompt = cls.get_analysis_prompt(query, companies, is_multi_company, 
                                         is_quarterly_comparison, needs_q4_calculation, 
                                         financial_statement_scope)
        
        # Format the placeholders in the prompt
        prompt = prompt.format(
            cls=cls,
            RATIO_ANALYSIS_GUIDANCE=cls.RATIO_ANALYSIS_GUIDANCE,
            REPORT_STRUCTURE_TEMPLATE=cls.REPORT_STRUCTURE_TEMPLATE,
            CHAIN_OF_THOUGHT_INSTRUCTIONS=cls.CHAIN_OF_THOUGHT_INSTRUCTIONS
        )
        
        return prompt

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