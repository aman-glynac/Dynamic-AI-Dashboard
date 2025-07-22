import { useState, useEffect, useRef } from 'react';
import { ChartConfig, ChartData } from '@/types';
import { dataService } from '@/services/dataService';

interface UseRealTimeDataReturn {
  data: ChartData[] | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
  lastUpdated: Date | null;
}

export function useRealTimeData(chart: ChartConfig): UseRealTimeDataReturn {
  const [data, setData] = useState<ChartData[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const intervalRef = useRef<NodeJS.Timeout>();

  const fetchData = async () => {
    if (!chart.dataSource) {
      // Use static data if no data source
      setData(chart.data);
      setLastUpdated(new Date());
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const fetchedData = await dataService.fetchChartData(chart.dataSource);
      setData(fetchedData);
      setLastUpdated(new Date());
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch data';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const refetch = () => {
    fetchData();
  };

  useEffect(() => {
    // Initial data fetch
    fetchData();

    // Set up real-time updates if refresh interval is specified
    if (chart.refreshInterval && chart.refreshInterval > 0) {
      intervalRef.current = setInterval(fetchData, chart.refreshInterval * 1000);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [chart.id, chart.dataSource, chart.refreshInterval]);

  return {
    data,
    isLoading,
    error,
    refetch,
    lastUpdated,
  };
}