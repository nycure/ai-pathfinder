"use client";

import React, { useState } from 'react';
import { Send, Sparkles } from 'lucide-react';
import { useRoadmapStore } from '@/store/useRoadmapStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';

const SUGGESTIONS = [
  "I know basic Python, I want to learn AI Engineering for 10 hours a week.",
  "I want to become a Full Stack React Developer. I have no prior coding experience.",
  "Transition from Data Analyst to Data Scientist in 3 months.",
];

export function GoalChat() {
  const [inputValue, setInputValue] = useState("");
  const { submitGoal, isLoading, error } = useRoadmapStore();

  const handleGenerate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputValue.trim() || isLoading) return;
    
    await submitGoal(inputValue);
  };

  return (
    <Card className="w-full max-w-2xl mx-auto bg-card border border-border shadow-xs rounded-2xl relative overflow-hidden">
      <CardHeader className="pb-4">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-7 h-7 rounded-lg bg-primary text-primary-foreground flex items-center justify-center">
            <Sparkles className="w-3.5 h-3.5" />
          </div>
          <CardTitle className="text-xl font-bold tracking-tight text-foreground">
            What do you want to master?
          </CardTitle>
        </div>
        <CardDescription className="text-xs text-muted-foreground">
          Describe your career goal, current background, and weekly availability in natural language.
        </CardDescription>
      </CardHeader>

      <CardContent>
        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-600 text-xs">
            {error}
          </div>
        )}
        <form onSubmit={handleGenerate} className="flex flex-col gap-4">
          <div className="relative">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="E.g., I want to become a full-stack AI engineer..."
              className="pr-14 bg-background border-border h-13 text-sm rounded-xl text-foreground placeholder:text-muted-foreground/60 focus-visible:ring-1 focus-visible:ring-foreground/30"
              disabled={isLoading}
            />
            <Button
              type="submit"
              size="icon"
              disabled={!inputValue.trim() || isLoading}
              className="absolute right-2 top-2 h-9 w-9 bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg transition-all"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>

          <div className="flex flex-col gap-2 mt-2">
            <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
              Quick Suggestions
            </span>
            <div className="flex flex-wrap gap-1.5">
              {SUGGESTIONS.map((suggestion, idx) => (
                <button
                  type="button"
                  key={idx}
                  onClick={() => setInputValue(suggestion)}
                  className="px-2.5 py-1 rounded-md bg-muted/70 hover:bg-muted text-foreground border border-border/60 text-xs transition-colors text-left"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </form>

        {isLoading && (
          <div className="absolute inset-0 z-50 flex flex-col items-center justify-center bg-card/90 backdrop-blur-xs">
            <div className="w-9 h-9 rounded-full border-3 border-border border-t-foreground animate-spin mb-3" />
            <p className="text-xs font-semibold text-foreground animate-pulse">
              Synthesizing your personalized curriculum...
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
