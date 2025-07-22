import { ChartConfig, ChartType, DataSourceConfig } from './chart';
import { ContainerConfig } from './container';
import { Mode } from './common';

export interface PromptRequest {
  prompt: string;
  containerId?: number;
  context?: DashboardContext;
}

export interface DashboardContext {
  dashboardId: string;
  existingCharts: ChartConfig[];
  containerStates: ContainerConfig[];
  mode: Mode;
}

export interface AIResponse {
  success: boolean;
  chartConfig?: ChartConfig;
  containerId?: number;
  message: string;
  suggestions?: string[];
}

export interface ChartGenerationRequest {
  prompt: string;
  containerId?: number;
  chartType?: ChartType;
  dataSource?: DataSourceConfig;
}
