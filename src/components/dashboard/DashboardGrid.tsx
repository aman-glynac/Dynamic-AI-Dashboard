'use client';

import React, { useCallback, useMemo } from 'react';
import { Responsive, WidthProvider } from 'react-grid-layout';
import { useDashboardStore, useUIStore } from '@/store';
import { DashboardContainer } from './DashboardContainer';
import { ContainerConfig } from '@/types';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

const ResponsiveGridLayout = WidthProvider(Responsive);

export function DashboardGrid() {
  const { gridConfig, updateContainer } = useDashboardStore();
  const { mode, selectedContainerId, setSelectedContainer } = useUIStore();
  
  const isEditMode = mode === 'edit';

  // Convert our container configs to react-grid-layout format
  const layoutItems = useMemo(() => {
    return gridConfig.containers.map(container => ({
      i: container.id.toString(),
      x: container.layout.x,
      y: container.layout.y,
      w: container.layout.width,
      h: container.layout.height,
      minW: container.layout.minWidth || 1,
      minH: container.layout.minHeight || 1,
      static: !isEditMode, // Disable dragging/resizing in view mode
    }));
  }, [gridConfig.containers, isEditMode]);

  const handleLayoutChange = useCallback((layout: any[]) => {
    if (!isEditMode) return;

    layout.forEach(item => {
      const containerId = parseInt(item.i);
      const container = gridConfig.containers.find(c => c.id === containerId);
      
      if (container) {
        const hasChanged = 
          container.layout.x !== item.x ||
          container.layout.y !== item.y ||
          container.layout.width !== item.w ||
          container.layout.height !== item.h;

        if (hasChanged) {
          updateContainer(containerId, {
            layout: {
              ...container.layout,
              x: item.x,
              y: item.y,
              width: item.w,
              height: item.h,
            },
          });
        }
      }
    });
  }, [gridConfig.containers, updateContainer, isEditMode]);

  const handleContainerClick = useCallback((containerId: number) => {
    if (isEditMode) {
      setSelectedContainer(
        selectedContainerId === containerId ? undefined : containerId
      );
    }
  }, [isEditMode, selectedContainerId, setSelectedContainer]);

  return (
    <div className="h-full w-full">
      <ResponsiveGridLayout
        className="grid-layout"
        layouts={{ lg: layoutItems }}
        breakpoints={{ lg: 1200, md: 996, sm: 768 }}
        cols={{ lg: 12, md: 10, sm: 6 }}
        rowHeight={100}
        isDraggable={isEditMode}
        isResizable={isEditMode}
        onLayoutChange={handleLayoutChange}
        margin={[16, 16]}
        containerPadding={[0, 0]}
        useCSSTransforms={true}
        preventCollision={false}
        compactType="vertical"
      >
        {gridConfig.containers.map((container) => (
          <div key={container.id.toString()}>
            <DashboardContainer
              container={container}
              isSelected={selectedContainerId === container.id}
              onClick={() => handleContainerClick(container.id)}
              isEditMode={isEditMode}
            />
          </div>
        ))}
      </ResponsiveGridLayout>
    </div>
  );
}