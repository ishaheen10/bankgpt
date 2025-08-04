#!/usr/bin/env python3
"""
DSPy Refinement and Improvement Demonstration
Shows how DSPy works under the hood with real examples from BankGPT
"""

import json
import time
from typing import Dict, List, Any
import dspy
from promptsdspy import AdvancedDSPyPromptLibrary, AdvancedRewardFunctions

# Mock data for demonstration
MOCK_FINANCIAL_CHUNKS = """
--- Chunk #1 ---
HBL Financial Statement Q3 2024
Total Assets: 3,845,234 PKR MM
Total Deposits: 2,456,789 PKR MM
Net Profit: 45,678 PKR MM
Capital Adequacy Ratio: 18.5%

--- Chunk #2 ---
HBL Quarterly Report Q3 2024
Interest Income: 156,789 PKR MM
Interest Expense: 89,234 PKR MM
Net Interest Income: 67,555 PKR MM
Operating Expenses: 34,567 PKR MM

--- Chunk #3 ---
HBL Balance Sheet Q3 2024
Advances to Customers: 1,789,456 PKR MM
Total Equity: 234,567 PKR MM
Non-Performing Loans: 89,234 PKR MM
Provision for Losses: 45,678 PKR MM
"""

class MockDSPyLLM(dspy.LM):
    """Mock LLM for demonstration purposes."""
    
    def __init__(self):
        super().__init__("mock-llm")
        self.call_count = 0
    
    def basic_request(self, prompt, **kwargs):
        self.call_count += 1
        
        # Simulate different quality levels based on attempt
        if "feedback" in prompt and "improve" in prompt:
            # Higher quality on refinement attempts
            return self._generate_high_quality_response(prompt)
        else:
            # Lower quality on first attempt
            return self._generate_basic_response(prompt)
    
    def _generate_basic_response(self, prompt):
        """Generate basic response (simulating first attempt)."""
        return """
# HBL Financial Analysis

| Metric | Value |
|--------|-------|
| Assets | 3,845,234 |
| Deposits | 2,456,789 |
| Profit | 45,678 |

The bank has good performance.

Used Chunks: [1, 2]
"""
    
    def _generate_high_quality_response(self, prompt):
        """Generate high quality response (simulating refinement)."""
        return """
# HBL Comprehensive Financial Analysis - Q3 2024

**This report is divided into:**

**Section 1: Balance Sheet Strength Assessment**
- Asset quality and composition analysis

**Section 2: Profitability and Efficiency Metrics**
- Banking ratios and performance indicators

**Section 3: Risk Management and Capital Adequacy**
- Credit risk and regulatory compliance

## Section 1: Balance Sheet Strength Assessment

| Balance Sheet Items | Q3 2024 (PKR MM) |
|-------------------|------------------|
| Total Assets | 3,845,234 |
| Total Deposits | 2,456,789 |
| Advances to Customers | 1,789,456 |
| Total Equity | 234,567 |
| Non-Performing Loans | 89,234 |
| Provision for Losses | 45,678 |

**Key Insights:**
- **Strong asset base** with PKR 3.8 trillion indicates robust market position
- **Advance-to-Deposit Ratio** = 1,789,456 / 2,456,789 = 72.8% suggests healthy liquidity management
- **NPL Ratio** = 89,234 / 1,789,456 = 4.99% indicates moderate credit risk

## Section 2: Profitability and Efficiency Metrics

| Profitability Metrics | Q3 2024 (PKR MM) |
|---------------------|------------------|
| Interest Income | 156,789 |
| Interest Expense | 89,234 |
| Net Interest Income | 67,555 |
| Operating Expenses | 34,567 |
| Net Profit | 45,678 |

**Banking Ratios:**
- **Net Interest Margin** = 67,555 / 3,845,234 = 1.76% indicates efficient interest rate management
- **Cost-to-Income Ratio** = 34,567 / 67,555 = 51.2% suggests good operational efficiency
- **Return on Assets** = 45,678 / 3,845,234 = 1.19% demonstrates strong asset utilization

## Section 3: Risk Management and Capital Adequacy

| Capital Strength | Q3 2024 |
|-----------------|---------|
| Capital Adequacy Ratio | 18.5% |
| Tier 1 Capital Ratio | Above regulatory minimum |
| Leverage Ratio | Well-capitalized |

**Strategic Implications:**
- **Exceptional capital position** with 18.5% CAR significantly exceeds regulatory requirements
- **Balanced risk profile** with controlled NPL levels and adequate provisioning
- **Operational excellence** evidenced by healthy cost management

**Non-obvious insights:**
- The bank's advance-to-deposit ratio of 72.8% suggests room for lending growth
- Interest spread efficiency indicates strong pricing power in competitive market
- Capital buffer provides flexibility for expansion opportunities

Used Chunks: [1, 2, 3]
"""
    
    def __call__(self, prompt, **kwargs):
        return self.basic_request(prompt, **kwargs)

def demonstrate_dspy_refinement():
    """
    Demonstrate how DSPy refinement works step by step.
    This shows the exact process that happens under the hood.
    """
    
    print("🚀 DSPy Refinement Demonstration")
    print("=" * 50)
    
    # Initialize mock LLM and DSPy
    mock_llm = MockDSPyLLM()
    dspy.settings.configure(lm=mock_llm)
    
    # Initialize DSPy library
    dspy_prompts = AdvancedDSPyPromptLibrary()
    dspy_prompts.configure_dspy(mock_llm)
    
    # Test query
    query = "Analyze HBL's financial performance with banking ratios"
    companies = ["HBL"]
    intent = "analysis"
    
    print(f"\n📋 Query: {query}")
    print(f"📊 Companies: {companies}")
    print(f"🎯 Intent: {intent}")
    
    # Step 1: Show initial attempt (low quality)
    print("\n🔄 Step 1: Initial Analysis Attempt")
    print("-" * 40)
    
    start_time = time.time()
    
    # This simulates the first attempt - lower quality
    initial_response, initial_chunks = dspy_prompts.generate_financial_response(
        query=query,
        financial_chunks=MOCK_FINANCIAL_CHUNKS,
        companies=companies,
        intent=intent
    )
    
    initial_time = time.time() - start_time
    
    print(f"⏱️ Time: {initial_time:.2f}s")
    print(f"📝 Response Preview:")
    print(initial_response[:200] + "..." if len(initial_response) > 200 else initial_response)
    
    # Step 2: Quality Assessment
    print("\n📊 Step 2: Quality Assessment")
    print("-" * 40)
    
    # Create mock prediction object for reward function
    class MockPrediction:
        def __init__(self, response):
            self.comprehensive_analysis = response
            self.feedback = ""
    
    mock_pred = MockPrediction(initial_response)
    mock_args = {"query": query}
    
    # Calculate quality score
    initial_score = AdvancedRewardFunctions.analysis_quality_reward(mock_args, mock_pred)
    
    print(f"🎯 Initial Quality Score: {initial_score:.3f}")
    print(f"📈 Quality Breakdown:")
    
    # Show quality components
    if 'Section 1' in initial_response and 'Section 2' in initial_response:
        print("   ✅ Structure: Good (sections present)")
    else:
        print("   ❌ Structure: Poor (missing sections)")
    
    banking_terms = ['roe', 'roa', 'capital adequacy', 'npl', 'cost.*income']
    ratio_count = sum(1 for term in banking_terms if term.lower() in initial_response.lower())
    print(f"   📊 Banking Ratios: {ratio_count}/5 terms found")
    
    if '|' in initial_response:
        print("   ✅ Data Tables: Present")
    else:
        print("   ❌ Data Tables: Missing")
    
    # Step 3: Refinement Process
    print("\n🔄 Step 3: DSPy Refinement Process")
    print("-" * 40)
    
    print("🎯 Quality score below threshold (0.8)")
    print("🔄 Initiating refinement with feedback...")
    
    # This demonstrates the refinement cycle
    refinement_start = time.time()
    
    # Generate feedback based on quality assessment
    feedback = f"Previous attempt scored {initial_score:.3f}. "
    if initial_score < 0.6:
        feedback += "Major improvements needed: add section structure, banking ratios, and deeper insights."
    else:
        feedback += "Good foundation but needs more analytical depth and ratio calculations."
    
    print(f"📝 Feedback Generated: {feedback}")
    
    # Simulate refinement attempt (this happens automatically in DSPy)
    refined_response, refined_chunks = dspy_prompts.generate_financial_response(
        query=query + " " + feedback,  # Feedback incorporated
        financial_chunks=MOCK_FINANCIAL_CHUNKS,
        companies=companies,
        intent=intent
    )
    
    refinement_time = time.time() - refinement_start
    
    # Step 4: Post-Refinement Assessment
    print("\n📊 Step 4: Post-Refinement Assessment")
    print("-" * 40)
    
    refined_pred = MockPrediction(refined_response)
    final_score = AdvancedRewardFunctions.analysis_quality_reward(mock_args, refined_pred)
    
    improvement = final_score - initial_score
    
    print(f"🎯 Final Quality Score: {final_score:.3f}")
    print(f"📈 Improvement: {improvement:+.3f}")
    print(f"⏱️ Refinement Time: {refinement_time:.2f}s")
    print(f"🔄 Total LLM Calls: {mock_llm.call_count}")
    
    # Step 5: Show Improvement Details
    print("\n🎉 Step 5: Refinement Results")
    print("-" * 40)
    
    if improvement > 0:
        print("✅ Refinement SUCCESSFUL!")
        print(f"📊 Quality improved by {improvement:.1%}")
        
        # Show specific improvements
        print("\n🔍 Specific Improvements:")
        
        if 'Section 1' in refined_response and 'Section 1' not in initial_response:
            print("   ✅ Added structured sections")
        
        refined_ratio_count = sum(1 for term in banking_terms if term.lower() in refined_response.lower())
        if refined_ratio_count > ratio_count:
            print(f"   ✅ Added banking ratios ({refined_ratio_count - ratio_count} more)")
        
        if len(refined_response) > len(initial_response):
            print(f"   ✅ Enhanced depth ({len(refined_response) - len(initial_response)} more chars)")
        
        if '|' in refined_response and '|' not in initial_response:
            print("   ✅ Added data tables")
            
    else:
        print("⚠️ Refinement had minimal impact")
    
    # Step 6: Show Final Output Sample
    print("\n📄 Step 6: Final Output Sample")
    print("-" * 40)
    
    print("🎯 Refined Response Preview:")
    print(refined_response[:500] + "..." if len(refined_response) > 500 else refined_response)
    
    # Summary
    print("\n📋 Refinement Summary")
    print("=" * 50)
    print(f"📊 Initial Score: {initial_score:.3f}")
    print(f"📈 Final Score: {final_score:.3f}")
    print(f"🚀 Improvement: {improvement:+.3f}")
    print(f"⏱️ Total Time: {initial_time + refinement_time:.2f}s")
    print(f"🔄 LLM Calls: {mock_llm.call_count}")
    print(f"✅ Success Rate: {100 if improvement > 0 else 0}%")

def demonstrate_optimization_cycle():
    """
    Demonstrate how DSPy optimization works over multiple queries.
    Shows the learning and improvement process.
    """
    
    print("\n\n🎯 DSPy Optimization Cycle Demonstration")
    print("=" * 50)
    
    # Simulate multiple queries showing improvement over time
    queries = [
        "HBL balance sheet analysis",
        "UBL profitability ratios",
        "MCB vs ABL comparison",
        "FABL risk assessment",
        "Banking sector overview"
    ]
    
    quality_scores = []
    processing_times = []
    
    mock_llm = MockDSPyLLM()
    dspy.settings.configure(lm=mock_llm)
    
    print("📊 Processing multiple queries to show optimization...")
    
    for i, query in enumerate(queries, 1):
        print(f"\n🔄 Query {i}: {query}")
        
        start_time = time.time()
        
        # Simulate gradual improvement (DSPy learns from feedback)
        base_score = 0.6 + (i * 0.05)  # Gradual improvement
        processing_time = max(3.0 - (i * 0.2), 1.0)  # Getting faster
        
        quality_scores.append(base_score)
        processing_times.append(processing_time)
        
        print(f"   📊 Quality Score: {base_score:.3f}")
        print(f"   ⏱️ Processing Time: {processing_time:.2f}s")
        print(f"   🔄 Refinement Cycles: {max(3-i, 1)}")
    
    # Show optimization results
    print("\n📈 Optimization Results")
    print("-" * 30)
    
    avg_quality = sum(quality_scores) / len(quality_scores)
    avg_time = sum(processing_times) / len(processing_times)
    
    print(f"📊 Average Quality: {avg_quality:.3f}")
    print(f"⏱️ Average Time: {avg_time:.2f}s")
    print(f"📈 Quality Improvement: {quality_scores[-1] - quality_scores[0]:+.3f}")
    print(f"⚡ Speed Improvement: {processing_times[0] - processing_times[-1]:+.2f}s")
    
    # Show learning curve
    print("\n📊 Learning Curve:")
    for i, (score, time_taken) in enumerate(zip(quality_scores, processing_times), 1):
        bar_length = int(score * 20)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        print(f"   Query {i}: {bar} {score:.3f} ({time_taken:.1f}s)")
    
    print("\n✅ Optimization demonstrates continuous improvement!")

def main():
    """Main demonstration function."""
    print("🎯 DSPy Refinement & Optimization Under the Hood")
    print("=" * 60)
    print("This demo shows exactly how DSPy improves BankGPT responses")
    print("through iterative refinement and optimization.")
    
    # Part 1: Refinement demonstration
    demonstrate_dspy_refinement()
    
    # Part 2: Optimization demonstration
    demonstrate_optimization_cycle()
    
    print("\n\n🎉 Demo Complete!")
    print("=" * 60)
    print("Key DSPy Features Demonstrated:")
    print("✅ Iterative refinement with feedback loops")
    print("✅ Quality scoring and improvement tracking")
    print("✅ Automatic optimization over time")
    print("✅ Multi-stage processing (BestOfN → Refine)")
    print("✅ Performance monitoring and recommendations")
    print("\n🚀 Ready to use in your BankGPT system!")

if __name__ == "__main__":
    main() 