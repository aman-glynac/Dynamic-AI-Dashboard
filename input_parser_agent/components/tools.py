"""
Input Parser Agent Tools - LangChain Integration
"""

import json
import re
import sqlite3
import time
from typing import Any, Dict, List, Optional, Union

from langchain.tools import tool

from .config import config
from .base_llm import llm
from .schema import InputValidationOutput
from .helper_functions import (
    load_prompt_template,
    calculate_processing_time
)


@tool("clean_text", return_direct=True)
def clean_text(
    raw_input: str,
    fix_typos: Optional[bool] = True,
    remove_noise: Optional[bool] = True
) -> Dict[str, Any]:
    """Clean and normalize user input using LLM."""
    start_time = time.time()
    
    prompt_template = load_prompt_template("text_cleaning_prompt.txt")
    prompt = prompt_template.format(user_input=raw_input)
    
    try:
        response = llm.invoke(prompt)
        cleaned_input = response.content.strip()
        
        # Simple extraction - just get the cleaned text
        lines = cleaned_input.split('\n')
        cleaned_input = lines[0].strip()
        
        # Remove any prefix text the LLM might add
        if ':' in cleaned_input and len(cleaned_input.split(':')) == 2:
            cleaned_input = cleaned_input.split(':')[1].strip()
        
        # If empty or too short, keep it empty
        if len(cleaned_input) < 2:
            cleaned_input = ""
            
    except Exception as e:
        print(f"❌ LLM text cleaning failed: {e}")
        cleaned_input = raw_input.strip()
    
    processing_time = calculate_processing_time(start_time)
    
    return {
        'original_input': raw_input,
        'cleaned_input': cleaned_input,
        'processing_time_ms': processing_time
    }


@tool("validate_input", return_direct=True)
def validate_input(cleaned_input: str) -> Dict[str, Any]:
    """Validate input using LangChain structured output."""
    start_time = time.time()
    
    prompt_template = load_prompt_template("input_validation_prompt.txt")
    prompt = prompt_template.format(user_input=cleaned_input)
    
    try:
        structured_llm = llm.with_structured_output(InputValidationOutput)
        result = structured_llm.invoke(prompt)
        
        processing_time = calculate_processing_time(start_time)
        
        return {
            'is_valid': result.is_valid,
            'confidence_score': result.confidence_score,
            'primary_intent': result.primary_intent,
            'data_elements': result.data_elements or [],
            'processing_time_ms': processing_time,
            'method': 'langchain_structured_output'
        }
    
    except Exception as e:
        print(f"❌ LLM validation failed: {e}")
        processing_time = calculate_processing_time(start_time)
        
        return {
            'is_valid': False,
            'confidence_score': 0.0,
            'primary_intent': 'error',
            'data_elements': [],
            'processing_time_ms': processing_time,
            'method': 'error',
            'error_message': str(e)
        }


@tool("retrieve_database_schema", return_direct=True)
def retrieve_database_schema() -> Dict[str, Any]:
    """Retrieve all database schemas for Intent Resolver."""
    start_time = time.time()
    
    schema_cache = {}
    
    try:
        with sqlite3.connect(config.database.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            # Load table schemas
            for table_name in tables:
                try:
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = []
                    data_types = {}
                    for row in cursor.fetchall():
                        columns.append(row[1])
                        data_types[row[1]] = row[2]
                    
                    cursor.execute(f"PRAGMA foreign_key_list({table_name})")
                    relationships = []
                    for row in cursor.fetchall():
                        relationships.append(f"{row[3]} -> {row[2]}.{row[4]}")
                    
                    schema_cache[table_name] = {
                        'table_name': table_name,
                        'columns': columns,
                        'relationships': relationships,
                        'data_types': data_types
                    }
                    
                except Exception as e:
                    print(f"Warning: Could not load table {table_name}: {e}")
                    continue
        
        processing_time = calculate_processing_time(start_time)
        
        return {
            'relevant_schemas': schema_cache,
            'total_schemas_found': len(schema_cache),
            'processing_time_ms': processing_time
        }
        
    except Exception as e:
        processing_time = calculate_processing_time(start_time)
        return {
            'relevant_schemas': {},
            'total_schemas_found': 0,
            'processing_time_ms': processing_time,
            'error': f"Failed to retrieve schemas: {str(e)}"
        }
