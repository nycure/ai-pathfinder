"use client";

import React, { useState } from 'react';
import { Send, Sparkles } from 'lucide-react';
import { useRoadmapStore } from '@/store/useRoadmapStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

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
    <Card className="w-full max-w-2xl mx-auto bg-card/60 backdrop-blur-xl border-border shadow-[0_0_40px_rgba(var(--primary),0.15)] relative overflow-hidden">
      {/* Decorative Glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-1 bg-gradient-to-r from-transparent via-primary to-transparent opacity-50" />
      
      <CardHeader>
        <CardTitle className="text-2xl font-bold flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-primary" />
          AI Learning Pathfinder
        </CardTitle>
        <CardDescription>
          Describe your career goal, current skills, and weekly availability in natural language.
        </CardDescription>
      </CardHeader>

      <CardContent>
        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        )}
        <form onSubmit={handleGenerate} className="flex flex-col gap-4">
          <div className="relative">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="E.g., I want to become a DevOps engineer..."
              className="pr-12 bg-background/50 border-input h-14 text-base"
              disabled={isLoading}
            />
            <Button
              type="submit"
              size="icon"
              disabled={!inputValue.trim() || isLoading}
              className="absolute right-2 top-2 bg-primary/20 hover:bg-primary/40 text-primary-foreground border border-primary/50"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>

          <div className="flex flex-col gap-2 mt-4">
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Quick Suggestions
            </span>
            <div className="flex flex-wrap gap-2">
              {SUGGESTIONS.map((suggestion, idx) => (
                <Badge
                  key={idx}
                  variant="secondary"
                  className="cursor-pointer hover:bg-primary/20 hover:text-primary transition-colors text-xs font-normal"
                  onClick={() => setInputValue(suggestion)}
                >
                  {suggestion}
                </Badge>
              ))}
            </div>
          </div>
        </form>

        {isLoading && (
          <div className="absolute inset-0 z-50 flex flex-col items-center justify-center bg-background/80 backdrop-blur-sm">
            <div className="w-12 h-12 rounded-full border-4 border-primary/20 border-t-primary animate-spin mb-4" />
            <p className="text-sm font-medium text-primary animate-pulse">
              Synthesizing your personalized roadmap...
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
