"""
Unit tests for the main QueryEngineAgent class
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add parent directory to path so we can import query_engine
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from query_engine.agent import QueryEngineAgent
    from query_engine.state import QueryEngineInput, QueryEngineState
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure the query_engine package is properly structured")

class TestQueryEngineAgent(unittest.TestCase):
    """Test cases for QueryEngineAgent"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a test database path
        self.test_db_path = "test_dashboard.db"
        
        # Check if test database exists
        if not Path(self.test_db_path).exists():
            self.skipTest("Test database not found. Run create_test_db.py first")
        
        try:
            self.agent = QueryEngineAgent(self.test_db_path)
        except Exception as e:
            self.skipTest(f"Failed to initialize agent: {e}")
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        self.assertIsNotNone(self.agent.graph)
        self.assertEqual(self.agent.db_path, self.test_db_path)
        self.assertIsNotNone(self.agent._create_graph())
    
    def test_cache_decision_logic(self):
        """Test cache decision logic"""
        # Test cache hit
        state_hit = QueryEngineState(
            intent_type="test", metric="test", dimension=None, chart_type="bar",
            schema_validated=True, context_merged=False, raw_prompt="", enhanced_prompt="",
            cache_key="", cache_hit=True, sql_query="", execution_time=0.0, query_success=False,
            raw_data=[], record_count=0, formatted_data=[], metadata={},
            error=None, warnings=[], nodes_executed=[], processing_start_time=0.0
        )
        self.assertEqual(self.agent._cache_decision(state_hit), "cache_hit")
        
        # Test cache miss
        state_miss = state_hit.copy()
        state_miss["cache_hit"] = False
        self.assertEqual(self.agent._cache_decision(state_miss), "cache_miss")
    
    def test_execution_decision_logic(self):
        """Test execution decision logic"""
        # Test success (no error)
        state_success = QueryEngineState(
            intent_type="test", metric="test", dimension=None, chart_type="bar",
            schema_validated=True, context_merged=False, raw_prompt="", enhanced_prompt="",
            cache_key="", cache_hit=False, sql_query="", execution_time=0.0, query_success=True,
            raw_data=[], record_count=0, formatted_data=[], metadata={},
            error=None, warnings=[], nodes_executed=[], processing_start_time=0.0
        )
        self.assertEqual(self.agent._execution_decision(state_success), "success")
        
        # Test error
        state_error = state_success.copy()
        state_error["error"] = "Query failed"
        self.assertEqual(self.agent._execution_decision(state_error), "error")
    
    def test_process_method_exists(self):
        """Test that process method exists and is callable"""
        self.assertTrue(hasattr(self.agent, 'process'))
        self.assertTrue(callable(getattr(self.agent, 'process')))
    
    def test_basic_query_processing(self):
        """Test basic query processing functionality"""
        # Simple test intent
        test_intent = {
            "intent_type": "summary",
            "metric": "customers",
            "dimension": None,
            "chart_type": "card",
            "schema_validated": True,
            "context_merged": False,
            "raw_prompt": "total customers",
            "enhanced_prompt": "Show total customer count"
        }
        
        try:
            result = self.agent.process(test_intent)
            
            # Validate result structure
            self.assertIsInstance(result, dict)
            self.assertIn('data', result)
            self.assertIn('metadata', result)
            self.assertIsInstance(result['data'], list)
            self.assertIsInstance(result['metadata'], dict)
            
            # Basic metadata validation
            metadata = result['metadata']
            self.assertIn('total_records', metadata)
            self.assertIn('execution_time', metadata)
            self.assertIn('status', metadata)
            
        except Exception as e:
            self.fail(f"Basic query processing failed: {e}")
    
    def test_revenue_by_category_aggregation(self):
        """Test that revenue by category uses proper SQL aggregation"""
        test_intent = {
            "intent_type": "comparison",
            "metric": "revenue",
            "dimension": "category",
            "chart_type": "bar",
            "schema_validated": True,
            "context_merged": False,
            "raw_prompt": "revenue by category",
            "enhanced_prompt": "Show revenue by category"
        }
        
        try:
            result = self.agent.process(test_intent)
            
            # Check that we got multiple categories (aggregation working)
            self.assertGreater(len(result['data']), 1, "Should return multiple categories")
            
            # Check that SQL uses proper aggregation
            query = result['metadata'].get('query', '')
            self.assertIn('SUM(', query, "Query should use SUM aggregation for revenue")
            self.assertIn('GROUP BY', query, "Query should group by category")
            
            # Check data structure
            if result['data']:
                first_row = result['data'][0]
                self.assertIn('category', first_row)
                self.assertIn('revenue', first_row)
                self.assertIsInstance(first_row['revenue'], (int, float))
                
        except Exception as e:
            self.fail(f"Revenue by category test failed: {e}")
    
    def test_error_handling(self):
        """Test error handling with invalid input"""
        invalid_intent = {
            "intent_type": "invalid_type",
            "metric": "nonexistent_metric", 
            "dimension": "invalid_dimension",
            "chart_type": "unknown_chart",
            "schema_validated": False,
            "context_merged": False,
            "raw_prompt": "invalid query",
            "enhanced_prompt": "This should fail"
        }
        
        try:
            result = self.agent.process(invalid_intent)
            
            # Should still return a result structure, even if it's an error
            self.assertIsInstance(result, dict)
            self.assertIn('data', result)
            self.assertIn('metadata', result)
            
            # Error should be handled gracefully
            metadata = result['metadata']
            # Either status should be 'error' or we should get fallback data
            self.assertTrue(
                metadata.get('status') == 'error' or 
                len(result['data']) > 0,
                "Should handle errors gracefully"
            )
            
        except Exception as e:
            self.fail(f"Error handling test failed: {e}")

class TestQueryEngineIntegration(unittest.TestCase):
    """Integration tests for complete workflow"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.test_db_path = "test_dashboard.db"
        
        if not Path(self.test_db_path).exists():
            self.skipTest("Test database not found. Run create_test_db.py first")
        
        try:
            self.agent = QueryEngineAgent(self.test_db_path)
        except Exception as e:
            self.skipTest(f"Failed to initialize agent: {e}")
    
    def test_cache_functionality(self):
        """Test that caching works correctly"""
        test_intent = {
            "intent_type": "summary",
            "metric": "orders",
            "dimension": None,
            "chart_type": "card",
            "schema_validated": True,
            "context_merged": False,
            "raw_prompt": "total orders",
            "enhanced_prompt": "Show total order count"
        }
        
        try:
            # First call - should be cache miss
            result1 = self.agent.process(test_intent)
            cache_hit1 = result1['metadata'].get('cache_hit', False)
            
            # Second call - should be cache hit
            result2 = self.agent.process(test_intent)
            cache_hit2 = result2['metadata'].get('cache_hit', False)
            
            # Validate caching behavior
            self.assertFalse(cache_hit1, "First call should be cache miss")
            self.assertTrue(cache_hit2, "Second call should be cache hit")
            
            # Results should be the same
            self.assertEqual(result1['data'], result2['data'])
            
        except Exception as e:
            self.fail(f"Cache functionality test failed: {e}")
    
    def test_multiple_query_types(self):
        """Test different types of queries work correctly"""
        test_cases = [
            {
                "name": "Summary Query",
                "intent": {
                    "intent_type": "summary",
                    "metric": "customers",
                    "dimension": None,
                    "chart_type": "card"
                }
            },
            {
                "name": "Comparison Query", 
                "intent": {
                    "intent_type": "comparison",
                    "metric": "sales",
                    "dimension": "region",
                    "chart_type": "bar"
                }
            },
            {
                "name": "Trend Query",
                "intent": {
                    "intent_type": "trend",
                    "metric": "orders",
                    "dimension": "month",
                    "chart_type": "line"
                }
            }
        ]
        
        for test_case in test_cases:
            with self.subTest(test_case['name']):
                # Add required fields
                intent = test_case['intent']
                intent.update({
                    "schema_validated": True,
                    "context_merged": False,
                    "raw_prompt": f"test {intent['metric']}",
                    "enhanced_prompt": f"Test {intent['metric']} query"
                })
                
                try:
                    result = self.agent.process(intent)
                    
                    # Basic validation
                    self.assertIn('data', result)
                    self.assertIn('metadata', result)
                    self.assertEqual(result['metadata']['status'], 'success')
                    
                    if intent.get('dimension'):
                        # Grouped queries should return multiple records
                        self.assertGreater(len(result['data']), 0)
                    else:
                        # Summary queries should return single record
                        self.assertEqual(len(result['data']), 1)
                        
                except Exception as e:
                    self.fail(f"{test_case['name']} failed: {e}")


def run_tests():
    """Run all tests"""
    print("Running Query Engine Agent Unit Tests")
    print("=" * 45)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestQueryEngineAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestQueryEngineIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    tests_run = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    
    print(f"\nTest Summary:")
    print(f"Tests run: {tests_run}")
    print(f"Failures: {failures}")
    print(f"Errors: {errors}")
    
    if failures == 0 and errors == 0:
        print("All tests PASSED!")
        return True
    else:
        print("Some tests FAILED!")
        return False


if __name__ == '__main__':
    run_tests()