'use client';

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { ChartConfig, ChartData } from '@/types';

interface BarChartProps {
  data: ChartData[];
  config: ChartConfig;
  isEditMode: boolean;
}

export function BarChartComponent({ data, config }: BarChartProps) {
  const { xAxis, yAxis, colorScheme = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b'] } = config;

  // Determine the data keys for bars
  const dataKeys = Object.keys(data[0] || {}).filter(key => 
    key !== xAxis && typeof data[0]?.[key] === 'number'
  );

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
        <XAxis 
          dataKey={xAxis} 
          className="text-xs"
          tick={{ fontSize: 12 }}
        />
        <YAxis 
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
        />
        {dataKeys.length > 1 && <Legend />}
        
        {dataKeys.map((key, index) => (
          <Bar
            key={key}
            dataKey={key}
            fill={colorScheme[index % colorScheme.length]}
            radius={[2, 2, 0, 0]}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}