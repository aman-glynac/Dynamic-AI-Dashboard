import { DashboardMetadata } from './dashboard';
import { ChartConfig } from './chart';

export interface PaginationParams {
  page: number;
  limit: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

export interface ErrorResponse {
  success: false;
  error: string;
  details?: string;
  code?: string;
}

// API endpoint types
export type DashboardListResponse = PaginatedResponse<DashboardMetadata>;

export interface ChartGenerationResponse {
  success: boolean;
  chart?: ChartConfig;
  message: string;
  containerId?: number;
}
