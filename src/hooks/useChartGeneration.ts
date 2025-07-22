import { useState } from 'react';
import { useChartStore, useDashboardStore } from '@/store';
import { ChartConfig, ChartType } from '@/types';
import { generateId } from '@/lib/utils';

interface GenerateChartParams {
  prompt: string;
  containerId?: number;
}

interface UseChartGenerationReturn {
  generateChart: (params: GenerateChartParams) => Promise<void>;
  isGenerating: boolean;
  error?: string;
}

export function useChartGeneration(): UseChartGenerationReturn {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string>();
  
  const { addChart } = useChartStore();
  const { gridConfig, updateContainer } = useDashboardStore();

  const generateChart = async ({ prompt, containerId }: GenerateChartParams) => {
    setIsGenerating(true);
    setError(undefined);

    try {
      // Simulate AI processing delay
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Parse prompt to determine chart type and generate mock data
      const chartConfig = parsePromptToChart(prompt);
      
      // Determine target container
      let targetContainerId = containerId;
      if (!targetContainerId) {
        // Find first empty container
        const emptyContainer = gridConfig.containers.find(c => c.isEmpty);
        targetContainerId = emptyContainer?.id || 1;
      }

      // Add chart to store
      addChart(targetContainerId, chartConfig);

      // Update container to mark as filled
      updateContainer(targetContainerId, { isEmpty: false, chartId: chartConfig.id });

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate chart');
      throw err;
    } finally {
      setIsGenerating(false);
    }
  };

  return {
    generateChart,
    isGenerating,
    error,
  };
}

function parsePromptToChart(prompt: string): ChartConfig {
  const lowerPrompt = prompt.toLowerCase();
  
  // Determine chart type from prompt
  let chartType: ChartType = 'bar';
  if (lowerPrompt.includes('line') || lowerPrompt.includes('trend') || lowerPrompt.includes('over time')) {
    chartType = 'line';
  } else if (lowerPrompt.includes('pie') || lowerPrompt.includes('donut') || lowerPrompt.includes('proportion')) {
    chartType = 'pie';
  } else if (lowerPrompt.includes('scatter') || lowerPrompt.includes('correlation')) {
    chartType = 'scatter';
  } else if (lowerPrompt.includes('table') || lowerPrompt.includes('data table')) {
    chartType = 'table';
  }

  // Generate mock data based on chart type
  const mockData = generateMockData(chartType, prompt);
  
  // Extract title from prompt
  const title = extractTitle(prompt);

  return {
    id: generateId(),
    type: chartType,
    title,
    data: mockData,
    xAxis: chartType === 'table' ? undefined : 'category',
    yAxis: chartType === 'table' ? undefined : 'value',
    colorScheme: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'],
  };
}

function generateMockData(chartType: ChartType, prompt: string) {
  const categories = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
  
  switch (chartType) {
    case 'line':
      return categories.map((category, index) => ({
        category,
        value: Math.floor(Math.random() * 100) + index * 10,
        date: `2024-${(index + 1).toString().padStart(2, '0')}-01`,
      }));
      
    case 'pie':
      return [
        { category: 'Product A', value: 35 },
        { category: 'Product B', value: 25 },
        { category: 'Product C', value: 20 },
        { category: 'Product D', value: 20 },
      ];
      
    case 'scatter':
      return Array.from({ length: 20 }, (_, i) => ({
        x: Math.random() * 100,
        y: Math.random() * 100,
        category: `Point ${i + 1}`,
      }));
      
    case 'table':
      return categories.map((category, index) => ({
        category,
        value: Math.floor(Math.random() * 1000),
        percentage: Math.floor(Math.random() * 100),
        status: index % 2 === 0 ? 'Active' : 'Inactive',
      }));
      
    default: // bar
      return categories.map(category => ({
        category,
        value: Math.floor(Math.random() * 100),
      }));
  }
}

function extractTitle(prompt: string): string {
  // Simple title extraction - in a real app, this would be more sophisticated
  const words = prompt.split(' ');
  if (words.length <= 6) {
    return prompt;
  }
  
  // Try to extract meaningful title
  if (prompt.toLowerCase().includes('showing')) {
    const parts = prompt.split(/showing|show/i);
    return parts[1]?.trim() || 'Generated Chart';
  }
  
  return prompt.length > 50 ? prompt.substring(0, 47) + '...' : prompt;
}