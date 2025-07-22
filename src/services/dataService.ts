import { DataSourceConfig, ChartData } from '@/types';
import { APP_CONFIG } from '@/lib/constants';

class DataService {
  private baseUrl = `${APP_CONFIG.API_BASE_URL}/api/data`;

  async fetchChartData(dataSource: DataSourceConfig): Promise<ChartData[]> {
    try {
      switch (dataSource.type) {
        case 'api':
          return await this.fetchFromAPI(dataSource);
        case 'database':
          return await this.fetchFromDatabase(dataSource);
        case 'file':
          return await this.fetchFromFile(dataSource);
        case 'mock':
        default:
          return await this.fetchMockData(dataSource);
      }
    } catch (error) {
      console.error('Data fetch error:', error);
      throw new Error(`Failed to fetch data: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  private async fetchFromAPI(dataSource: DataSourceConfig): Promise<ChartData[]> {
    if (!dataSource.url) {
      throw new Error('API URL is required');
    }

    const response = await fetch(dataSource.url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...dataSource.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  }

  private async fetchFromDatabase(dataSource: DataSourceConfig): Promise<ChartData[]> {
    const response = await fetch(`${this.baseUrl}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        sourceId: dataSource.id,
        query: dataSource.query,
        params: dataSource.params,
      }),
    });

    if (!response.ok) {
      throw new Error(`Database query failed: ${response.statusText}`);
    }

    return await response.json();
  }

  private async fetchFromFile(dataSource: DataSourceConfig): Promise<ChartData[]> {
    // This would handle CSV/Excel file parsing
    // For now, return mock data
    await this.sleep(1000); // Simulate loading time
    return this.generateMockData();
  }

  private async fetchMockData(dataSource: DataSourceConfig): Promise<ChartData[]> {
    // Simulate network delay
    await this.sleep(Math.random() * 1000 + 500);
    
    return this.generateMockData();
  }

  private generateMockData(): ChartData[] {
    // Generate dynamic mock data with some randomization
    return [
      { month: 'Jan', sales: Math.floor(Math.random() * 5000) + 3000 },
      { month: 'Feb', sales: Math.floor(Math.random() * 5000) + 3000 },
      { month: 'Mar', sales: Math.floor(Math.random() * 5000) + 3000 },
      { month: 'Apr', sales: Math.floor(Math.random() * 5000) + 3000 },
      { month: 'May', sales: Math.floor(Math.random() * 5000) + 3000 },
      { month: 'Jun', sales: Math.floor(Math.random() * 5000) + 3000 },
    ];
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

export const dataService = new DataService();