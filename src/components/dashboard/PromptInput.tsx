'use client';

import React, { useState, useRef } from 'react';
import { useDashboardStore, useUIStore, useChartStore } from '@/store';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Send, Loader2, Lightbulb, Zap } from 'lucide-react';
import { useChartGeneration } from '@/hooks/useChartGeneration';

export function PromptInput() {
  const [prompt, setPrompt] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  const { selectedContainerId } = useUIStore();
  const { isGenerating } = useChartStore();
  const { generateChart } = useChartGeneration();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!prompt.trim() || isGenerating) return;

    try {
      await generateChart({
        prompt: prompt.trim(),
        containerId: selectedContainerId,
      });
      
      setPrompt('');
      
      // Auto-resize textarea back to original size
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    } catch (error) {
      console.error('Failed to generate chart:', error);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setPrompt(e.target.value);
    
    // Auto-resize textarea
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
  };

  const examplePrompts = [
    "Create a bar chart showing monthly sales data",
    "Show user growth over time as a line chart",
    "Display revenue by region in a pie chart",
    "Create a scatter plot of price vs performance",
    "Show top 10 products in a data table",
  ];

  const insertExamplePrompt = (example: string) => {
    setPrompt(example);
    textareaRef.current?.focus();
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Example Prompts */}
      {!prompt && (
        <div className="mb-3">
          <div className="flex items-center gap-2 mb-2">
            <Lightbulb className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">Try these examples:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {examplePrompts.slice(0, 3).map((example, index) => (
              <Button
                key={index}
                variant="ghost"
                size="sm"
                className="text-xs h-7 px-2 text-muted-foreground hover:text-foreground"
                onClick={() => insertExamplePrompt(example)}
              >
                <Zap className="w-3 h-3 mr-1" />
                {example}
              </Button>
            ))}
          </div>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-end gap-3 p-4 bg-card rounded-lg border border-border shadow-sm">
          <div className="flex-1">
            <Textarea
              ref={textareaRef}
              value={prompt}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder={
                selectedContainerId
                  ? `Describe the chart you want to create in container ${selectedContainerId}...`
                  : "Describe the chart you want to create (e.g., 'Create a bar chart showing monthly sales')"
              }
              className="min-h-[60px] max-h-[120px] resize-none border-0 shadow-none focus-visible:ring-0 bg-transparent"
              disabled={isGenerating}
            />
          </div>
          
          <Button
            type="submit"
            disabled={!prompt.trim() || isGenerating}
            className="shrink-0"
          >
            {isGenerating ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </div>

        {/* Status Indicators */}
        {selectedContainerId && (
          <div className="absolute -top-8 left-0">
            <div className="inline-flex items-center gap-1 px-2 py-1 bg-primary text-primary-foreground text-xs rounded-full">
              Target: Container {selectedContainerId}
            </div>
          </div>
        )}
      </form>

      {/* Help Text */}
      <div className="mt-2 text-xs text-muted-foreground text-center">
        Press Enter to generate • Shift+Enter for new line
        {!selectedContainerId && " • Click a container to target it specifically"}
      </div>
    </div>
  );
}