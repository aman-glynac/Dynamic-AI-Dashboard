from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import uuid
import asyncio
from datetime import datetime
import traceback

from .models import (
    ChartGenerationRequest, ChartGenerationResponse, AsyncJobResponse, 
    JobStatusResponse, DatabaseStatusResponse, DatabaseTable, 
    ErrorResponse, JobStatus
)

from prompt_enhancement import PromptEnhancer
from query_generation import QueryExecutor, DataProcessor
from chart_generation import ComponentGenerator
from database import DatabaseManager

# Router instance
router = APIRouter()

# In-memory job storage (in production, use Redis or database)
jobs_storage: Dict[str, Dict[str, Any]] = {}

@router.post("/generate-chart", response_model=AsyncJobResponse)
async def generate_chart(request: ChartGenerationRequest, background_tasks: BackgroundTasks):
    """
    Generate a chart component asynchronously from user prompt
    
    Args:
        request: Chart generation request with prompt
        background_tasks: FastAPI background tasks
        
    Returns:
        Job ID for tracking the async generation process
    """
    try:
        # Create unique job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job in storage
        jobs_storage[job_id] = {
            "id": job_id,
            "status": JobStatus.PENDING,
            "prompt": request.prompt,
            "container_id": request.container_id,
            "created_at": datetime.now().isoformat(),
            "progress": 0,
            "result": None,
            "error_message": None,
            "completed_at": None
        }
        
        # Start background task
        background_tasks.add_task(process_chart_generation, job_id, request.prompt)
        
        return AsyncJobResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
            message="Chart generation started. Use the job ID to check status."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start chart generation: {str(e)}"
        )

@router.get("/job-status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the status of an async chart generation job
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        Current job status and result if completed
    """
    if job_id not in jobs_storage:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    
    job = jobs_storage[job_id]
    
    return JobStatusResponse(
        job_id=job["id"],
        status=job["status"],
        progress=job.get("progress", 0),
        result=job.get("result"),
        error_message=job.get("error_message"),
        created_at=job["created_at"],
        completed_at=job.get("completed_at")
    )

@router.get("/database-status", response_model=DatabaseStatusResponse)
async def get_database_status():
    """
    Get current database status and available tables
    
    Returns:
        Database information including all available tables
    """
    try:
        db_manager = DatabaseManager()
        tables_info = db_manager.get_all_tables()
        
        # Convert to response format
        tables = [
            DatabaseTable(
                table_name=table["table_name"],
                file_name=table["file_name"],
                row_count=table["row_count"],
                column_count=table["column_count"],
                columns=table["columns"],
                loaded_at=table.get("loaded_at", "Unknown")
            )
            for table in tables_info
        ]
        
        return DatabaseStatusResponse(
            total_tables=len(tables),
            tables=tables,
            database_path=db_manager.db_path
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get database status: {str(e)}"
        )

@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a completed job from storage
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        Success message
    """
    if job_id not in jobs_storage:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    
    job = jobs_storage[job_id]
    
    # Only allow deletion of completed or failed jobs
    if job["status"] in [JobStatus.PENDING, JobStatus.PROCESSING]:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete job that is still processing"
        )
    
    del jobs_storage[job_id]
    
    return {"message": "Job deleted successfully"}

@router.get("/jobs")
async def list_jobs():
    """
    List all jobs (for debugging/monitoring)
    
    Returns:
        List of all jobs with their current status
    """
    return {
        "total_jobs": len(jobs_storage),
        "jobs": [
            {
                "job_id": job["id"],
                "status": job["status"],
                "prompt": job["prompt"][:50] + "..." if len(job["prompt"]) > 50 else job["prompt"],
                "created_at": job["created_at"]
            }
            for job in jobs_storage.values()
        ]
    }

async def process_chart_generation(job_id: str, user_prompt: str):
    """
    Background task to process chart generation
    
    Args:
        job_id: Unique job identifier
        user_prompt: User's prompt for chart generation
    """
    try:
        # Update job status to processing
        jobs_storage[job_id]["status"] = JobStatus.PROCESSING
        jobs_storage[job_id]["progress"] = 10
        
        # Step 1: Enhance prompt
        enhancer = PromptEnhancer()
        enhancement_result = enhancer.enhance_prompt(user_prompt)
        jobs_storage[job_id]["progress"] = 25
        
        if not enhancement_result.has_context and enhancement_result.sql_context.strip() == "No database tables available.":
            raise Exception("No database tables available. Please process data files first.")
        
        # Step 2: Generate and execute SQL
        executor = QueryExecutor()
        sql_result, execution_results = executor.execute_sql_generation(
            enhancement_result.enhanced_prompt,
            enhancement_result.sql_context
        )
        jobs_storage[job_id]["progress"] = 50
        
        if not sql_result.success:
            raise Exception(f"SQL generation failed: {sql_result.error_message}")
        
        # Step 3: Process data
        processor = DataProcessor()
        processed_data = processor.process_query_results(sql_result, execution_results)
        jobs_storage[job_id]["progress"] = 75
        
        if not processed_data.success:
            raise Exception(f"Data processing failed: {processed_data.error_message}")
        
        # Step 4: Generate React component
        component_generator = ComponentGenerator()
        component_result = component_generator.generate_component(processed_data, user_prompt)
        
        if not component_result.success:
            # Try fallback component
            component_result = component_generator.generate_fallback_component(
                processed_data, 
                component_result.error_message or "Component generation failed"
            )
        
        # Update job with result
        jobs_storage[job_id].update({
            "status": JobStatus.COMPLETED,
            "progress": 100,
            "result": component_result.component_code,
            "component_name": component_result.component_name,
            "chart_type": component_result.chart_type,
            "completed_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        # Update job with error
        error_message = str(e)
        
        # Log full error for debugging
        print(f"Chart generation error for job {job_id}: {error_message}")
        print(f"Full traceback: {traceback.format_exc()}")
        
        jobs_storage[job_id].update({
            "status": JobStatus.FAILED,
            "error_message": error_message,
            "completed_at": datetime.now().isoformat()
        })

@router.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "message": "AI Dashboard API is running",
        "timestamp": datetime.now().isoformat()
    }