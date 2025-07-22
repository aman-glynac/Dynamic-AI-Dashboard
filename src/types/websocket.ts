import { ChartData, ChartConfig } from './chart';

export interface WebSocketMessage {
  type: string;
  payload: unknown;
  timestamp: number;
}

export interface DataUpdateMessage extends WebSocketMessage {
  type: 'data_update';
  payload: {
    chartId: string;
    data: ChartData[];
  };
}

export interface ChartUpdateMessage extends WebSocketMessage {
  type: 'chart_update';
  payload: {
    chartId: string;
    config: Partial<ChartConfig>;
  };
}

export interface ConnectionStatusMessage extends WebSocketMessage {
  type: 'connection_status';
  payload: {
    status: 'connected' | 'disconnected' | 'reconnecting';
    message?: string;
  };
}

export type WSMessage = DataUpdateMessage | ChartUpdateMessage | ConnectionStatusMessage;
