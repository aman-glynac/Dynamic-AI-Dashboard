'use client';

import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { ChartConfig, ChartData } from '@/types';

interface PieChartProps {
  data: ChartData[];
  config: ChartConfig;
  isEditMode: boolean;
}

export function PieChartComponent({ data, config }: PieChartProps) {
  const { colorScheme = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#f97316'] } = config;
  
  // Find the value key (first numeric field)
  const valueKey = Object.keys(data[0] || {}).find(key => 
    typeof data[0]?.[key] === 'number'
  ) || 'value';

  // Find the name key (first non-numeric field)
  const nameKey = Object.keys(data[0] || {}).find(key => 
    typeof data[0]?.[key] !== 'number'
  ) || 'name';

  const isDonut = config.type === 'donut';

  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          outerRadius={80}
          innerRadius={isDonut ? 40 : 0}
          paddingAngle={2}
          dataKey={valueKey}
          nameKey={nameKey}
        >
          {data.map((entry, index) => (
            <Cell 
              key={`cell-${index}`} 
              fill={colorScheme[index % colorScheme.length]} 
            />
          ))}
        </Pie>
        <Tooltip 
          contentStyle={{
            backgroundColor: 'hsl(var(--card))',
            border: '1px solid hsl(var(--border))',
            borderRadius: '6px',
            color: 'hsl(var(--card-foreground))',
          }}
        />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}