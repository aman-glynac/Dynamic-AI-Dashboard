'use client';

import React from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { ChartConfig, ChartData } from '@/types';

interface ScatterChartProps {
  data: ChartData[];
  config: ChartConfig;
  isEditMode: boolean;
}

export function ScatterChartComponent({ data, config }: ScatterChartProps) {
  const { xAxis, yAxis, colorScheme = ['#3b82f6'] } = config;

  return (
    <ResponsiveContainer width="100%" height="100%">
      <ScatterChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
        <XAxis 
          dataKey={xAxis} 
          type="number"
          className="text-xs"
          tick={{ fontSize: 12 }}
        />
        <YAxis 
          dataKey={yAxis}
          type="number"
          className="text-xs"
          tick={{ fontSize: 12 }}
        />
        <Tooltip 
          contentStyle={{
            backgroundColor: 'hsl(var(--card))',
            border: '1px solid hsl(var(--border))',
            borderRadius: '6px',
            color: 'hsl(var(--card-foreground))',
          }}
          cursor={{ strokeDasharray: '3 3' }}
        />
        <Scatter 
          data={data} 
          fill={colorScheme[0]}
        />
      </ScatterChart>
    </ResponsiveContainer>
  );
}