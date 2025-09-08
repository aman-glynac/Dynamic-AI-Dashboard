"""
Simple test script for Input Parser Agent
Just give it a prompt and see the results!
"""

import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from input_parser_agent.graph import input_parser_agent
from input_parser_agent.components.state import InputParserState


def test_agent(user_input):
    """Test the agent with a user input and show results"""
    print(f"🔤 Input: '{user_input}'")
    print("-" * 50)
    
    # Create state
    state = InputParserState()
    state['raw_input'] = user_input
    
    # Run the agent
    result = input_parser_agent.invoke(state)
    
    # Show results
    print(f"✅ Cleaned Input: {result.get('cleaned_input', 'N/A')}")
    print(f"✅ Valid: {result.get('is_valid', 'N/A')}")
    print(f"✅ Schema Tables: {len(result.get('schema_context', {}))}")
    
    return result


def main():
    """Main function - can run predefined tests or interactive mode"""
    print("🧪 Simple Input Parser Agent Test")
    print("=" * 50)
    
    # Check if user provided input as command line argument
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        test_agent(user_input)
        return
    
    # Predefined test cases
    test_cases = [
        "show me sales data for Q1",
        "compare Q1 vs Q2 revenue",
        "show customer trends over time",
        "display product performance metrics",
        "hello how are you"  # Invalid case
    ]
    
    print("Running predefined test cases...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}:")
        test_agent(test_case)
        print("\n" + "="*50 + "\n")
    
    # Interactive mode
    print("🎯 Interactive Mode (type 'quit' to exit)")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\nEnter your prompt: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
            
            if not user_input:
                print("Please enter a prompt!")
                continue
            
            print()
            test_agent(user_input)
            
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == '__main__':
    main()
