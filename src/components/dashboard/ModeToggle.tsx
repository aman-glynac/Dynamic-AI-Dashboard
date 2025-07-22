'use client';

import React from 'react';
import { useUIStore } from '@/store';
import { Button } from '@/components/ui/button';
import { Edit, Eye } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

export function ModeToggle() {
  const { mode, setMode } = useUIStore();
  const isEditMode = mode === 'edit';

  const handleToggle = () => {
    setMode(isEditMode ? 'view' : 'edit');
  };

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant={isEditMode ? 'default' : 'outline'}
            size="sm"
            onClick={handleToggle}
            className="gap-2"
          >
            {isEditMode ? (
              <>
                <Eye className="w-4 h-4" />
                <span className="hidden sm:inline">View Mode</span>
              </>
            ) : (
              <>
                <Edit className="w-4 h-4" />
                <span className="hidden sm:inline">Edit Mode</span>
              </>
            )}
          </Button>
        </TooltipTrigger>
        <TooltipContent>
          <p>Switch to {isEditMode ? 'View' : 'Edit'} Mode</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}