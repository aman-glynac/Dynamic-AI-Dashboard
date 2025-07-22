import { useState } from 'react';
import { useChartStore, useDashboardStore, useUIStore } from '@/store';
import { ChartGenerationRequest, ChartConfig } from '@/types';
import { generateId } from '@/lib/utils';
import { aiService } from '@/services/aiService';

export function useChartGeneration() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { addChart } = useChartStore();
  const { updateContainer, gridConfig } = useDashboardStore();
  const { addNotification } = useUIStore();

  const generateChart = async (request: ChartGenerationRequest) => {
    setIsGenerating(true);
    setError(null);

    try {
      // Determine target container
      const containerId = request.containerId || getNextAvailableContainer();
      
      if (!containerId) {
        throw new Error('No available containers. Please add more containers or clear existing charts.');
      }

      // Call AI service to generate chart
      const response = await aiService.generateChart({
        ...request,
        containerId,
        context: {
          dashboardId: 'current', // Will be replaced with actual dashboard ID
          existingCharts: Object.values(useChartStore.getState().charts),
          containerStates: gridConfig.containers,
          mode: 'edit',
        },
      });

      if (!response.success || !response.chartConfig) {
        throw new Error(response.message || 'Failed to generate chart');
      }

      // Create chart config with generated ID
      const chartConfig: ChartConfig = {
        ...response.chartConfig,
        id: generateId(),
      };

      // Add chart to store
      addChart(containerId, chartConfig);

      // Update container to mark as not empty
      updateContainer(containerId, {
        isEmpty: false,
        chartId: chartConfig.id,
      });

      // Show success notification
      addNotification({
        type: 'success',
        title: 'Chart Created',
        message: `${chartConfig.type} chart created successfully in container ${containerId}`,
      });

      return { chartConfig, containerId };

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate chart';
      setError(errorMessage);
      
      addNotification({
        type: 'error',
        title: 'Chart Generation Failed',
        message: errorMessage,
      });
      
      throw err;
    } finally {
      setIsGenerating(false);
    }
  };

  const getNextAvailableContainer = (): number | null => {
    const emptyContainer = gridConfig.containers.find(c => c.isEmpty);
    return emptyContainer?.id || null;
  };

  return {
    generateChart,
    isGenerating,
    error,
    clearError: () => setError(null),
  };
}