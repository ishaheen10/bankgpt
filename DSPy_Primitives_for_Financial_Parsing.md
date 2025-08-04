# DSPy Primitives for Financial Query Parsing

## Understanding the DSPy Primitive Ecosystem

You've correctly identified that **Signatures** break down complex prompts into focused components. But DSPy offers several other primitives that can significantly enhance your financial parsing system. Let's explore them with your PSX banking data as examples.

## 1. ChainOfThought - Adding Reasoning to Financial Analysis

### What it does
Adds step-by-step reasoning to any Signature, making the LLM explain its thinking process.

### Perfect for Financial Parsing Because:
- Financial decisions need explainable reasoning
- Debugging becomes much easier when you see the reasoning
- Regulatory compliance often requires audit trails

### Your Current Signature (Basic):
```python
class IntentClassificationSignature(dspy.Signature):
    """Classify user query intent as 'statement' or 'analysis'."""
    
    user_query: str = dspy.InputField(desc="Natural language financial query")
    
    intent: str = dspy.OutputField(desc="'statement' or 'analysis'")
```

### Enhanced with ChainOfThought:
```python
class IntentClassifier(dspy.Module):
    def __init__(self):
        super().__init__()
        # ChainOfThought adds reasoning steps automatically
        self.classify = dspy.ChainOfThought(IntentClassificationSignature)
    
    def forward(self, user_query):
        result = self.classify(user_query=user_query)
        return result

# Example output:
# Query: "Compare HBL and UBL profitability trends"
# Reasoning: "This query mentions 'Compare' and involves two companies (HBL, UBL), 
#            plus requests analysis of 'profitability trends' rather than specific 
#            financial statements. This clearly indicates analysis intent."
# Intent: "analysis"
```

## 2. Assert - Financial Data Validation

### What it does
Adds validation constraints to ensure outputs meet specific requirements.

### Perfect for Financial Parsing Because:
- Financial data has strict format requirements
- Ticker symbols must be valid
- Period formats must be exact
- Metadata must follow schema

### Example with Your Parsing System:
```python
class ValidatedCompanyExtractor(dspy.Module):
    def __init__(self, valid_tickers):
        super().__init__()
        self.extract = dspy.ChainOfThought(CompanyExtractionSignature)
        self.valid_tickers = valid_tickers
    
    def forward(self, user_query, available_tickers):
        result = self.extract(
            user_query=user_query,
            available_tickers=available_tickers
        )
        
        companies = json.loads(result.companies)
        
        # Assert all extracted companies are valid PSX tickers
        dspy.Assert(
            all(ticker in self.valid_tickers for ticker in companies),
            f"All companies must be valid PSX tickers. Got: {companies}"
        )
        
        # Assert at least one company was found
        dspy.Assert(
            len(companies) > 0,
            "Must extract at least one company from the query"
        )
        
        return result

# If assertion fails, DSPy will automatically retry with feedback
```

## 3. Suggest - Multiple Financial Interpretations

### What it does
Generates multiple possible interpretations, useful for ambiguous queries.

### Perfect for Financial Parsing Because:
- Financial queries can be ambiguous ("HBL performance" - what kind?)
- Multiple valid period interpretations ("last quarter" - which quarter?)
- Different analysis approaches possible

### Example for Ambiguous Period Parsing:
```python
class PeriodSuggestionSignature(dspy.Signature):
    """Generate multiple valid period interpretations for ambiguous queries."""
    
    user_query: str = dspy.InputField(desc="Financial query with ambiguous periods")
    current_date: str = dspy.InputField(desc="Current date for context")
    
    period_options: str = dspy.OutputField(desc="JSON list of valid period interpretations")
    confidence_scores: str = dspy.OutputField(desc="Confidence score for each option")

class AmbiguousPeriodHandler(dspy.Module):
    def __init__(self):
        super().__init__()
        self.suggest = dspy.Suggest(PeriodSuggestionSignature)
    
    def forward(self, user_query):
        # Get multiple interpretations
        suggestions = self.suggest(
            user_query=user_query,
            current_date="2024-12-19"
        )
        
        return suggestions

# Example:
# Query: "HBL last quarter performance"
# Suggestions:
# [
#   {"period": ["Q3-2024", "Q3-2023"], "confidence": 0.8, "reasoning": "Most recent completed quarter"},
#   {"period": ["Q4-2024", "Q4-2023"], "confidence": 0.6, "reasoning": "Current quarter if available"},
#   {"period": ["Q2-2024", "Q2-2023"], "confidence": 0.3, "reasoning": "Previous quarter if Q3 not yet reported"}
# ]
```

## 4. Majority - Consensus for Complex Classifications

### What it does
Runs multiple attempts and takes the majority answer, improving reliability.

### Perfect for Financial Parsing Because:
- Intent classification can be tricky for borderline cases
- Financial analysis needs high accuracy
- Reduces impact of LLM inconsistency

### Example for Robust Intent Classification:
```python
class RobustIntentClassifier(dspy.Module):
    def __init__(self):
        super().__init__()
        # Run classification 5 times and take majority
        self.classify = dspy.Majority(
            dspy.ChainOfThought(IntentClassificationSignature),
            k=5  # Number of attempts
        )
    
    def forward(self, user_query):
        result = self.classify(user_query=user_query)
        return result

# Example for borderline case:
# Query: "HBL financial statements for 2023 and 2024"
# Attempt 1: "statement" (historical data request)
# Attempt 2: "analysis" (multiple periods)  
# Attempt 3: "statement" (specific statements)
# Attempt 4: "statement" (single company)
# Attempt 5: "statement" (explicit statement request)
# Majority Result: "statement" (4/5 votes)
```

## 5. Retrieve - Financial Knowledge Augmentation

### What it does
Adds retrieval capabilities to pull relevant information during processing.

### Perfect for Financial Parsing Because:
- Need to validate company information
- Retrieve current financial periods
- Look up banking regulations
- Get company metadata

### Example for Company Information Retrieval:
```python
class CompanyInfoRetriever(dspy.Module):
    def __init__(self, company_db):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=3)  # Retrieve top 3 matches
        self.extract = dspy.ChainOfThought(CompanyExtractionSignature)
        self.company_db = company_db
    
    def forward(self, user_query):
        # First, retrieve relevant company information
        company_context = self.retrieve(
            query=user_query,
            documents=self.company_db  # PSX company database
        )
        
        # Then extract companies with enriched context
        result = self.extract(
            user_query=user_query + f"\nCompany context: {company_context}"
        )
        
        return result

# Retrieves information like:
# "HBL: Habib Bank Limited, largest private bank in Pakistan, ticker: HBL"
# "UBL: United Bank Limited, major commercial bank, ticker: UBL"
```

## 6. Module - Orchestrating Your Financial Pipeline

### What it does
Composes multiple components into a cohesive system.

### Perfect for Financial Parsing Because:
- Your parsing has multiple steps that need coordination
- Components need to pass data between each other
- Error handling across the pipeline

### Your Complete Financial Parser as a Module:
```python
class FinancialQueryParser(dspy.Module):
    """Complete financial query parsing pipeline using multiple DSPy primitives."""
    
    def __init__(self, valid_tickers, company_db):
        super().__init__()
        
        # Robust intent classification with majority voting
        self.intent_classifier = dspy.Majority(
            dspy.ChainOfThought(IntentClassificationSignature),
            k=3
        )
        
        # Company extraction with validation
        self.company_extractor = ValidatedCompanyExtractor(valid_tickers)
        
        # Period parsing with ambiguity handling
        self.period_handler = AmbiguousPeriodHandler()
        
        # Metadata generation with reasoning
        self.metadata_generator = dspy.ChainOfThought(MetadataGenerationSignature)
        
        # Query decomposition with validation
        self.query_decomposer = dspy.ChainOfThought(CombinatorialQueryDecompositionSignature)
    
    def forward(self, user_query, available_tickers):
        # Step 1: Classify intent with majority consensus
        intent_result = self.intent_classifier(user_query=user_query)
        
        # Step 2: Extract companies with validation
        company_result = self.company_extractor(
            user_query=user_query,
            available_tickers=available_tickers
        )
        
        # Step 3: Handle periods (with ambiguity if needed)
        if self._is_ambiguous_period(user_query):
            period_suggestions = self.period_handler(user_query=user_query)
            # Take highest confidence option
            period_result = self._select_best_period(period_suggestions)
        else:
            period_result = self.period_standardizer(user_query=user_query)
        
        # Step 4: Generate final query plan
        final_result = self.query_decomposer(
            companies=company_result.companies,
            period_sets=period_result.period_sets,
            statement_types=self._extract_statement_types(user_query),
            intent=intent_result.intent,
            user_query=user_query
        )
        
        return {
            'intent': intent_result.intent,
            'reasoning': intent_result.reasoning,
            'companies': json.loads(company_result.companies),
            'query_plan': json.loads(final_result.query_plan),
            'confidence': self._calculate_overall_confidence(intent_result, company_result, final_result)
        }
```

## 7. ProgramOfThought - Financial Calculations

### What it does
Combines reasoning with code execution for computational tasks.

### Perfect for Financial Parsing Because:
- Q4 calculations: Q4 = Annual - Q3
- Period set validations
- Complex combinatorial logic

### Example for Q4 Calculation Logic:
```python
class Q4CalculationSignature(dspy.Signature):
    """Determine if Q4 calculation is needed and provide the logic."""
    
    requested_periods: str = dspy.InputField(desc="Periods requested in query")
    available_periods: str = dspy.InputField(desc="Available period data")
    
    needs_calculation: str = dspy.OutputField(desc="Whether Q4 calculation needed")
    calculation_code: str = dspy.OutputField(desc="Python code for calculation")

class Q4Calculator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.calculator = dspy.ProgramOfThought(Q4CalculationSignature)
    
    def forward(self, requested_periods, available_periods):
        result = self.calculator(
            requested_periods=requested_periods,
            available_periods=available_periods
        )
        
        # DSPy executes the generated code
        if result.needs_calculation == "true":
            # The generated code is automatically executed
            return result
        
        return {"needs_calculation": False}

# Example output:
# needs_calculation: "true"
# calculation_code: """
# def calculate_q4(annual_data, q3_data):
#     q4_result = {}
#     for line_item in annual_data:
#         if line_item in q3_data:
#             q4_result[line_item] = annual_data[line_item] - q3_data[line_item]
#     return q4_result
# """
```

## DSPy Primitives Summary for Your System

| Primitive | Use Case in Financial Parsing | Impact |
|-----------|-------------------------------|---------|
| **Signature** | Break down complex parsing logic | ✅ Modularity |
| **ChainOfThought** | Explainable financial reasoning | ✅ Transparency |
| **Assert** | Validate financial data formats | ✅ Reliability |
| **Suggest** | Handle ambiguous financial queries | ✅ Robustness |
| **Majority** | Consensus on tricky classifications | ✅ Accuracy |
| **Retrieve** | Access company/financial databases | ✅ Context |
| **Module** | Orchestrate complete parsing pipeline | ✅ Integration |
| **ProgramOfThought** | Financial calculations (Q4, ratios) | ✅ Computation |

## The Power of Composition

The real magic happens when you combine these primitives:

```python
# A robust, validated, explainable financial parser
parser = FinancialQueryParser(
    valid_tickers=PSX_BANK_TICKERS,
    company_db=financial_database
)

# Each component:
# - Uses ChainOfThought for explainability
# - Has Assert statements for validation  
# - Uses Majority for critical decisions
# - Leverages Retrieve for context
# - Composes cleanly in Module
```

## Key Insight

DSPy primitives transform your 17K character monolithic prompt into a **composable, validated, explainable system** where each component does one thing exceptionally well, but together they create something more powerful than the original monolithic approach.

Your financial parsing logic becomes not just modular, but **robust, transparent, and continuously improvable**. 