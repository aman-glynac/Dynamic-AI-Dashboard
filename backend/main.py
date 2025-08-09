"""
AI Dashboard Prototype - Backend Testing and Pipeline Functions

For API server functionality, use:
- python run_server.py (to start FastAPI server)
- python -m api.app (alternative way to start server)

This file contains testing and pipeline functions for development.
"""

from knowledge_base import FileParser, ContextExtractor, ChromaManager
from prompt_enhancement import PromptEnhancer
from database import DatabaseManager, SchemaAnalyzer
from query_generation import SQLGenerator, QueryExecutor, DataProcessor
from chart_generation import ComponentGenerator

def process_file_complete_pipeline(file_path: str) -> str:
    """
    Complete pipeline: Load file to database + knowledge base
    
    Args:
        file_path: Path to the CSV/Excel file
        
    Returns:
        str: Document ID of stored context
    """
    # Initialize components
    parser = FileParser()
    extractor = ContextExtractor()
    chroma_manager = ChromaManager()
    db_manager = DatabaseManager()
    
    try:
        print(f"=== PROCESSING FILE: {file_path} ===")
        
        # Step 1: Load file into SQLite database
        print("1. Loading file into database...")
        db_result = db_manager.load_file_to_database(file_path)
        print(f"   Created table: {db_result['table_name']}")
        print(f"   Loaded {db_result['row_count']} rows, {db_result['column_count']} columns")
        
        # Step 2: Parse file metadata
        print("2. Parsing file metadata...")
        metadata = parser.parse_file(file_path)
        
        # Step 3: Generate context using LLM
        print("3. Generating context with LLM...")
        context = extractor.generate_context(metadata)
        
        # Step 4: Store in ChromaDB
        print("4. Storing in knowledge base...")
        doc_id = chroma_manager.store_file_context(context)
        
        print(f"✅ Successfully processed file!")
        print(f"   Database table: {db_result['table_name']}")
        print(f"   Knowledge base ID: {doc_id}")
        
        return doc_id
        
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        raise

def test_complete_pipeline_with_chart_generation(user_prompt: str):
    """
    Test the COMPLETE pipeline: Prompt -> SQL -> Data -> Chart Component Generation
    
    Args:
        user_prompt: Raw user prompt
    """
    print(f"\n{'='*80}")
    print(f"🚀 COMPLETE PIPELINE TEST WITH CHART GENERATION")
    print(f"USER PROMPT: {user_prompt}")
    print(f"{'='*80}")
    
    try:
        # Step 1: Enhance prompt
        print("\n1️⃣ ENHANCING PROMPT...")
        enhancer = PromptEnhancer()
        enhancement_result = enhancer.enhance_prompt(user_prompt)
        
        print(f"   ✅ Enhanced (Context: {enhancement_result.has_context})")
        print(f"   📊 Data Sources: {', '.join(enhancement_result.data_sources)}")
        
        # Step 2: Generate and execute SQL
        print("\n2️⃣ GENERATING & EXECUTING SQL...")
        executor = QueryExecutor()
        sql_result, execution_results = executor.execute_sql_generation(
            enhancement_result.enhanced_prompt,
            enhancement_result.sql_context
        )
        
        if sql_result.success:
            print(f"   ✅ Generated {len(sql_result.queries)} queries")
            successful_executions = [r for r in execution_results if r.success]
            print(f"   🎯 Executed successfully: {len(successful_executions)}/{len(execution_results)}")
        else:
            print(f"   ❌ SQL Generation failed: {sql_result.error_message}")
            return
        
        # Step 3: Process data
        print("\n3️⃣ PROCESSING DATA...")
        processor = DataProcessor()
        processed_data = processor.process_query_results(sql_result, execution_results)
        
        if processed_data.success:
            print(f"   ✅ Processed {len(processed_data.chart_data)} data points")
            print(f"   📈 Chart type: {processed_data.chart_config.get('chart_type', 'unknown')}")
        else:
            print(f"   ❌ Data processing failed: {processed_data.error_message}")
            return
        
        # Step 4: Generate React Component
        print("\n4️⃣ GENERATING REACT COMPONENT...")
        component_generator = ComponentGenerator()
        component_result = component_generator.generate_component(processed_data, user_prompt)
        
        if component_result.success:
            print(f"   ✅ Generated component: {component_result.component_name}")
            print(f"   🎨 Chart type: {component_result.chart_type}")
            print(f"   📝 Code length: {len(component_result.component_code)} characters")
        else:
            print(f"   ❌ Component generation failed: {component_result.error_message}")
            # Generate fallback component
            print("   🔄 Generating fallback component...")
            component_result = component_generator.generate_fallback_component(
                processed_data, 
                component_result.error_message or "Unknown error"
            )
        
        # Step 5: Show complete results
        print(f"\n5️⃣ FINAL RESULTS:")
        print(f"{'='*50}")
        
        print(f"\n📊 DATA SUMMARY:")
        summary = processed_data.data_summary
        print(f"   Rows: {summary.get('total_rows', 0)}")
        print(f"   Columns: {summary.get('total_columns', 0)}")
        print(f"   Execution time: {summary.get('execution_time', 0):.3f}s")
        
        print(f"\n🎨 CHART CONFIG:")
        config = processed_data.chart_config
        print(f"   Type: {config.get('chart_type', 'unknown')}")
        print(f"   X-axis: {config.get('x_axis', 'unknown')}")
        print(f"   Y-axis: {config.get('y_axis', 'unknown')}")
        print(f"   Title: {config.get('title', 'No title')}")
        
        print(f"\n⚛️ GENERATED COMPONENT:")
        print(f"   Name: {component_result.component_name}")
        print(f"   Type: {component_result.chart_type}")
        print(f"   Code preview (first 300 chars):")
        print(f"   {'-'*40}")
        print(f"   {component_result.component_code[:300]}...")
        print(f"   {'-'*40}")
        
        print(f"\n💾 SAMPLE DATA (first 3 rows):")
        for i, row in enumerate(processed_data.chart_data[:3]):
            print(f"   Row {i+1}: {row}")
        
        print(f"\n🔍 QUERIES EXECUTED:")
        for i, result in enumerate(execution_results):
            if result.success:
                print(f"   ✅ Query {i+1}: {result.query_used[:100]}...")
                print(f"      → {result.row_count} rows in {result.execution_time:.3f}s")
            else:
                print(f"   ❌ Query {i+1}: {result.error_message}")
        
        print(f"\n{'='*80}")
        print("🎉 COMPLETE PIPELINE WITH CHART GENERATION SUCCESSFUL!")
        print("📋 The generated React component is ready to be rendered in the frontend container!")
        
        # Optionally save the generated component to a file for inspection
        try:
            with open(f"generated_component_{component_result.component_name}.jsx", "w") as f:
                f.write(component_result.component_code)
            print(f"💾 Component saved to: generated_component_{component_result.component_name}.jsx")
        except:
            pass
        
    except Exception as e:
        print(f"\n❌ PIPELINE ERROR: {e}")
        import traceback
        traceback.print_exc()

def test_complete_pipeline(user_prompt: str):
    """Legacy function - redirects to new chart generation pipeline"""
    test_complete_pipeline_with_chart_generation(user_prompt)

def show_database_status():
    """Show current database status"""
    db_manager = DatabaseManager()
    tables = db_manager.get_all_tables()
    
    print(f"\n📁 DATABASE STATUS:")
    print(f"   Total tables: {len(tables)}")
    
    for table in tables:
        print(f"\n   Table: {table['table_name']}")
        print(f"   File: {table['file_name']}")
        print(f"   Rows: {table['row_count']}, Columns: {table['column_count']}")
        print(f"   Columns: {', '.join(table['columns'][:5])}{'...' if len(table['columns']) > 5 else ''}")

def test_raw_sql_query(query: str):
    """Test a raw SQL query"""
    print(f"\n🔍 TESTING RAW QUERY:")
    print(f"Query: {query}")
    
    executor = QueryExecutor()
    result = executor.execute_raw_query(query)
    
    if result.success:
        print(f"✅ Success: {result.row_count} rows in {result.execution_time:.3f}s")
        for i, row in enumerate(result.data[:3]):
            print(f"   Row {i+1}: {row}")
    else:
        print(f"❌ Failed: {result.error_message}")

if __name__ == "__main__":
    # Example usage
    file_path = "path/to/your/data.csv"  # Replace with actual file path
    
    try:
        print("🎯 AI DASHBOARD PROTOTYPE - BACKEND TESTING")
        print("💡 To start the API server, run: python run_server.py")
        print("="*60)
        
        # Step 1: Process file (uncomment when you have a file)
        # doc_id = process_file_complete_pipeline(file_path)
        
        # Step 2: Show current database status
        show_database_status()
        
        # Step 3: Test complete pipeline with chart generation
        test_prompts = [
            "show me sales by platform",
            "create a bar chart of total sales by year", 
            "display the top 10 best selling games"
        ]
        
        for prompt in test_prompts:
            test_complete_pipeline_with_chart_generation(prompt)
        
        # Step 4: Test raw SQL (optional)
        # test_raw_sql_query("SELECT * FROM your_table_name LIMIT 5")
        
        print(f"\n✅ Backend testing completed!")
        print("🌐 To test the API, start the server with: python run_server.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Setup checklist:")
        print("1. Set GROQ_API_KEY in your environment")
        print("2. Process a file first with process_file_complete_pipeline()")
        print("3. Install required packages: pip install -r requirements.txt")
        print("4. Ensure data/ directory exists for SQLite database")