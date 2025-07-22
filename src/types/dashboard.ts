import { GridConfig } from './container';
import { ChartConfig } from './chart';

export interface Dashboard {
  id: string;
  title: string;
  description?: string;
  gridConfig: GridConfig;
  charts: Record<string, ChartConfig>;
  createdAt: Date;
  updatedAt: Date;
  userId?: string;
  isPublic: boolean;
  version: number;
}

export interface DashboardMetadata {
  id: string;
  title: string;
  description?: string;
  createdAt: Date;
  updatedAt: Date;
  chartCount: number;
  containerCount: number;
}

export interface CreateDashboardRequest {
  title: string;
  description?: string;
  containerCount?: number;
}

export interface UpdateDashboardRequest {
  title?: string;
  description?: string;
  gridConfig?: GridConfig;
  charts?: Record<string, ChartConfig>;
}
