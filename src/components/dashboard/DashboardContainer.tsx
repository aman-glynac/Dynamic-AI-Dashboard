'use client';

import React from 'react';
import { ContainerConfig } from '@/types';
import { useChartStore } from '@/store';
import { ChartRenderer } from '@/components/charts/ChartRenderer';
import { EmptyChart } from '@/components/charts/EmptyChart';
import { cn } from '@/lib/utils';

interface DashboardContainerProps {
  container: ContainerConfig;
  isSelected: boolean;
  onClick: () => void;
  isEditMode: boolean;
}

export function DashboardContainer({
  container,
  isSelected,
  onClick,
  isEditMode,
}: DashboardContainerProps) {
  const { getChartByContainer } = useChartStore();
  
  const chart = getChartByContainer(container.id);
  const isEmpty = !chart || container.isEmpty;

  return (
    <div
      className={cn(
        'dashboard-container h-full w-full relative cursor-pointer',
        {
          'active': isSelected && isEditMode,
          'empty': isEmpty,
          'resizing': container.isResizing,
        }
      )}
      onClick={onClick}
    >
      {/* Container ID Badge (Edit Mode Only) */}
      {isEditMode && (
        <div className="absolute top-2 left-2 z-10 bg-primary text-primary-foreground text-xs px-2 py-1 rounded-full font-mono">
          {container.id}
        </div>
      )}

      {/* Chart Content */}
      <div className="chart-container">
        {isEmpty ? (
          <EmptyChart 
            containerId={container.id}
            isEditMode={isEditMode}
          />
        ) : chart ? (
          <ChartRenderer
            chart={chart}
            isEditMode={isEditMode}
          />
        ) : null}
      </div>

      {/* Resize Handle (Edit Mode Only) */}
      {isEditMode && !isEmpty && (
        <div className="react-resizable-handle react-resizable-handle-se" />
      )}
    </div>
  );
}