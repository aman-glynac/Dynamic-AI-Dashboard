'use client';

import React from 'react';
import { Plus, BarChart3, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useUIStore } from '@/store';

interface EmptyChartProps {
  containerId: number;
  isEditMode: boolean;
}

export function EmptyChart({ containerId, isEditMode }: EmptyChartProps) {
  const { setSelectedContainer, selectedContainerId } = useUIStore();

  const handleSelectContainer = () => {
    if (isEditMode) {
      setSelectedContainer(containerId);
    }
  };

  if (!isEditMode) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        <div className="text-center">
          <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p className="text-sm">No chart configured</p>
        </div>
      </div>
    );
  }

  const isSelected = selectedContainerId === containerId;

  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center space-y-4">
        <div className="relative">
          <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto">
            {isSelected ? (
              <MessageSquare className="w-8 h-8 text-primary animate-pulse" />
            ) : (
              <Plus className="w-8 h-8 text-muted-foreground" />
            )}
          </div>
          {isSelected && (
            <div className="absolute -top-1 -right-1 w-6 h-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-xs font-bold">
              {containerId}
            </div>
          )}
        </div>

        <div className="space-y-2">
          <h3 className="font-medium text-sm">
            {isSelected ? 'Ready for your prompt' : `Container ${containerId}`}
          </h3>
          <p className="text-xs text-muted-foreground max-w-xs">
            {isSelected 
              ? 'Type a description below to generate a chart for this container'
              : 'Click to select this container, then describe the chart you want to create'
            }
          </p>
        </div>

        {!isSelected && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleSelectContainer}
            className="mt-4"
          >
            Select Container
          </Button>
        )}
      </div>
    </div>
  );
}