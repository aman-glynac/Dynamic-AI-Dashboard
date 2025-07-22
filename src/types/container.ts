import { Mode } from './common';

export interface ContainerLayout {
  id: number;
  x: number;
  y: number;
  width: number;
  height: number;
  minWidth?: number;
  minHeight?: number;
}

export interface ContainerConfig {
  id: number;
  layout: ContainerLayout;
  chartId?: string;
  isEmpty: boolean;
  isResizing?: boolean;
}

export interface GridConfig {
  containerCount: number;
  containers: ContainerConfig[];
  mode: Mode;
}
