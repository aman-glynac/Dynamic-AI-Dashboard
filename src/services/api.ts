const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface ChartGenerationRequest {
  prompt: string;
  container_id?: number;
}

export interface AsyncJobResponse {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  message: string;
}

export interface JobStatusResponse {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  result?: string;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

export interface DatabaseTable {
  table_name: string;
  file_name: string;
  row_count: number;
  column_count: number;
  columns: string[];
  loaded_at: string;
}

export interface DatabaseStatusResponse {
  total_tables: number;
  tables: DatabaseTable[];
  database_path: string;
}

class ApiService {
  
  async generateChart(request: ChartGenerationRequest): Promise<AsyncJobResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/generate-chart`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error generating chart:', error);
      throw error;
    }
  }

  async getJobStatus(jobId: string): Promise<JobStatusResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/job-status/${jobId}`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting job status:', error);
      throw error;
    }
  }

  async getDatabaseStatus(): Promise<DatabaseStatusResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/database-status`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting database status:', error);
      throw error;
    }
  }

  async healthCheck(): Promise<{ status: string; message: string; timestamp: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error checking API health:', error);
      throw error;
    }
  }

  // Utility method for polling job status
  async pollJobStatus(
    jobId: string, 
    onProgress?: (status: JobStatusResponse) => void,
    pollInterval: number = 5000
  ): Promise<string> {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const status = await this.getJobStatus(jobId);
          
          // Call progress callback if provided
          if (onProgress) {
            onProgress(status);
          }

          if (status.status === 'completed') {
            if (status.result) {
              resolve(status.result);
            } else {
              reject(new Error('Job completed but no result returned'));
            }
          } else if (status.status === 'failed') {
            reject(new Error(status.error_message || 'Job failed'));
          } else {
            // Continue polling for pending/processing jobs
            setTimeout(poll, pollInterval);
          }
        } catch (error) {
          reject(error);
        }
      };

      // Start polling
      poll();
    });
  }
}

export const apiService = new ApiService();