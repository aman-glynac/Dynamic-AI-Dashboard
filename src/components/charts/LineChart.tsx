'use client';

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { ChartConfig, ChartData } from '@/types';

interface LineChartProps {
  data: ChartData[];
  config: ChartConfig;
  isEditMode: boolean;
}

export function LineChartComponent({ data, config }: LineChartProps) {
  const { xAxis, yAxis, colorScheme = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b'] } = config;

  // Determine the data keys for lines
  const dataKeys = Object.keys(data[0] || {}).filter(key => 
    key !== xAxis && typeof data[0]?.[key] === 'number'
  );

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
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
          <Line
            key={key}
            type="monotone"
            dataKey={key}
            stroke={colorScheme[index % colorScheme.length]}
            strokeWidth={2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}