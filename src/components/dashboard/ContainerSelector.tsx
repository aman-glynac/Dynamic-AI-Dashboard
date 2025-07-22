'use client';

import React from 'react';
import { useDashboardStore } from '@/store';
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Grid3X3, Minus, Plus } from 'lucide-react';

export function ContainerSelector() {
  const { gridConfig, setContainerCount } = useDashboardStore();
  const currentCount = gridConfig.containerCount;

  const handleCountChange = (value: number[]) => {
    setContainerCount(value[0]!);
  };

  const increment = () => {
    if (currentCount < 10) {
      setContainerCount(currentCount + 1);
    }
  };

  const decrement = () => {
    if (currentCount > 1) {
      setContainerCount(currentCount - 1);
    }
  };

  return (
    <div className="flex items-center gap-3 p-2 bg-muted rounded-lg">
      <Grid3X3 className="w-4 h-4 text-muted-foreground" />
      <Label className="text-sm font-medium whitespace-nowrap">
        Containers: {currentCount}
      </Label>
      
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          className="h-6 w-6 p-0"
          onClick={decrement}
          disabled={currentCount <= 1}
        >
          <Minus className="h-3 w-3" />
        </Button>
        
        <div className="w-24">
          <Slider
            value={[currentCount]}
            onValueChange={handleCountChange}
            min={1}
            max={10}
            step={1}
            className="w-full"
          />
        </div>
        
        <Button
          variant="outline"
          size="sm"
          className="h-6 w-6 p-0"
          onClick={increment}
          disabled={currentCount >= 10}
        >
          <Plus className="h-3 w-3" />
        </Button>
      </div>
    </div>
  );
}