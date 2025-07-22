'use client';

import React from 'react';
import { useUIStore, useDashboardStore } from '@/store';
import { Button } from '@/components/ui/button';
import { Edit3, Eye, Save } from 'lucide-react';
import { Mode } from '@/types';

export function ModeToggle() {
  const { mode, setMode } = useUIStore();
  const { hasUnsavedChanges, saveDashboard, isLoading } = useDashboardStore();

  const handleModeChange = async (newMode: Mode) => {
    // If switching from edit to view and there are unsaved changes, save first
    if (mode === 'edit' && newMode === 'view' && hasUnsavedChanges) {
      await saveDashboard();
    }
    setMode(newMode);
  };

  return (
    <div className="flex items-center gap-2">
      {hasUnsavedChanges && mode === 'edit' && (
        <Button
          variant="outline"
          size="sm"
          onClick={() => saveDashboard()}
          disabled={isLoading}
          className="text-orange-600 border-orange-200 hover:bg-orange-50"
        >
          <Save className="w-4 h-4 mr-1" />
          {isLoading ? 'Saving...' : 'Save'}
        </Button>
      )}
      
      <div className="flex rounded-lg border border-border bg-muted p-1">
        <Button
          variant={mode === 'edit' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => handleModeChange('edit')}
          className="h-8 px-3 text-xs"
        >
          <Edit3 className="w-3 h-3 mr-1" />
          Edit
        </Button>
        <Button
          variant={mode === 'view' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => handleModeChange('view')}
          className="h-8 px-3 text-xs"
        >
          <Eye className="w-3 h-3 mr-1" />
          View
        </Button>
      </div>
    </div>
  );
}