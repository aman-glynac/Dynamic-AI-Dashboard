import { ChartGenerationRequest, AIResponse, PromptRequest, ChartType } from '@/types';
import { APP_CONFIG } from '@/lib/constants';

class AIService {
  private baseUrl = `${APP_CONFIG.API_BASE_URL}/api/ai`;

  async generateChart(request: ChartGenerationRequest): Promise<AIResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/generate-chart`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Mock response for development
      if (process.env.NODE_ENV === 'development') {
        return this.mockGenerateChart(request);
      }

      return data;
    } catch (error) {
      console.error('AI service error:', error);
      
      // Fallback to mock in development
      if (process.env.NODE_ENV === 'development') {
        return this.mockGenerateChart(request);
      }
      
      throw error;
    }
  }

  async processPrompt(request: PromptRequest): Promise<AIResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/process-prompt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('AI service error:', error);
      throw error;
    }
  }

  // Mock implementation for development
  private mockGenerateChart(request: ChartGenerationRequest): AIResponse {
    const { prompt, containerId } = request;
    
    // Simple prompt analysis for mock data
    const isBar = prompt.toLowerCase().includes('bar');
    const isLine = prompt.toLowerCase().includes('line');
    const isPie = prompt.toLowerCase().includes('pie');
    const isTable = prompt.toLowerCase().includes('table');
    const isScatter = prompt.toLowerCase().includes('scatter');
    
    let chartType: ChartType = 'bar';
    if (isLine) chartType = 'line';
    else if (isPie) chartType = 'pie';
    else if (isTable) chartType = 'table';
    else if (isScatter) chartType = 'scatter';

    // Generate mock data
    const mockData = this.generateMockData(chartType);

    return {
      success: true,
      chartConfig: {
        id: '', // Will be set by the hook
        type: chartType,
        title: this.extractTitleFromPrompt(prompt),
        data: mockData,
        xAxis: chartType !== 'pie' && chartType !== 'table' ? Object.keys(mockData[0])[0] : undefined,
        yAxis: chartType !== 'pie' && chartType !== 'table' ? Object.keys(mockData[0])[1] : undefined,
        containerId,
      },
      message: 'Chart generated successfully',
    };
  }

  private extractTitleFromPrompt(prompt: string): string {
    // Simple title extraction logic
    const titlePatterns = [
      /(?:show|display|create|generate)\s+(.+?)\s+(?:chart|graph|table|visualization)/i,
      /chart\s+(?:of|showing|displaying)\s+(.+)/i,
      /(.+?)\s+(?:over|by|per)\s+(.+)/i,
    ];

    for (const pattern of titlePatterns) {
      const match = prompt.match(pattern);
      if (match && match[1]) {
        return match[1].trim()
          .split(' ')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ');
      }
    }

    return 'Generated Chart';
  }

  private generateMockData(chartType: ChartType): any[] {
    switch (chartType) {
      case 'bar':
      case 'line':
        return [
          { month: 'Jan', value: 400, value2: 240 },
          { month: 'Feb', value: 300, value2: 139 },
          { month: 'Mar', value: 600, value2: 380 },
          { month: 'Apr', value: 800, value2: 480 },
          { month: 'May', value: 500, value2: 380 },
          { month: 'Jun', value: 700, value2: 430 },
        ];

      case 'pie':
        return [
          { name: 'Group A', value: 400 },
          { name: 'Group B', value: 300 },
          { name: 'Group C', value: 600 },
          { name: 'Group D', value: 200 },
          { name: 'Group E', value: 300 },
        ];

      case 'scatter':
        return Array.from({ length: 50 }, () => ({
          x: Math.random() * 100,
          y: Math.random() * 100,
          z: Math.random() * 50 + 50,
        }));

      case 'table':
        return [
          { id: 1, name: 'John Doe', department: 'Engineering', salary: 75000, status: 'Active' },
          { id: 2, name: 'Jane Smith', department: 'Marketing', salary: 65000, status: 'Active' },
          { id: 3, name: 'Bob Johnson', department: 'Sales', salary: 70000, status: 'On Leave' },
          { id: 4, name: 'Alice Brown', department: 'HR', salary: 60000, status: 'Active' },
          { id: 5, name: 'Charlie Wilson', department: 'Engineering', salary: 80000, status: 'Active' },
        ];

      default:
        return [];
    }
  }
}

export const aiService = new AIService();