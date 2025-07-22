'use client';

import React from 'react';
import { useDashboardStore, useUIStore } from '@/store';
import { DashboardGrid } from './DashboardGrid';
import { PromptInput } from './PromptInput';
import { ContainerSelector } from './ContainerSelector';
import { ModeToggle } from './ModeToggle';
import { SaveLoadControls } from './SaveLoadControls';
import { cn } from '@/lib/utils';

interface DashboardCanvasProps {
  className?: string;
}

export function DashboardCanvas({ className }: DashboardCanvasProps) {
  const { gridConfig } = useDashboardStore();
  const { mode } = useUIStore();
  const isEditMode = mode === 'edit';

  return (
    <div className={cn('flex flex-col h-full', className)}>
      {/* Header Controls */}
      <div className="flex items-center justify-between p-4 bg-card border-b border-border">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-semibold">Dashboard Builder</h1>
          {isEditMode && <ContainerSelector />}
        </div>
        
        <div className="flex items-center gap-2">
          <SaveLoadControls />
          <ModeToggle />
        </div>
      </div>

      {/* Main Canvas Area */}
      <div className="flex-1 dashboard-canvas p-4">
        <DashboardGrid />
      </div>

      {/* Prompt Input (Edit Mode Only) */}
      {isEditMode && (
        <div className="prompt-input-container">
          <PromptInput />
        </div>
      )}
    </div>
  );
}
