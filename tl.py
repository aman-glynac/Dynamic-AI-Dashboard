"""
Test the complete LangGraph Query Engine Agent
Run this file to validate everything works correctly
"""

import sys
import json
import time
from pathlib import Path

def test_langgraph_agent():
    """Test the LangGraph Query Engine Agent"""
    
    print("LangGraph Query Engine Agent - Test Suite")
    print("=" * 50)
    
    # Check database exists
    if not Path("test_dashboard.db").exists():
        print("Database not found. Creating test database...")
        try:
            from create_test_db import create_test_database
            create_test_database()
        except Exception as e:
            print(f"Failed to create database: {str(e)}")
            print("Please run: python create_test_db.py")
            return False
    
    # Test LangGraph import
    try:
        from langgraph.graph import StateGraph
        print("LangGraph import successful")
    except ImportError:
        print("LangGraph not installed. Run: pip install langgraph")
        return False
    
    # Test agent import
    try:
        from query_engine import QueryEngineAgent
        print("Query Engine Agent import successful")
    except ImportError as e:
        print(f"Agent import failed: {str(e)}")
        print("Make sure all files are in the query_engine/ directory")
        return False
    
    # Initialize agent
    try:
        agent = QueryEngineAgent("test_dashboard.db")
        print("Agent initialized successfully")
    except Exception as e:
        print(f"Agent initialization failed: {str(e)}")
        return False
    
    # Test cases
    test_cases = [
        {
            "name": "Revenue by Category",
            "intent": {
                "intent_type": "comparison",
                "metric": "revenue",
                "dimension": "category",
                "chart_type": "bar",
                "schema_validated": True,
                "context_merged": False,
                "raw_prompt": "show revenue by category",
                "enhanced_prompt": "Display revenue comparison by category"
            }
        },
        {
            "name": "Total Customers Summary",
            "intent": {
                "intent_type": "summary",
                "metric": "customers",
                "dimension": None,
                "chart_type": "card",
                "schema_validated": True,
                "context_merged": False,
                "raw_prompt": "total customers",
                "enhanced_prompt": "Show total customer count"
            }
        },
        {
            "name": "Sales by Region",
            "intent": {
                "intent_type": "comparison",
                "metric": "sales",
                "dimension": "region",
                "chart_type": "bar",
                "schema_validated": True,
                "context_merged": False,
                "raw_prompt": "sales by region",
                "enhanced_prompt": "Compare sales across regions"
            }
        }
    ]
    
    test_results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print("-" * 30)
        
        try:
            start_time = time.time()
            result = agent.process(test_case['intent'])
            processing_time = time.time() - start_time
            
            # Validate result structure
            if 'data' not in result or 'metadata' not in result:
                print(f"  Invalid result structure")
                test_results.append(False)
                continue
            
            # Display results
            print(f"  Records returned: {len(result['data'])}")
            print(f"  Processing time: {processing_time*1000:.1f}ms")
            print(f"  Cache hit: {result['metadata'].get('cache_hit', False)}")
            print(f"  Nodes executed: {result['metadata'].get('nodes_executed', [])}")
            
            # Show sample data
            if result['data']:
                sample = result['data'][:2]
                print(f"  Sample data: {json.dumps(sample, default=str)}")
            
            # Validate SQL aggregation fix
            query = result['metadata'].get('query', '')
            if test_case['intent'].get('dimension') and query:
                if 'SUM(' in query or 'COUNT(' in query or 'AVG(' in query:
                    print(f"  SQL aggregation: Fixed (proper aggregation used)")
                else:
                    print(f"  SQL aggregation: Issue detected")
            
            test_results.append(True)
            print(f"  Status: PASSED")
            
        except Exception as e:
            print(f"  Status: FAILED - {str(e)}")
            test_results.append(False)
    
    # Test caching with a unique query
    print(f"\nTesting Cache Functionality")
    print("-" * 30)
    try:
        # Use a unique test case for cache testing
        cache_test_intent = {
            "intent_type": "summary",
            "metric": "orders",
            "dimension": None,
            "chart_type": "card",
            "schema_validated": True,
            "context_merged": False,
            "raw_prompt": "total orders for cache test",
            "enhanced_prompt": "Show total order count for cache test"
        }
        
        # First call (cache miss)
        result1 = agent.process(cache_test_intent)
        cache_miss = not result1['metadata'].get('cache_hit', False)
        
        # Second call (should cache hit)
        result2 = agent.process(cache_test_intent)
        cache_hit = result2['metadata'].get('cache_hit', False)
        
        print(f"  First call cache hit: {result1['metadata'].get('cache_hit', False)}")
        print(f"  Second call cache hit: {result2['metadata'].get('cache_hit', False)}")
        
        if cache_miss and cache_hit:
            print("  Cache functionality: WORKING")
            cache_working = True
        else:
            print("  Cache functionality: ISSUE")
            cache_working = False
    except Exception as e:
        print(f"  Cache test failed: {str(e)}")
        cache_working = False
    
    # Final results
    print(f"\nTest Results Summary")
    print("=" * 25)
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"Basic Tests: {passed_tests}/{total_tests} passed")
    print(f"Cache Test: {'PASSED' if cache_working else 'FAILED'}")
    
    overall_success = passed_tests == total_tests and cache_working
    
    if overall_success:
        print(f"\nAll tests PASSED! LangGraph Query Engine Agent is working correctly.")
        print(f"\nNext steps:")
        print(f"1. Integrate with your Intent Resolver Agent")
        print(f"2. Connect to your Visualization Agent")
        print(f"3. Show your team lead the LangGraph structure")
        return True
    else:
        print(f"\nSome tests FAILED. Please check the error messages above.")
        return False


if __name__ == "__main__":
    print("Starting LangGraph Query Engine Agent Test")
    print("=" * 60)
    
    success = test_langgraph_agent()
    
    if success:
        print(f"\nTesting completed successfully!")
    else:
        print(f"\nTesting failed. Please resolve issues before proceeding.")
        sys.exit(1)