'use client';

import React from 'react';
import {
  ScatterChart as RechartsScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ZAxis,
} from 'recharts';
import { ChartProps } from '@/types/chart';
import { CHART_COLORS } from '@/lib/constants';

export function ScatterChartComponent({ title, data, config }: ChartProps) {
  const colorScheme = config?.colorScheme || CHART_COLORS;
  
  // Ensure data is an array
  const chartData = Array.isArray(data) ? data : [];
  
  if (chartData.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <p className="text-muted-foreground">No data available</p>
      </div>
    );
  }

  // Get numeric keys for axes
  const numericKeys = Object.keys(chartData[0] || {}).filter(key => 
    typeof chartData[0]?.[key] === 'number'
  );

  const xKey = config?.xAxis || numericKeys[0] || 'x';
  const yKey = config?.yAxis || numericKeys[1] || 'y';
  const zKey = numericKeys[2] || 'z';

  return (
    <div className="w-full h-full">
      {title && <h3 className="text-lg font-semibold mb-4">{title}</h3>}
      <ResponsiveContainer width="100%" height="100%">
        <RechartsScatterChart>
          <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
          <XAxis 
            dataKey={xKey}
            name={xKey}
            className="text-xs"
            tick={{ fill: 'hsl(var(--foreground))' }}
          />
          <YAxis 
            dataKey={yKey}
            name={yKey}
            className="text-xs"
            tick={{ fill: 'hsl(var(--foreground))' }}
          />
          {numericKeys.length > 2 && <ZAxis dataKey={zKey} range={[50, 200]} />}
          <Tooltip 
            cursor={{ strokeDasharray: '3 3' }}
            contentStyle={{
              backgroundColor: 'hsl(var(--card))',
              border: '1px solid hsl(var(--border))',
              borderRadius: '6px',
              color: 'hsl(var(--card-foreground))',
            }}
          />
          <Legend />
          <Scatter
            name="Data Points"
            data={chartData}
            fill={colorScheme[0]}
          />
        </RechartsScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

export { ScatterChartComponent as ScatterChart };