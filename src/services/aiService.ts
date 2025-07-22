import { ChartGenerationRequest, AIResponse, PromptRequest } from '@/types';
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
    
    let chartType = 'bar';
    if (isLine) chartType = 'line';
    else if (isPie) chartType = 'pie';
    else if (isTable) chartType = 'table';

    // Generate mock data
    const mockData = this.generateMockData(chartType);

    return {
      success: true,
      chartConfig: {
        id: '', // Will be set by the hook
        type: chartType as any,
        title: this.extractTitleFromPrompt(prompt),
        data: mockData,
        xAxis: chartType !== 'pie' ? Object.keys(mockData[0])[0] : undefined,
        yAxis: chartType !== 'pie' ? Object.keys(mockData[0])[1] : undefined,
        refreshInterval: 30, // 30 seconds
      },
      containerId,
      message: `Generated ${chartType} chart based on your prompt`,
    };
  }

  private extractTitleFromPrompt(prompt: string): string {
    // Simple title extraction
    const words = prompt.split(' ');
    const titleWords = words.slice(0, 5).join(' ');
    return titleWords.charAt(0).toUpperCase() + titleWords.slice(1);
  }

  private generateMockData(chartType: string) {
    switch (chartType) {
      case 'bar':
        return [
          { category: 'Jan', sales: 4000, revenue: 2400 },
          { category: 'Feb', sales: 3000, revenue: 1398 },
          { category: 'Mar', sales: 2000, revenue: 9800 },
          { category: 'Apr', sales: 2780, revenue: 3908 },
          { category: 'May', sales: 1890, revenue: 4800 },
          { category: 'Jun', sales: 2390, revenue: 3800 },
        ];
      
      case 'line':
        return [
          { date: 'Jan', users: 1000, sessions: 1500 },
          { date: 'Feb', users: 1200, sessions: 1800 },
          { date: 'Mar', users: 1100, sessions: 1650 },
          { date: 'Apr', users: 1400, sessions: 2100 },
          { date: 'May', users: 1600, sessions: 2400 },
          { date: 'Jun', users: 1800, sessions: 2700 },
        ];
      
      case 'pie':
        return [
          { segment: 'Desktop', value: 45 },
          { segment: 'Mobile', value: 35 },
          { segment: 'Tablet', value: 20 },
        ];
      
      case 'table':
        return [
          { product: 'Product A', sales: 150, revenue: '$15,000', growth: '12%' },
          { product: 'Product B', sales: 200, revenue: '$25,000', growth: '8%' },
          { product: 'Product C', sales: 100, revenue: '$12,000', growth: '-2%' },
          { product: 'Product D', sales: 300, revenue: '$35,000', growth: '15%' },
        ];
      
      default:
        return [];
    }
  }
}

export const aiService = new AIService();