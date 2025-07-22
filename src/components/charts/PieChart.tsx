'use client';

import React from 'react';
import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { ChartProps } from '@/types/chart';
import { CHART_COLORS } from '@/lib/constants';

export function PieChart({ title, data, config }: ChartProps) {
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
  
  // Find the value key (first numeric field)
  const valueKey = Object.keys(chartData[0] || {}).find(key => 
    typeof chartData[0]?.[key] === 'number'
  ) || 'value';

  // Find the name key (first non-numeric field)
  const nameKey = Object.keys(chartData[0] || {}).find(key => 
    typeof chartData[0]?.[key] !== 'number'
  ) || 'name';

  const isDonut = config?.type === 'donut';

  return (
    <div className="w-full h-full">
      {title && <h3 className="text-lg font-semibold mb-4">{title}</h3>}
      <ResponsiveContainer width="100%" height="100%">
        <RechartsPieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            outerRadius={80}
            innerRadius={isDonut ? 40 : 0}
            paddingAngle={2}
            dataKey={valueKey}
            nameKey={nameKey}
          >
            {chartData.map((entry, index) => (
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
        </RechartsPieChart>
      </ResponsiveContainer>
    </div>
  );
}