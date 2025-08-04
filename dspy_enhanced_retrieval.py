import dspy
from typing import List, Dict, Any, Optional
import json

# Configure DSPy with your existing LLM
dspy.configure(lm=dspy.LM('google_genai/gemini-2.5-flash'))

# ====== Query Expansion for Better Retrieval ======
class QueryExpansionSignature(dspy.Signature):
    """Expand financial query to improve vector search retrieval"""
    user_query = dspy.InputField(desc="Original user query")
    expanded_query = dspy.OutputField(desc="Query optimized for vector search with financial keywords")
    search_keywords = dspy.OutputField(desc="Additional keywords for semantic search")

# ====== Retrieval Context Optimization ======
class RetrievalOptimizerSignature(dspy.Signature):
    """Generate optimal search query for PSX financial data retrieval"""
    user_query = dspy.InputField(desc="User's financial query")
    companies = dspy.InputField(desc="Companies mentioned in query")
    statement_type = dspy.InputField(desc="Type of financial statement needed")
    time_period = dspy.InputField(desc="Time period for analysis")
    
    optimized_search_query = dspy.OutputField(desc="Optimized query for vector search")
    metadata_filters = dspy.OutputField(desc="Metadata filters for precise retrieval")
    retrieval_strategy = dspy.OutputField(desc="Strategy for retrieval (broad/narrow/multi-query)")

# ====== Enhanced Retrieval Pipeline ======
class PSXRetrievalPipeline(dspy.Module):
    """Enhanced retrieval pipeline for PSX financial data"""
    
    def __init__(self, mcp_server_client):
        self.query_expander = dspy.ChainOfThought(QueryExpansionSignature)
        self.retrieval_optimizer = dspy.ChainOfThought(RetrievalOptimizerSignature)
        self.mcp_client = mcp_server_client  # Your existing MCP server client
    
    def forward(self, user_query: str, companies: List[str], statement_type: str, time_period: str):
        """Enhanced retrieval with query optimization"""
        
        # Step 1: Expand query for better semantic search
        expanded = self.query_expander(user_query=user_query)
        
        # Step 2: Optimize retrieval strategy
        optimized = self.retrieval_optimizer(
            user_query=expanded.expanded_query,
            companies=companies,
            statement_type=statement_type,
            time_period=time_period
        )
        
        # Step 3: Execute retrieval with optimized parameters
        retrieval_results = self._execute_retrieval(
            search_query=optimized.optimized_search_query,
            metadata_filters=optimized.metadata_filters,
            strategy=optimized.retrieval_strategy
        )
        
        return {
            "expanded_query": expanded.expanded_query,
            "search_keywords": expanded.search_keywords,
            "optimized_search_query": optimized.optimized_search_query,
            "metadata_filters": optimized.metadata_filters,
            "retrieval_strategy": optimized.retrieval_strategy,
            "retrieved_nodes": retrieval_results
        }
    
    def _execute_retrieval(self, search_query: str, metadata_filters: str, strategy: str) -> List[Dict]:
        """Execute retrieval using your existing MCP server"""
        
        # Parse metadata filters (DSPy output is string, need to convert)
        try:
            filters = json.loads(metadata_filters) if isinstance(metadata_filters, str) else metadata_filters
        except:
            filters = {}
        
        # Adjust retrieval parameters based on strategy
        if strategy == "broad":
            top_k = 20  # Cast wider net
        elif strategy == "narrow":
            top_k = 10  # Focused retrieval
        elif strategy == "multi-query":
            # Execute multiple searches and combine
            return self._multi_query_retrieval(search_query, filters)
        else:
            top_k = 15  # Default
        
        # Call your existing MCP server
        result = self.mcp_client.psx_search_financial_data(
            search_query=search_query,
            metadata_filters=filters,
            top_k=top_k
        )
        
        return result.get("nodes", [])
    
    def _multi_query_retrieval(self, search_query: str, filters: Dict) -> List[Dict]:
        """Execute multiple retrieval queries for comprehensive results"""
        
        # Generate multiple search perspectives
        queries = [
            search_query,  # Original
            f"financial statement {search_query}",  # Statement focus
            f"quarterly report {search_query}",  # Period focus
            f"annual report {search_query}",  # Annual focus
        ]
        
        all_nodes = []
        seen_node_ids = set()
        
        for query in queries:
            result = self.mcp_client.psx_search_financial_data(
                search_query=query,
                metadata_filters=filters,
                top_k=8  # Smaller per query
            )
            
            # Deduplicate nodes
            for node in result.get("nodes", []):
                node_id = node.get("node_id")
                if node_id not in seen_node_ids:
                    all_nodes.append(node)
                    seen_node_ids.add(node_id)
        
        # Sort by relevance score and return top results
        all_nodes.sort(key=lambda x: x.get("score", 0), reverse=True)
        return all_nodes[:15]

# ====== Integration with Your Current System ======
class EnhancedPSXRetrieval:
    """Drop-in replacement for your current retrieval logic"""
    
    def __init__(self, mcp_server_client):
        self.retrieval_pipeline = PSXRetrievalPipeline(mcp_server_client)
    
    async def enhanced_search(self, user_query: str, companies: List[str], 
                            statement_type: str, time_period: str) -> Dict[str, Any]:
        """Enhanced search that replaces your current retrieval"""
        
        # Use DSPy pipeline to optimize retrieval
        result = self.retrieval_pipeline(
            user_query=user_query,
            companies=companies,
            statement_type=statement_type,
            time_period=time_period
        )
        
        return {
            "nodes": result["retrieved_nodes"],
            "total_found": len(result["retrieved_nodes"]),
            "search_optimization": {
                "expanded_query": result["expanded_query"],
                "search_keywords": result["search_keywords"],
                "optimized_search_query": result["optimized_search_query"],
                "metadata_filters": result["metadata_filters"],
                "retrieval_strategy": result["retrieval_strategy"]
            }
        }

# ====== Usage Example ======
def demonstrate_enhanced_retrieval():
    """Show how enhanced retrieval works for different query types"""
    
    # Mock MCP client for demonstration
    class MockMCPClient:
        def psx_search_financial_data(self, search_query, metadata_filters, top_k):
            return {
                "nodes": [
                    {"node_id": "1", "text": f"Sample financial data for {search_query}", "score": 0.9},
                    {"node_id": "2", "text": f"More financial data for {search_query}", "score": 0.8}
                ]
            }
    
    # Initialize enhanced retrieval
    enhanced = EnhancedPSXRetrieval(MockMCPClient())
    
    # Test different query types
    test_queries = [
        {
            "query": "Get FABL profit and loss account for the last 4 quarters",
            "companies": ["FABL"],
            "statement_type": "profit_and_loss",
            "time_period": "last_4_quarters"
        },
        {
            "query": "Write an equity research report comparing MEBL, BIPL, FABL and UBL",
            "companies": ["MEBL", "BIPL", "FABL", "UBL"],
            "statement_type": "comprehensive",
            "time_period": "recent"
        },
        {
            "query": "Get FABL balance sheet for 2024",
            "companies": ["FABL"],
            "statement_type": "balance_sheet",
            "time_period": "2024"
        }
    ]
    
    print("=== Enhanced Retrieval Results ===")
    for i, test in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {test['query']}")
        
        # This would be async in real usage
        result = enhanced.enhanced_search(
            user_query=test["query"],
            companies=test["companies"],
            statement_type=test["statement_type"],
            time_period=test["time_period"]
        )
        
        print(f"   Nodes found: {result['total_found']}")
        print(f"   Optimized query: {result['search_optimization']['optimized_search_query']}")
        print(f"   Strategy: {result['search_optimization']['retrieval_strategy']}")

if __name__ == "__main__":
    demonstrate_enhanced_retrieval()
    
    print("\n=== Key Benefits for Your Retrieval ===")
    print("✓ Query expansion improves semantic search quality")
    print("✓ Metadata filters are optimized per query type")
    print("✓ Multi-query strategy for comprehensive results")
    print("✓ Adaptive retrieval parameters (broad/narrow/multi)")
    print("✓ Drop-in replacement for your existing MCP search") 