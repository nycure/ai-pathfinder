"use client";

import React, { useState } from 'react';
import { useRoadmapStore } from '@/store/useRoadmapStore';
import { 
  FileEdit, 
  ExternalLink, 
  Sparkles, 
  Clock, 
  CheckCircle2, 
  BrainCircuit, 
  RotateCcw, 
  Send, 
  GraduationCap, 
  GitBranch, 
  MessageSquare,
  Lock,
  Star
} from 'lucide-react';
import { MilestoneChatTutor } from './MilestoneChatTutor';
import { MasteryQuizModal } from './MasteryQuizModal';
import { GitHubVerificationModal } from './GitHubVerificationModal';

export function MilestoneStudioPane() {
  const { activeNodeId, setActiveNode, roadmap, profile, submitFeedback, isLoading } = useRoadmapStore();
  const [activeTab, setActiveTab] = useState<'overview' | 'tutor' | 'feedback'>('overview');
  const [feedbackText, setFeedbackText] = useState('');
  const [isQuizOpen, setIsQuizOpen] = useState(false);
  const [isGitHubOpen, setIsGitHubOpen] = useState(false);

  const nodes = roadmap?.nodes || [];
  
  // Find current node, or fallback to the first active/available one
  const activeNode = nodes.find(n => n.id === activeNodeId) || nodes.find(n => n.data.status !== 'completed') || nodes[0];
  const activeIndex = activeNode ? nodes.findIndex(n => n.id === activeNode.id) : 0;

  if (!roadmap || !activeNode) {
    return (
      <div className="h-full rounded-2xl border border-border bg-card p-8 flex flex-col items-center justify-center text-center">
        <Sparkles className="w-8 h-8 text-muted-foreground/60 mb-3" />
        <h3 className="text-sm font-semibold text-foreground">No Milestone Selected</h3>
        <p className="text-xs text-muted-foreground mt-1 max-w-xs">
          Select a milestone from the curriculum feed to inspect details, chat with the AI tutor, or verify mastery.
        </p>
      </div>
    );
  }

  const { data } = activeNode;
  const isCompleted = data.status === 'completed';
  const isLocked = data.status === 'locked';

  const handleFeedbackSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!feedbackText.trim() || isLoading) return;
    const contextPrefix = `Regarding milestone '${data.label}': `;
    await submitFeedback(contextPrefix + feedbackText);
    setFeedbackText('');
  };

  return (
    <div className="h-full rounded-2xl border border-border bg-card shadow-xs flex flex-col overflow-hidden">
      {/* Studio Header Row */}
      <div className="px-6 py-4 border-b border-border/60 flex items-center justify-between shrink-0 bg-card">
        <div className="flex items-center gap-2">
          <FileEdit className="w-4 h-4 text-foreground" />
          <h2 className="text-sm font-bold tracking-tight text-foreground">
            Milestone Studio
          </h2>
        </div>

        {/* Phase / Topic Tag */}
        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-foreground text-background text-xs font-semibold">
          <span className="w-1.5 h-1.5 rounded-full bg-background"></span>
          <span className="truncate max-w-[150px]">
            {data.phase_title || `Phase ${data.phase}`}
          </span>
        </div>
      </div>

      {/* Main Studio Body (Scrollable) */}
      <div className="flex-1 overflow-y-auto p-6 space-y-5">
        {/* Title & Metadata */}
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Phase {data.phase} • {data.difficulty}
            </span>
            {isCompleted && (
              <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                <CheckCircle2 className="w-3 h-3" /> Mastered
              </span>
            )}
          </div>
          <h1 className="text-xl font-bold tracking-tight text-foreground leading-snug">
            {data.label}
          </h1>
          <p className="text-xs text-muted-foreground mt-2 leading-relaxed">
            {data.description}
          </p>
        </div>

        {/* Nested Quote / Resource Box (Muted Taupe styled like reference image) */}
        {data.primary_resource && (
          <div className="rounded-xl bg-muted/60 border border-border p-4 relative group">
            <div className="flex items-start justify-between gap-3">
              <div className="space-y-1">
                <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground block">
                  Curated Resource Hook
                </span>
                <a
                  href={data.primary_resource.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs font-semibold text-foreground hover:underline flex items-center gap-1.5 leading-snug"
                >
                  <span>{data.primary_resource.title}</span>
                  <ExternalLink className="w-3 h-3 text-muted-foreground shrink-0" />
                </a>
                <div className="flex items-center gap-2 text-[11px] text-muted-foreground pt-0.5">
                  <span className="font-medium text-foreground/80">{data.primary_resource.provider}</span>
                  <span>•</span>
                  <span>~{data.primary_resource.estimated_hours}h</span>
                  <span>•</span>
                  <span className="capitalize">{data.primary_resource.cost}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Studio Sub-Navigation Tabs */}
        <div className="inline-flex w-full p-1 rounded-xl bg-muted/70 text-xs font-medium text-muted-foreground">
          <button
            onClick={() => setActiveTab('overview')}
            className={`flex-1 py-1.5 rounded-lg transition-all ${
              activeTab === 'overview' 
                ? 'bg-card text-foreground font-semibold shadow-xs' 
                : 'hover:text-foreground'
            }`}
          >
            Overview & XAI
          </button>
          <button
            onClick={() => {
              setActiveNode(activeNode.id);
              setActiveTab('tutor');
            }}
            className={`flex-1 py-1.5 rounded-lg transition-all ${
              activeTab === 'tutor' 
                ? 'bg-card text-foreground font-semibold shadow-xs' 
                : 'hover:text-foreground'
            }`}
          >
            AI Tutor
          </button>
          <button
            onClick={() => setActiveTab('feedback')}
            className={`flex-1 py-1.5 rounded-lg transition-all ${
              activeTab === 'feedback' 
                ? 'bg-card text-foreground font-semibold shadow-xs' 
                : 'hover:text-foreground'
            }`}
          >
            Adapt Path
          </button>
        </div>

        {/* Tab 1: Overview & XAI */}
        {activeTab === 'overview' && (
          <div className="space-y-4">
            {/* Acquired Skills Pills */}
            <div>
              <span className="text-xs font-semibold text-foreground block mb-2">
                Target Competencies
              </span>
              <div className="flex flex-wrap gap-1.5">
                {data.skills_acquired.map(skill => (
                  <span
                    key={skill}
                    className="text-[11px] px-2.5 py-1 rounded-md bg-muted/80 text-foreground border border-border/60"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Explainable AI Callout */}
            <div className="rounded-xl border border-border p-3.5 bg-card/60 space-y-2">
              <div className="flex items-center gap-1.5 text-xs font-semibold text-foreground">
                <BrainCircuit className="w-3.5 h-3.5" />
                <span>Why this step in your sequence?</span>
              </div>
              <p className="text-xs text-muted-foreground leading-relaxed">
                {data.why_recommended}
              </p>
            </div>

            {/* Alternative Resources */}
            {data.alternative_resources && data.alternative_resources.length > 0 && (
              <div className="space-y-2 pt-2">
                <span className="text-xs font-semibold text-foreground block">
                  Alternative Materials
                </span>
                <div className="space-y-2">
                  {data.alternative_resources.map(res => (
                    <a
                      key={res.id}
                      href={res.url}
                      target="_blank"
                      rel="noreferrer"
                      className="block p-2.5 rounded-lg border border-border bg-card hover:bg-muted/40 transition-colors"
                    >
                      <div className="flex items-center justify-between text-xs font-medium text-foreground">
                        <span className="truncate">{res.title}</span>
                        <ExternalLink className="w-3 h-3 text-muted-foreground shrink-0 ml-2" />
                      </div>
                      <div className="text-[10px] text-muted-foreground mt-0.5">
                        {res.provider} • {res.type} • {res.cost}
                      </div>
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tab 2: AI Tutor */}
        {activeTab === 'tutor' && (
          <div className="h-[360px] flex flex-col border border-border rounded-xl overflow-hidden bg-card">
            <MilestoneChatTutor />
          </div>
        )}

        {/* Tab 3: Adapt / Feedback */}
        {activeTab === 'feedback' && (
          <form onSubmit={handleFeedbackSubmit} className="space-y-3">
            <span className="text-xs font-semibold text-foreground block">
              Customize or Reposition this Topic
            </span>
            <p className="text-xs text-muted-foreground">
              Already familiar with this? Need more hands-on labs or want to swap frameworks? Tell our adaptation agent:
            </p>
            <textarea
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              placeholder="E.g., I already know this well, skip to advanced topics, or give me more practice with PyTorch..."
              rows={3}
              className="w-full p-3 text-xs rounded-xl border border-border bg-card text-foreground focus:outline-none focus:ring-1 focus:ring-foreground/20 resize-none"
            />
            <button
              type="submit"
              disabled={isLoading || !feedbackText.trim()}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-foreground text-background text-xs font-semibold hover:bg-foreground/90 disabled:opacity-50 transition-all"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Submit & Adapt</span>
            </button>
          </form>
        )}
      </div>

      {/* Footer Action Bar */}
      <div className="p-4 border-t border-border/60 bg-card flex items-center justify-between shrink-0">
        {/* Step Counter */}
        <div className="text-xs font-medium text-muted-foreground">
          Step <span className="font-bold text-foreground">{activeIndex + 1}</span> / {nodes.length}
        </div>

        {/* Dual-Track Active Validation Buttons */}
        <div className="flex items-center gap-2">
          {isCompleted ? (
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs font-semibold shadow-xs">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>Mastered</span>
              </span>
              <button
                onClick={() => setIsQuizOpen(true)}
                disabled={isLoading}
                className="px-2.5 py-1.5 rounded-lg border border-border bg-card hover:bg-muted text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
                title="Retake Quiz for revision"
              >
                Retake Quiz
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsQuizOpen(true)}
                disabled={isLoading || isLocked}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-foreground text-background hover:bg-foreground/90 text-xs font-semibold shadow-xs transition-all disabled:opacity-50"
              >
                <GraduationCap className="w-3.5 h-3.5" />
                <span>Take Quiz</span>
              </button>

              <button
                onClick={() => setIsGitHubOpen(true)}
                disabled={isLoading || isLocked}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border bg-card hover:bg-muted text-xs font-medium text-foreground transition-colors disabled:opacity-50"
              >
                <GitBranch className="w-3.5 h-3.5 text-muted-foreground" />
                <span>Verify GitHub</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Verification Modals */}
      <MasteryQuizModal
        isOpen={isQuizOpen}
        onClose={() => setIsQuizOpen(false)}
        nodeId={activeNode.id}
      />

      <GitHubVerificationModal
        isOpen={isGitHubOpen}
        onClose={() => setIsGitHubOpen(false)}
        nodeId={activeNode.id}
      />
    </div>
  );
}
