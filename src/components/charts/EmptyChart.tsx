'use client';

import React from 'react';
import { Plus, BarChart3, PieChart, LineChart, Sparkles } from 'lucide-react';

interface EmptyChartProps {
  containerId: number;
  isEditMode: boolean;
}

export function EmptyChart({ containerId, isEditMode }: EmptyChartProps) {
  if (!isEditMode) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <div className="text-center space-y-2">
          <BarChart3 className="w-12 h-12 mx-auto text-muted-foreground/30" />
          <p className="text-sm text-muted-foreground">Empty Container</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full flex items-center justify-center">
      <div className="text-center space-y-4">
        <div className="relative">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-20 h-20 bg-primary/10 rounded-full animate-pulse" />
          </div>
          <Plus className="w-12 h-12 mx-auto text-muted-foreground relative z-10" />
        </div>
        
        <div className="space-y-2">
          <p className="text-sm font-medium">Container {containerId}</p>
          <p className="text-xs text-muted-foreground max-w-[200px] mx-auto">
            Use the prompt below to create a chart
          </p>
        </div>

        <div className="flex items-center justify-center gap-2">
          <BarChart3 className="w-4 h-4 text-muted-foreground/50" />
          <LineChart className="w-4 h-4 text-muted-foreground/50" />
          <PieChart className="w-4 h-4 text-muted-foreground/50" />
          <Sparkles className="w-4 h-4 text-primary" />
        </div>
      </div>
    </div>
  );
}