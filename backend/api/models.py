from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum

class ChartGenerationRequest(BaseModel):
    """Request model for chart generation"""
    prompt: str
    container_id: Optional[int] = 1

class ChartGenerationResponse(BaseModel):
    """Response model for chart generation"""
    component_code: str
    component_name: str
    chart_type: str
    success: bool
    error_message: Optional[str] = None

class JobStatus(str, Enum):
    """Job status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AsyncJobResponse(BaseModel):
    """Response model for async job creation"""
    job_id: str
    status: JobStatus
    message: str

class JobStatusResponse(BaseModel):
    """Response model for job status check"""
    job_id: str
    status: JobStatus
    progress: Optional[int] = None
    result: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None

class DatabaseTable(BaseModel):
    """Model for database table information"""
    table_name: str
    file_name: str
    row_count: int
    column_count: int
    columns: List[str]
    loaded_at: str

class DatabaseStatusResponse(BaseModel):
    """Response model for database status"""
    total_tables: int
    tables: List[DatabaseTable]
    database_path: str

class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str
    message: str
    details: Optional[str] = None