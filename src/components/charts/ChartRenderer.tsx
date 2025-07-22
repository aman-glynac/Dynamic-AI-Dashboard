'use client';

import React, { useMemo } from 'react';
import { ChartConfig } from '@/types';
import { BarChartComponent } from './BarChart';
import { LineChartComponent } from './LineChart';
import { PieChartComponent } from './PieChart';
import { ScatterChartComponent } from './ScatterChart';
import { DataTableComponent } from './DataTable';
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
        return BarChartComponent;
      case 'line':
        return LineChartComponent;
      case 'pie':
      case 'donut':
        return PieChartComponent;
      case 'scatter':
        return ScatterChartComponent;
      case 'table':
        return DataTableComponent;
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
          variant="outline"
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
      {chart.title && (
        <div className="chart-title">
          {chart.title}
        </div>
      )}
      
      <div className="flex-1">
        <ChartComponent
          data={data || chart.data}
          config={chart}
          isEditMode={isEditMode}
        />
      </div>
    </div>
  );
}