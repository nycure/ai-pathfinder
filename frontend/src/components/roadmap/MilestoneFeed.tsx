"use client";

import React, { useState, useMemo } from 'react';
import { useRoadmapStore } from '@/store/useRoadmapStore';
import { 
  Search, 
  ChevronDown, 
  Globe, 
  CheckCircle2, 
  Lock, 
  PlayCircle, 
  RotateCw, 
  BookOpen, 
  Clock 
} from 'lucide-react';
import { RoadmapNode } from '@/lib/types';

interface MilestoneFeedProps {
  onSelectMilestone: (nodeId: string) => void;
}

export function MilestoneFeed({ onSelectMilestone }: MilestoneFeedProps) {
  const { roadmap, activeNodeId, recalibrateRoadmap, isLoading } = useRoadmapStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [filterPhase, setFilterPhase] = useState<string>('all');
  const [activeTab, setActiveTab] = useState<'all' | 'uncompleted'>('all');

  const nodes = useMemo(() => roadmap?.nodes || [], [roadmap]);

  // Extract unique phases
  const phases = useMemo(() => {
    const set = new Set<string>();
    nodes.forEach(n => {
      const p = n.data.phase_title || `Phase ${n.data.phase}`;
      if (p) set.add(p);
    });
    return Array.from(set);
  }, [nodes]);

  // Filter nodes based on search, phase, and status
  const filteredNodes = useMemo(() => {
    return nodes.filter(node => {
      const matchesSearch = 
        node.data.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
        node.data.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        node.data.skills_acquired.some(s => s.toLowerCase().includes(searchQuery.toLowerCase()));

      const phaseName = node.data.phase_title || `Phase ${node.data.phase}`;
      const matchesPhase = filterPhase === 'all' || phaseName === filterPhase;

      const matchesTab = activeTab === 'all' || (activeTab === 'uncompleted' && node.data.status !== 'completed');

      return matchesSearch && matchesPhase && matchesTab;
    });
  }, [nodes, searchQuery, filterPhase, activeTab]);

  const completedCount = nodes.filter(n => n.data.status === 'completed').length;

  if (!roadmap) return null;

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Top Header Row */}
      <div className="h-16 px-6 flex items-center justify-between border-b border-border/60 shrink-0">
        <div className="flex items-center gap-3">
          <h2 className="text-xl font-bold tracking-tight text-foreground">
            Curriculum
          </h2>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-muted/70 text-xs font-medium text-muted-foreground">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse"></span>
            <span>Radar Active · {roadmap.total_estimated_weeks}w</span>
          </div>
        </div>

        <button
          onClick={() => recalibrateRoadmap()}
          disabled={isLoading}
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-primary text-primary-foreground text-xs font-semibold shadow-xs hover:bg-primary/90 transition-all disabled:opacity-50"
        >
          <RotateCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Sync Path</span>
        </button>
      </div>

      {/* Controls & Filter Bar */}
      <div className="p-4 border-b border-border/60 space-y-3 shrink-0">
        {/* Capsule Segmented Tabs */}
        <div className="inline-flex w-full p-1 rounded-xl bg-muted/80 text-xs font-medium text-muted-foreground">
          <button
            onClick={() => setActiveTab('all')}
            className={`flex-1 py-1.5 rounded-lg transition-all ${
              activeTab === 'all' 
                ? 'bg-card text-foreground font-semibold shadow-xs' 
                : 'hover:text-foreground'
            }`}
          >
            All Milestones ({nodes.length})
          </button>
          <button
            onClick={() => setActiveTab('uncompleted')}
            className={`flex-1 py-1.5 rounded-lg transition-all ${
              activeTab === 'uncompleted' 
                ? 'bg-card text-foreground font-semibold shadow-xs' 
                : 'hover:text-foreground'
            }`}
          >
            In Progress & Up Next ({nodes.length - completedCount})
          </button>
        </div>

        {/* Search & Category Filter */}
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search concepts, skills, phases..."
              className="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg border border-border bg-card placeholder:text-muted-foreground/60 text-foreground focus:outline-none focus:ring-1 focus:ring-foreground/20"
            />
          </div>

          <div className="relative shrink-0">
            <select
              value={filterPhase}
              onChange={(e) => setFilterPhase(e.target.value)}
              className="appearance-none pl-3 pr-7 py-1.5 text-xs rounded-lg border border-border bg-card text-foreground focus:outline-none focus:ring-1 focus:ring-foreground/20 cursor-pointer"
            >
              <option value="all">Category: All</option>
              {phases.map((p, i) => (
                <option key={i} value={p}>{p}</option>
              ))}
            </select>
            <ChevronDown className="w-3 h-3 absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
          </div>
        </div>
      </div>

      {/* Feed List Items */}
      <div className="flex-1 overflow-y-auto divide-y divide-border/60">
        {filteredNodes.length === 0 ? (
          <div className="p-8 text-center text-xs text-muted-foreground">
            No milestones match your search or filter.
          </div>
        ) : (
          filteredNodes.map((node, index) => {
            const isSelected = activeNodeId === node.id;
            const isCompleted = node.data.status === 'completed';
            const isLocked = node.data.status === 'locked';

            const globalIndex = nodes.findIndex(n => n.id === node.id);

            return (
              <div
                key={node.id}
                onClick={() => onSelectMilestone(node.id)}
                className={`p-4 transition-colors cursor-pointer group flex items-start gap-3 ${
                  isSelected 
                    ? 'bg-card/90 ring-1 ring-border' 
                    : 'hover:bg-card/50'
                }`}
              >
                {/* Number Rank */}
                <span className="text-xs font-semibold text-muted-foreground/80 w-6 shrink-0 pt-0.5">
                  {(globalIndex >= 0 ? globalIndex : index) + 1}.
                </span>

                {/* Main Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <h3 className={`text-sm font-semibold leading-tight line-clamp-1 ${
                      isSelected ? 'text-foreground' : 'text-foreground/90 group-hover:text-foreground'
                    }`}>
                      {node.data.label}
                    </h3>
                  </div>

                  <p className="text-xs text-muted-foreground line-clamp-2 mt-1 leading-relaxed">
                    {node.data.description}
                  </p>

                  {/* Metadata & Tag */}
                  <div className="flex items-center gap-3 mt-2 text-[11px] text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Globe className="w-3 h-3 text-muted-foreground/70" />
                      <span className="truncate max-w-[140px]">
                        {node.data.primary_resource?.provider || 'Core Curriculum'}
                      </span>
                    </div>
                    <span>•</span>
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3 text-muted-foreground/70" />
                      <span>{node.data.estimated_weeks}w</span>
                    </div>
                    <span>•</span>
                    <span className="capitalize">{node.data.difficulty}</span>
                  </div>
                </div>

                {/* Action CTA Button */}
                <div className="shrink-0 pt-0.5">
                  {isCompleted ? (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectMilestone(node.id);
                      }}
                      className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-medium border transition-colors ${
                        isSelected 
                          ? 'bg-foreground text-background border-foreground font-semibold' 
                          : 'bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border-emerald-200'
                      }`}
                    >
                      <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                      <span>Review</span>
                    </button>
                  ) : isLocked ? (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-muted/60 text-muted-foreground text-[11px] font-medium">
                      <Lock className="w-3 h-3" />
                      <span>Locked</span>
                    </span>
                  ) : (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectMilestone(node.id);
                      }}
                      className={`px-3 py-1 rounded-md text-xs font-medium border transition-colors ${
                        isSelected 
                          ? 'bg-foreground text-background border-foreground font-semibold' 
                          : 'bg-card hover:bg-muted text-foreground border-border'
                      }`}
                    >
                      {isSelected ? 'Active' : 'Inspect'}
                    </button>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
