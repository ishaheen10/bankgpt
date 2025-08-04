#!/usr/bin/env python3
"""
Simplified DSPy Parsing System - Rewriting PARSING_SYSTEM_PROMPT
Using only Signature and ChainOfThought primitives
"""

import dspy
from typing import List, Dict, Any
import json


# ═══════════════════════════════════════════════════════════════════════
# CORE DSPy SIGNATURES - Breaking Down the Monolithic Prompt
# ═══════════════════════════════════════════════════════════════════════

class IntentClassificationSignature(dspy.Signature):
    """Classify user query intent as 'statement' or 'analysis' based on specific rules."""
    
    user_query: str = dspy.InputField(desc="Natural language financial query")
    conversation_context: str = dspy.InputField(desc="Previous conversation context for pronouns")
    
    # Core business logic from original prompt
    intent: str = dspy.OutputField(desc="'statement' for single company requesting specific statements (including historical), 'analysis' for multiple companies OR analysis keywords OR explicit analysis requests")
    reasoning: str = dspy.OutputField(desc="Explanation of why this intent was chosen based on company count and keywords")

class CompanyExtractionSignature(dspy.Signature):
    """Extract company tickers and resolve context references like 'them', 'their'."""
    
    user_query: str = dspy.InputField(desc="Natural language financial query")
    available_tickers: str = dspy.InputField(desc="Available PSX bank ticker symbols")
    conversation_context: str = dspy.InputField(desc="Previous conversation for resolving pronouns")
    
    companies: str = dspy.OutputField(desc="JSON list of PSX ticker symbols (HBL, UBL, etc.) extracted from query")
    context_resolved: str = dspy.OutputField(desc="Query with pronouns resolved to actual company names")

class PeriodStandardizationSignature(dspy.Signature):
    """Parse and standardize time periods into the exact format required by the system."""
    
    user_query: str = dspy.InputField(desc="Natural language financial query")
    
    # Business rules from original prompt
    period_sets: str = dspy.OutputField(desc="JSON list of standardized period sets: Annual ['2024', '2023'] or Quarterly ['Q1-2024', 'Q1-2023']")
    filing_type: str = dspy.OutputField(desc="'annual' or 'quarterly' based on detected periods")
    needs_q4_calculation: str = dspy.OutputField(desc="'true' if Q4 needs to be calculated from Annual - Q3")

class MetadataGenerationSignature(dspy.Signature):
    """Generate metadata filters for each query following the exact schema."""
    
    company: str = dspy.InputField(desc="Single company ticker")
    statement_type: str = dspy.InputField(desc="Statement type if specified")
    period_set: str = dspy.InputField(desc="Single period set like ['2024', '2023']")
    filing_type: str = dspy.InputField(desc="'annual' or 'quarterly'")
    intent: str = dspy.InputField(desc="'statement' or 'analysis'")
    is_notes_request: str = dspy.InputField(desc="'true' if notes are requested")
    
    # Exact metadata schema from original prompt
    metadata_filters: str = dspy.OutputField(desc="JSON metadata filters with ticker, statement_type, financial_statement_scope, filing_type, filing_period, is_statement, is_note, note_link fields")
    search_query: str = dspy.OutputField(desc="Human-readable search query: '[COMPANY] [STATEMENT_TYPE/ANALYSIS_TYPE] [PERIOD]'")

class CombinatorialQueryDecompositionSignature(dspy.Signature):
    """Apply the core combinatorial logic: companies × periods × statements = total queries."""
    
    companies: str = dspy.InputField(desc="JSON list of companies")
    period_sets: str = dspy.InputField(desc="JSON list of period sets")
    statement_types: str = dspy.InputField(desc="JSON list of statement types")
    intent: str = dspy.InputField(desc="'statement' or 'analysis'")
    user_query: str = dspy.InputField(desc="Original query for context")
    
    # Core combinatorial expansion from original prompt
    query_plan: str = dspy.OutputField(desc="JSON QueryPlan with companies[], intent, queries[] following exact combinatorial logic (2×2×2 = 8 queries pattern)")
    total_queries: int = dspy.OutputField(desc="Total number of queries generated (companies × periods × statements)")


# ═══════════════════════════════════════════════════════════════════════
# CHAINOFTHOUGHT MODULES - Implementing the Business Logic
# ═══════════════════════════════════════════════════════════════════════

class IntentClassifier(dspy.Module):
    """Implements intent classification logic from original prompt."""
    
    def __init__(self):
        super().__init__()
        self.classify = dspy.ChainOfThought(IntentClassificationSignature)
    
    def forward(self, user_query: str, conversation_context: str = ""):
        """
        Apply intent classification rules:
        - "statement": Single company requesting specific financial statement(s), including historical periods
        - "analysis": Multiple companies OR analysis keywords OR explicit analysis request
        """
        
        result = self.classify(
            user_query=user_query,
            conversation_context=conversation_context
        )
        
        return result

class CompanyExtractor(dspy.Module):
    """Extracts companies and resolves context references."""
    
    def __init__(self):
        super().__init__()
        self.extract = dspy.ChainOfThought(CompanyExtractionSignature)
    
    def forward(self, user_query: str, available_tickers: str, conversation_context: str = ""):
        """Extract PSX ticker symbols and resolve pronouns like 'them', 'their'."""
        
        result = self.extract(
            user_query=user_query,
            available_tickers=available_tickers,
            conversation_context=conversation_context
        )
        
        return result

class PeriodStandardizer(dspy.Module):
    """Standardizes periods into the exact format required."""
    
    def __init__(self):
        super().__init__()
        self.standardize = dspy.ChainOfThought(PeriodStandardizationSignature)
    
    def forward(self, user_query: str):
        """
        Parse periods and convert to standard format:
        - Annual: ["2024", "2023"] (always include previous year)
        - Quarterly: ["Q1-2024", "Q1-2023"] (always include previous year)
        """
        
        result = self.standardize(user_query=user_query)
        
        return result

class MetadataGenerator(dspy.Module):
    """Generates exact metadata schema for each query."""
    
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(MetadataGenerationSignature)
    
    def forward(self, company: str, statement_type: str, period_set: str, 
               filing_type: str, intent: str, is_notes_request: str = "false"):
        """
        Generate metadata following exact schema:
        - ticker, statement_type, financial_statement_scope, filing_type, filing_period
        - is_statement, is_note, note_link
        """
        
        result = self.generate(
            company=company,
            statement_type=statement_type,
            period_set=period_set,
            filing_type=filing_type,
            intent=intent,
            is_notes_request=is_notes_request
        )
        
        return result

class CombinatorialDecomposer(dspy.Module):
    """Implements the core combinatorial logic: companies × periods × statements."""
    
    def __init__(self):
        super().__init__()
        self.decompose = dspy.ChainOfThought(CombinatorialQueryDecompositionSignature)
    
    def forward(self, companies: List[str], period_sets: List[str], 
               statement_types: List[str], intent: str, user_query: str):
        """
        Apply combinatorial expansion:
        - Multiple companies/periods/statements = separate queries
        - Create all combinations (2×2×2 = 8 queries pattern)
        """
        
        result = self.decompose(
            companies=json.dumps(companies),
            period_sets=json.dumps(period_sets),
            statement_types=json.dumps(statement_types),
            intent=intent,
            user_query=user_query
        )
        
        return result


# ═══════════════════════════════════════════════════════════════════════
# MAIN PARSING SYSTEM - Composing All Components
# ═══════════════════════════════════════════════════════════════════════

class SimplifiedDSPyParsingSystem(dspy.Module):
    """
    Complete parsing system using only Signature + ChainOfThought.
    Replaces the 200+ line PARSING_SYSTEM_PROMPT with modular components.
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize all components
        self.intent_classifier = IntentClassifier()
        self.company_extractor = CompanyExtractor()
        self.period_standardizer = PeriodStandardizer()
        self.metadata_generator = MetadataGenerator()
        self.combinatorial_decomposer = CombinatorialDecomposer()
    
    def forward(self, user_query: str, available_tickers: List[str], 
               conversation_context: str = ""):
        """
        Main parsing pipeline:
        1. Classify intent (statement vs analysis)
        2. Extract companies and resolve context
        3. Standardize time periods
        4. Apply combinatorial decomposition
        5. Generate metadata for each query
        """
        
        # Step 1: Intent Classification
        intent_result = self.intent_classifier(
            user_query=user_query,
            conversation_context=conversation_context
        )
        
        # Step 2: Company Extraction
        company_result = self.company_extractor(
            user_query=user_query,
            available_tickers=str(available_tickers),
            conversation_context=conversation_context
        )
        
        # Step 3: Period Standardization
        period_result = self.period_standardizer(user_query=user_query)
        
        # Step 4: Determine statement types based on query
        statement_types = self._extract_statement_types(user_query, intent_result.intent)
        
        # Step 5: Combinatorial Decomposition
        companies = json.loads(company_result.companies)
        period_sets = json.loads(period_result.period_sets)
        
        final_result = self.combinatorial_decomposer(
            companies=companies,
            period_sets=period_sets,
            statement_types=statement_types,
            intent=intent_result.intent,
            user_query=user_query
        )
        
        return {
            'query_plan': json.loads(final_result.query_plan),
            'total_queries': final_result.total_queries,
            'intent': intent_result.intent,
            'companies': companies,
            'period_sets': period_sets,
            'statement_types': statement_types,
            'needs_q4_calculation': period_result.needs_q4_calculation == "true"
        }
    
    def _extract_statement_types(self, user_query: str, intent: str) -> List[str]:
        """Extract statement types from query or use defaults for analysis."""
        
        query_lower = user_query.lower()
        statement_types = []
        
        # Check for specific statement types
        if any(term in query_lower for term in ["balance sheet", "balance"]):
            statement_types.append("balance_sheet")
        if any(term in query_lower for term in ["profit and loss", "p&l", "income statement"]):
            statement_types.append("profit_and_loss")
        if any(term in query_lower for term in ["cash flow", "cashflow"]):
            statement_types.append("cash_flow")
        
        # Default for analysis intent
        if intent == "analysis" and not statement_types:
            statement_types = ["balance_sheet", "profit_and_loss", "cash_flow"]
        elif not statement_types:
            statement_types = ["balance_sheet"]  # Default for statement intent
        
        return statement_types


# ═══════════════════════════════════════════════════════════════════════
# DEMONSTRATION AND TESTING
# ═══════════════════════════════════════════════════════════════════════

def demonstrate_simplified_parsing():
    """Demonstrate the simplified DSPy parsing system."""
    
    print("🎯 Simplified DSPy Parsing System Demo")
    print("=" * 50)
    
    # Initialize the system
    parser = SimplifiedDSPyParsingSystem()
    
    # Test queries from the original prompt
    test_queries = [
        "HBL 2024 balance sheet",  # Simple statement
        "HBL and UBL 2024 balance sheet",  # Dual company
        "HBL 2024 balance sheet and profit and loss",  # Dual statement
        "HBL and UBL Q1-2024 and Q2-2024 balance sheet and profit and loss",  # Full complexity (2×2×2=8)
        "Compare UBL and HBL financial performance in 2023 vs 2022",  # Analysis
        "What are the banking ratios for all major banks?",  # Broad analysis
    ]
    
    available_tickers = ["HBL", "UBL", "MCB", "NBP", "BAFL"]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-" * 40)
        
        try:
            result = parser(
                user_query=query,
                available_tickers=available_tickers
            )
            
            print(f"🎯 Intent: {result['intent']}")
            print(f"🏢 Companies: {result['companies']}")
            print(f"📅 Period Sets: {result['period_sets']}")
            print(f"📊 Statement Types: {result['statement_types']}")
            print(f"🔢 Total Queries: {result['total_queries']}")
            print(f"📈 Needs Q4 Calc: {result['needs_q4_calculation']}")
            
            # Show first few queries as examples
            queries = result['query_plan']['queries'][:3]
            print(f"📋 Sample Queries:")
            for i, q in enumerate(queries, 1):
                print(f"  {i}. {q.get('search_query', 'N/A')}")
            
            if len(result['query_plan']['queries']) > 3:
                print(f"  ... and {len(result['query_plan']['queries']) - 3} more")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            print("🔄 This would use fallback logic in production")

if __name__ == "__main__":
    # Configure DSPy (would need real LLM in production)
    print("⚠️  Note: This demo requires DSPy configuration with an LLM")
    print("📝 Showing the structure that replaces the 200+ line PARSING_SYSTEM_PROMPT")
    print("\n🔧 DSPy Components Created:")
    print("✅ IntentClassificationSignature + ChainOfThought")
    print("✅ CompanyExtractionSignature + ChainOfThought") 
    print("✅ PeriodStandardizationSignature + ChainOfThought")
    print("✅ MetadataGenerationSignature + ChainOfThought")
    print("✅ CombinatorialQueryDecompositionSignature + ChainOfThought")
    print("\n💡 This modular approach replaces the monolithic prompt with:")
    print("• Testable components")
    print("• Reusable logic")
    print("• Clear separation of concerns") 
    print("• Automatic optimization via DSPy") 