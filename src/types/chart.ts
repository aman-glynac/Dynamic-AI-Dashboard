export type ChartType = 
  | 'bar' 
  | 'line' 
  | 'pie' 
  | 'scatter' 
  | 'table' 
  | 'area'
  | 'donut'
  | 'histogram';

export interface ChartData {
  [key: string]: string | number | boolean | null | undefined;
}

export interface ChartConfig {
  id: string;
  type: ChartType;
  title: string;
  data: ChartData[];
  xAxis?: string;
  yAxis?: string;
  colorScheme?: string[];
  customConfig?: Record<string, unknown>;
  dataSource?: DataSourceConfig;
  refreshInterval?: number;
}

export interface DataSourceConfig {
  id: string;
  type: 'api' | 'database' | 'file' | 'mock';
  url?: string;
  query?: string;
  headers?: Record<string, string>;
  params?: Record<string, unknown>;
  refreshRate?: number;
}
