#!/usr/bin/env python3
"""
Test script to verify prompt formatting and Gemini 2.5 Pro response
Tests the section structure and chain of thought instructions
"""

import asyncio
import os
from dotenv import load_dotenv
from llama_index.llms.google_genai import GoogleGenAI
from prompts import prompts

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable not set")

# Initialize Gemini 2.5 Pro
streaming_llm = GoogleGenAI(model="models/gemini-2.5-pro", api_key=GEMINI_API_KEY, temperature=0.3)

async def test_analysis_prompt():
    """Test analysis prompt with dummy context"""
    print("🧪 Testing Analysis Prompt with Section Structure...")
    print("=" * 60)
    
    # Test parameters
    query = "Analyze HBL performance in 2024"
    companies = ["HBL"]
    intent = "analysis"
    is_multi_company = False
    is_quarterly_comparison = False
    is_side_by_side = False
    needs_q4_calculation = False
    
    # Get the prompt using the prompts library
    prompt = prompts.get_prompt_for_intent(
        intent=intent,
        query=query,
        companies=companies,
        is_multi_company=is_multi_company,
        is_quarterly_comparison=is_quarterly_comparison,
        is_side_by_side=is_side_by_side,
        needs_q4_calculation=needs_q4_calculation
    )
    
    # Add dummy context
    dummy_context = """
--- Chunk #1 ---
HBL Balance Sheet as at December 31, 2024
Total Assets: 3,500,000 PKR
Total Liabilities: 2,800,000 PKR
Shareholders' Equity: 700,000 PKR

--- Chunk #2 ---
HBL Profit and Loss for the year ended December 31, 2024
Net Interest Income: 450,000 PKR
Non-Interest Income: 150,000 PKR
Total Operating Expenses: 300,000 PKR
Profit Before Tax: 300,000 PKR
Net Profit: 210,000 PKR

--- Chunk #3 ---
HBL Cash Flow Statement for the year ended December 31, 2024
Operating Cash Flow: 280,000 PKR
Investing Cash Flow: -50,000 PKR
Financing Cash Flow: -100,000 PKR
Net Change in Cash: 130,000 PKR
"""
    
    # Replace the [chunks] placeholder with dummy context
    full_prompt = prompt.replace("[chunks]", dummy_context)
    
    print("📝 Generated Prompt Preview (first 500 chars):")
    print("-" * 40)
    print(full_prompt[:500] + "...")
    print("\n" + "=" * 60)
    
    # Check if key components are present
    key_components = [
        "REPORT STRUCTURE REQUIREMENTS",
        "This report is divided into:",
        "Section 1:",
        "Section 2:",
        "Section 3:",
        "STEP 1: CONTEXT ANALYSIS & REASONING",
        "STEP 2: REPORT STRUCTURE PLANNING",
        "STEP 3: SYSTEMATIC SECTION DEVELOPMENT",
        "STEP 4: QUALITY VERIFICATION"
    ]
    
    print("🔍 Checking for key components:")
    for component in key_components:
        if component in full_prompt:
            print(f"✅ {component}")
        else:
            print(f"❌ {component} - MISSING!")
    
    print("\n" + "=" * 60)
    
    # Test with Gemini 2.5 Pro
    print("🤖 Testing with Gemini 2.5 Pro...")
    print("-" * 40)
    
    try:
        response = await streaming_llm.acomplete(full_prompt)
        response_text = str(response)
        
        print("📊 Gemini Response Preview (first 1000 chars):")
        print("-" * 40)
        print(response_text[:1000] + "..." if len(response_text) > 1000 else response_text)
        
        # Check if response contains expected structure
        print("\n🔍 Checking response structure:")
        structure_indicators = [
            "Executive Summary",
            "This report is divided into:",
            "Section 1:",
            "Section 2:",
            "Section 3:",
            "STEP 1:",
            "STEP 2:",
            "STEP 3:",
            "STEP 4:"
        ]
        
        for indicator in structure_indicators:
            if indicator in response_text:
                print(f"✅ {indicator}")
            else:
                print(f"❌ {indicator} - MISSING!")
        
        print(f"\n📏 Response length: {len(response_text)} characters")
        
    except Exception as e:
        print(f"❌ Error testing with Gemini: {e}")

async def test_statement_prompt():
    """Test statement prompt to ensure it doesn't have section structure"""
    print("\n🧪 Testing Statement Prompt (should NOT have section structure)...")
    print("=" * 60)
    
    # Test parameters for statement request
    query = "Show me HBL balance sheet 2024"
    companies = ["HBL"]
    intent = "statement"
    is_multi_company = False
    is_quarterly_comparison = False
    is_side_by_side = True
    needs_q4_calculation = False
    
    # Get the prompt using the prompts library
    prompt = prompts.get_prompt_for_intent(
        intent=intent,
        query=query,
        companies=companies,
        is_multi_company=is_multi_company,
        is_quarterly_comparison=is_quarterly_comparison,
        is_side_by_side=is_side_by_side,
        needs_q4_calculation=needs_q4_calculation
    )
    
    # Add dummy context
    dummy_context = """
--- Chunk #1 ---
HBL Balance Sheet as at December 31, 2024
Total Assets: 3,500,000 PKR
Total Liabilities: 2,800,000 PKR
Shareholders' Equity: 700,000 PKR
"""
    
    # Replace the [chunks] placeholder with dummy context
    full_prompt = prompt.replace("[chunks]", dummy_context)
    
    print("📝 Generated Statement Prompt Preview (first 500 chars):")
    print("-" * 40)
    print(full_prompt[:500] + "...")
    print("\n" + "=" * 60)
    
    # Check that statement prompts DON'T have analysis components
    analysis_components = [
        "REPORT STRUCTURE REQUIREMENTS",
        "This report is divided into:",
        "Section 1:",
        "STEP 1: CONTEXT ANALYSIS & REASONING",
        "STEP 2: REPORT STRUCTURE PLANNING"
    ]
    
    print("🔍 Checking that statement prompt does NOT contain analysis components:")
    for component in analysis_components:
        if component in full_prompt:
            print(f"❌ {component} - SHOULD NOT BE PRESENT!")
        else:
            print(f"✅ {component} - Correctly absent")
    
    # Check that statement prompts have the right format
    statement_components = [
        "Present ONLY the financial statement data",
        "NO explanatory text",
        "NO code blocks",
        "just the data tables"
    ]
    
    print("\n🔍 Checking for statement-specific components:")
    for component in statement_components:
        if component in full_prompt:
            print(f"✅ {component}")
        else:
            print(f"❌ {component} - MISSING!")

async def main():
    """Run all tests"""
    print("🚀 Starting Prompt Testing Suite")
    print("=" * 60)
    
    # Test analysis prompt
    await test_analysis_prompt()
    
    # Test statement prompt
    await test_statement_prompt()
    
    print("\n" + "=" * 60)
    print("✅ Testing completed!")

if __name__ == "__main__":
    asyncio.run(main()) 