'use client';

import React, { useMemo } from 'react';
import { ChartConfig } from '@/types';
import { BarChart } from './BarChart';
import { LineChart } from './LineChart';
import { PieChart } from './PieChart';
import { ScatterChart } from './ScatterChart';
import { DataTable } from './DataTable';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useRealTimeData } from '@/hooks/useRealTimeData';

interface ChartRendererProps {
  chart: ChartConfig;
  isEditMode: boolean;
}

export function ChartRenderer({ chart, isEditMode }: ChartRendererProps) {
  const { data, isLoading, error, refetch } = useRealTimeData(chart);

  const ChartComponent = useMemo(() => {
    switch (chart.type) {
      case 'bar':
        return BarChart;
      case 'line':
        return LineChart;
      case 'pie':
      case 'donut':
        return PieChart;
      case 'scatter':
        return ScatterChart;
      case 'table':
        return DataTable;
      default:
        return null;
    }
  }, [chart.type]);

  if (isLoading) {
    return (
      <div className="chart-loading">
        <LoadingSpinner size="lg" />
        <p className="text-sm text-muted-foreground mt-2">Loading chart data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="chart-error flex-col space-y-4">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 mx-auto mb-2 text-destructive" />
          <h4 className="font-medium text-destructive">Chart Error</h4>
          <p className="text-sm text-muted-foreground mt-1">{error}</p>
        </div>
        <Button
          variant={"outline" as const}
          size="sm"
          onClick={() => refetch()}
          className="mx-auto"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Retry
        </Button>
      </div>
    );
  }

  if (!ChartComponent) {
    return (
      <div className="chart-error">
        <AlertCircle className="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
        <p className="text-sm text-muted-foreground">
          Unsupported chart type: {chart.type}
        </p>
      </div>
    );
  }

  return (
    <div className="w-full h-full">
      <ChartComponent
        title={chart.title}
        data={data || chart.data}
        config={chart}
        isEditMode={isEditMode}
      />
    </div>
  );
}