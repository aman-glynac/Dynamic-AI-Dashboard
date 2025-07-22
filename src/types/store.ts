import { Mode } from './common';
import { Dashboard, DashboardMetadata } from './dashboard';
import { GridConfig } from './container';
import { ChartConfig, DataSourceConfig } from './chart';

export interface UIState {
  mode: Mode;
  selectedContainerId?: number;
  isGenerating: boolean;
  notifications: Notification[];
  sidebarOpen: boolean;
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  createdAt: Date;
}

export interface DashboardState {
  currentDashboard?: Dashboard;
  dashboards: DashboardMetadata[];
  gridConfig: GridConfig;
  isLoading: boolean;
  error?: string;
  hasUnsavedChanges: boolean;
}

export interface ChartState {
  charts: Record<string, ChartConfig>;
  isGenerating: boolean;
  activeChart?: string;
  error?: string;
}

export interface DataState {
  dataSources: Record<string, DataSourceConfig>;
  connectionStatus: Record<string, 'connected' | 'disconnected' | 'error'>;
  lastUpdated: Record<string, Date>;
}
