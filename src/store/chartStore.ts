import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { ChartConfig } from '@/types/chart';

interface ChartStore {
  // State
  charts: Record<string, ChartConfig>;
  isGenerating: boolean;
  activeChart?: string;
  error?: string;

  // Actions
  addChart: (containerId: number, chart: ChartConfig) => void;
  updateChart: (chartId: string, updates: Partial<ChartConfig>) => void;
  removeChart: (chartId: string) => void;
  setActiveChart: (chartId?: string) => void;
  setGenerating: (isGenerating: boolean) => void;
  clearError: () => void;
  getChartByContainer: (containerId: number) => ChartConfig | undefined;
}

export const useChartStore = create<ChartStore>()(
  devtools(
    (set, get) => ({
      // Initial state
      charts: {},
      isGenerating: false,

      // Actions
      addChart: (containerId: number, chart: ChartConfig) => {
        set(state => ({
          charts: {
            ...state.charts,
            [chart.id]: { ...chart, containerId },
          },
        }));
      },

      updateChart: (chartId: string, updates: Partial<ChartConfig>) => {
        set(state => ({
          charts: {
            ...state.charts,
            [chartId]: {
              ...state.charts[chartId]!,
              ...updates,
            },
          },
        }));
      },

      removeChart: (chartId: string) => {
        set(state => {
          const { [chartId]: removed, ...remainingCharts } = state.charts;
          return {
            charts: remainingCharts,
            activeChart: state.activeChart === chartId ? undefined : state.activeChart,
          };
        });
      },

      setActiveChart: (chartId?: string) => {
        set({ activeChart: chartId });
      },

      setGenerating: (isGenerating: boolean) => {
        set({ isGenerating, error: isGenerating ? undefined : get().error });
      },

      clearError: () => {
        set({ error: undefined });
      },

      getChartByContainer: (containerId: number) => {
        const { charts } = get();
        return Object.values(charts).find(chart => 
          (chart as any).containerId === containerId
        );
      },
    }),
    { name: 'chart-store' }
  )
);
