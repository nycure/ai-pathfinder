"use client";

import React, { useState } from 'react';
import { useRoadmapStore } from '@/store/useRoadmapStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { CheckCircle2, RotateCcw, AlertTriangle, Send, GitBranch } from 'lucide-react';
import { RoadmapNodeData } from '@/lib/types';
import { MasteryQuizModal } from './MasteryQuizModal';
import { GitHubVerificationModal } from './GitHubVerificationModal';

interface AdaptationControlsProps {
  nodeId: string;
  data: RoadmapNodeData;
}

export function AdaptationControls({ nodeId, data }: AdaptationControlsProps) {
  const { completeNode, submitFeedback, isLoading } = useRoadmapStore();
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackText, setFeedbackText] = useState("");
  
  const [isQuizModalOpen, setIsQuizModalOpen] = useState(false);
  const [isGitHubModalOpen, setIsGitHubModalOpen] = useState(false);

  const handleFeedbackSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!feedbackText.trim() || isLoading) return;
    
    // We prefix the feedback to give context to the backend agent
    const contextPrefix = `Regarding milestone '${data.label}': `;
    await submitFeedback(contextPrefix + feedbackText);
    setFeedbackText("");
    setShowFeedback(false);
  };

  if (data.status === 'locked') {
    return (
      <div className="flex items-center gap-2 text-muted-foreground bg-muted/50 p-3 rounded-lg border border-border text-sm">
        <AlertTriangle className="w-4 h-4" />
        Complete prerequisite milestones to unlock this action.
      </div>
    );
  }

  if (data.status === 'completed') {
    return (
      <div className="flex items-center gap-2 text-green-500 bg-green-500/10 p-3 rounded-lg border border-green-500/20 text-sm">
        <CheckCircle2 className="w-4 h-4" />
        You have successfully mastered this milestone.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col sm:flex-row gap-3">
        <Button 
          onClick={() => setIsQuizModalOpen(true)}
          disabled={isLoading}
          className="flex-1 bg-green-600 hover:bg-green-700 text-white"
        >
          <CheckCircle2 className="w-4 h-4 mr-2" />
          Mark as Mastered
        </Button>
        <Button 
          onClick={() => setIsGitHubModalOpen(true)}
          disabled={isLoading}
          variant="outline"
          className="flex-1 border-primary text-primary hover:bg-primary/10"
        >
          <GitBranch className="w-4 h-4 mr-2" />
          Verify Repo
        </Button>
        <Button 
          onClick={() => setShowFeedback(!showFeedback)}
          disabled={isLoading}
          variant="outline"
          className="flex-1 border-accent/50 text-accent hover:bg-accent/10"
        >
          <RotateCcw className="w-4 h-4 mr-2" />
          Need More Practice?
        </Button>
      </div>

      {showFeedback && (
        <form onSubmit={handleFeedbackSubmit} className="flex gap-2 animate-in fade-in slide-in-from-top-2">
          <Input 
            value={feedbackText}
            onChange={e => setFeedbackText(e.target.value)}
            placeholder="E.g., I'm struggling with React Hooks..."
            disabled={isLoading}
            className="flex-1 bg-background"
          />
          <Button type="submit" disabled={!feedbackText.trim() || isLoading} size="icon" variant="secondary">
            <Send className="w-4 h-4" />
          </Button>
        </form>
      )}

      {isLoading && (
        <p className="text-xs text-primary animate-pulse text-center">
          Adapting curriculum...
        </p>
      )}

      <MasteryQuizModal 
        isOpen={isQuizModalOpen} 
        onClose={() => setIsQuizModalOpen(false)} 
        nodeId={nodeId} 
      />
      
      <GitHubVerificationModal 
        isOpen={isGitHubModalOpen} 
        onClose={() => setIsGitHubModalOpen(false)} 
        nodeId={nodeId} 
      />
    </div>
  );
}
