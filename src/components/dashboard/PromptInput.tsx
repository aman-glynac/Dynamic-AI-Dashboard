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
              <button
                key={index}
                onClick={() => insertExamplePrompt(example)}
                className="text-xs px-3 py-1.5 rounded-full bg-muted hover:bg-muted/80 transition-colors"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="relative">
        <Textarea
          ref={textareaRef}
          value={prompt}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder={
            selectedContainerId
              ? `Describe the chart for container ${selectedContainerId}...`
              : "Describe the chart you want to create..."
          }
          className="min-h-[60px] max-h-[120px] pr-16 resize-none"
          disabled={isGenerating}
        />
        
        <div className="absolute right-2 bottom-2">
          <Button
            type="submit"
            size="sm"
            disabled={!prompt.trim() || isGenerating}
            className="h-8"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                <span className="sr-only">Generating...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4 mr-1" />
                <span className="sr-only">Send</span>
              </>
            )}
          </Button>
        </div>
      </form>

      {/* Helper Text */}
      <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
        <div className="flex items-center gap-4">
          <span>Press Enter to send, Shift+Enter for new line</span>
          {selectedContainerId && (
            <span className="flex items-center gap-1">
              <Zap className="w-3 h-3" />
              Target: Container {selectedContainerId}
            </span>
          )}
        </div>
        <span>{prompt.length}/500</span>
      </div>
    </div>
  );
}