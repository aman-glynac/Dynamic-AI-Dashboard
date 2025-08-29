"""
demo.py - Demo script for Error Handler Agent
"""
import sys
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from ..main import create_error_handler

def main():
    """Demo of Enhanced Error Handler Agent"""
    
    # Create agent
    print("Creating Error Handler Agent...")
    agent = create_error_handler()
    
    # Register demo feedback handlers
    def ui_handler(feedback):
        print(f"\n📱 [UI MESSAGE]: {feedback.get('user_message', 'No message')}")
        if feedback.get('recovery_suggestions'):
            print("   Suggestions:")
            for suggestion in feedback['recovery_suggestions'][:2]:
                print(f"   • {suggestion}")
    
    def pipeline_handler(feedback):
        action = feedback.get('action', 'none')
        if action == 'resume':
            print(f"\n🔄 [PIPELINE]: Resuming with preserved context")
    
    def ops_handler(feedback):
        severity = feedback.get('severity', 'unknown')
        error_id = feedback.get('error_id', 'unknown')
        print(f"\n🚨 [OPS ALERT]: Error {error_id} (Severity: {severity})")
    
    agent.register_feedback_handlers(
        ui_callback=ui_handler,
        pipeline_callback=pipeline_handler,
        ops_callback=ops_handler
    )
    
    # Pre-populate cache for demo
    print("\nPre-populating cache for demo...")
    agent.cache_service.store_result("q_003", {
        "rows": [
            {"month": "2025-07", "sales": 12345},
            {"month": "2025-08", "sales": 13456}
        ]
    })
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Input Error - Missing Parameters",
            "error": {
                "agent_id": "input_parser",
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "data": {
                    "error_type": "input_error",
                    "error_code": "AMBIGUOUS_INPUT",
                    "message": "User input 'show revenue' is ambiguous - missing time range",
                    "context": {"missing_params": ["time_range", "grouping"]},
                    "query_id": "q_001"
                }
            }
        },
        {
            "name": "Schema Error - Field Synonym Available",
            "error": {
                "agent_id": "query_engine",
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "data": {
                    "error_type": "schema_error",
                    "error_code": "FIELD_NOT_FOUND",
                    "message": "Field 'revenue' not found in schema",
                    "context": {
                        "field": "revenue",
                        "available_fields": ["sales", "product_name", "sku", "date", "region"]
                    },
                    "query_id": "q_002"
                }
            }
        },
        {
            "name": "Query Timeout - Cache Available",
            "error": {
                "agent_id": "query_engine",
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "data": {
                    "error_type": "query_error",
                    "error_code": "DB_TIMEOUT",
                    "message": "Database query timeout after 30 seconds",
                    "context": {"query_time": 30.5, "rows_scanned": 5000000},
                    "query_id": "q_003"
                }
            }
        },
        {
            "name": "Chart Error - Incompatible Type",
            "error": {
                "agent_id": "visualization_agent",
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "data": {
                    "error_type": "chart_error",
                    "error_code": "INCOMPATIBLE_CHART_TYPE",
                    "message": "Pie chart cannot display time-series data",
                    "context": {"chart": "pie", "dimension": "date", "measure": "revenue"},
                    "query_id": "q_004"
                }
            }
        },
        {
            "name": "System Error - Service Unavailable",
            "error": {
                "agent_id": "query_engine",
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "data": {
                    "error_type": "system_error",
                    "error_code": "SERVICE_UNAVAILABLE",
                    "message": "Database service is temporarily unavailable",
                    "context": {"service": "postgres", "status_code": 503},
                    "query_id": "q_005"
                }
            }
        },
        {
            "name": "Duplicate Error - Testing Idempotency",
            "error": {
                "agent_id": "query_engine",
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "data": {
                    "error_type": "schema_error",
                    "error_code": "FIELD_NOT_FOUND",
                    "message": "Field 'revenue' not found in schema",
                    "context": {
                        "field": "revenue",
                        "available_fields": ["sales", "product_name", "sku"]
                    },
                    "query_id": "q_002"  # Same as scenario 2
                }
            }
        }
    ]
    
    # Run test scenarios
    print("\n" + "="*60)
    print("Running Test Scenarios")
    print("="*60)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*60}")
        print(f"Scenario {i}: {scenario['name']}")
        print(f"{'='*60}")
        
        # Handle error
        result = agent.handle_error(scenario['error'])
        
        # Display results
        print(f"\n📊 Result Summary:")
        print(f"   Error ID: {result.get('error_id', 'unknown')}")
        print(f"   Error Type: {result.get('error_type', 'unknown')}")
        print(f"   Severity: {result.get('severity', 'unknown')}")
        print(f"   Next Action: {result.get('next_action', 'unknown')}")
        
        if result.get('automated_actions'):
            print(f"   Automated Actions: {', '.join(result['automated_actions'][:3])}")
        
        if result.get('field_mapping'):
            print(f"   Field Mapping Applied: {result['field_mapping']}")
        
        if result.get('cached_data'):
            print(f"   Using Cache (Age: {result['cached_data']['age_seconds']}s)")
        
        # Small delay for readability
        time.sleep(0.5)
    
    print(f"\n{'='*60}")
    print("Demo Complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()