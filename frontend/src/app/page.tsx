"use client";

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useRoadmapStore } from '@/store/useRoadmapStore';
import { GoalChat } from '@/components/chat/GoalChat';
import { RoadmapCanvas } from '@/components/roadmap/RoadmapCanvas';
import { LearnerDashboard } from '@/components/dashboard/LearnerDashboard';
import { NodeInspectorDrawer } from '@/components/roadmap/NodeInspectorDrawer';
import { AppSidebar } from '@/components/layout/AppSidebar';
import { MilestoneFeed } from '@/components/roadmap/MilestoneFeed';
import { MilestoneStudioPane } from '@/components/roadmap/MilestoneStudioPane';
import { createClient } from '@/lib/supabase/client';
import { LogOut, Compass, GitFork, Activity } from 'lucide-react';

export default function Home() {
  const { roadmap, initializeState, isLoading, reset, setActiveNode } = useRoadmapStore();
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [activeView, setActiveView] = useState<'feed' | 'canvas' | 'analytics'>('feed');
  const [isMobile, setIsMobile] = useState(false);
  const router = useRouter();
  const supabase = createClient();

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 1024);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (user) {
        setUserEmail(user.email ?? user.user_metadata?.username ?? 'Learner');
      } else {
        router.push('/login');
      }
    });
    initializeState();
  }, [initializeState, router, supabase]);

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    reset();
    router.push('/login');
    router.refresh();
  };

  if (isLoading && !roadmap) {
    return (
      <main className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="flex flex-col items-center gap-3">
          <div className="w-9 h-9 border-3 border-border border-t-foreground rounded-full animate-spin"></div>
          <p className="text-xs font-medium text-muted-foreground">Loading your workspace...</p>
        </div>
      </main>
    );
  }

  // Initial State: Goal Creation Prompt
  if (!roadmap) {
    return (
      <main className="min-h-screen bg-background text-foreground flex flex-col justify-between p-6 md:p-12">
        {/* Top Header */}
        <header className="w-full max-w-4xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-primary text-primary-foreground flex items-center justify-center font-bold text-xs tracking-wider">
              PF
            </div>
            <span className="font-extrabold tracking-tight text-lg text-foreground font-sans">
              PATHFINDER
            </span>
          </div>

          <div className="flex items-center gap-3">
            {userEmail && (
              <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-card border border-border text-xs text-foreground font-medium">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
                <span>{userEmail}</span>
              </div>
            )}
            <button 
              onClick={handleSignOut}
              className="text-xs px-3 py-1.5 rounded-lg border border-border bg-card hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
            >
              Sign Out
            </button>
          </div>
        </header>

        {/* Center Prompt & Chat */}
        <div className="w-full max-w-3xl mx-auto my-auto py-12 flex flex-col items-center text-center">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-foreground mb-3 font-sans">
            AI Pathfinder
          </h1>
          <p className="text-sm md:text-base text-muted-foreground max-w-lg mb-8 leading-relaxed">
            Personalized, adaptive learning curricula generated in seconds. Tell us what you want to master.
          </p>

          <div className="w-full">
            <GoalChat />
          </div>
        </div>

        {/* Subtle Footer */}
        <footer className="w-full max-w-4xl mx-auto text-center text-[11px] text-muted-foreground/60">
          Powered by Gemini & Multi-Agent Curriculum Synthesis
        </footer>
      </main>
    );
  }

  // Active Roadmap State: 3-Column Editorial Workspace
  const totalNodes = roadmap.nodes.length;
  const completedNodes = roadmap.nodes.filter(n => n.data.status === 'completed').length;

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col lg:flex-row h-screen overflow-hidden">
      {/* Column 1: Navigation Sidebar (Desktop fixed) */}
      <div className="hidden lg:block shrink-0">
        <AppSidebar
          activeView={activeView}
          onSelectView={setActiveView}
          userEmail={userEmail}
          onSignOut={handleSignOut}
          completedCount={completedNodes}
          totalCount={totalNodes}
        />
      </div>

      {/* Mobile Header Bar */}
      <header className="lg:hidden h-14 px-4 border-b border-border bg-card flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-primary text-primary-foreground flex items-center justify-center font-bold text-[10px]">
            PF
          </div>
          <span className="font-extrabold text-sm tracking-tight">PATHFINDER</span>
        </div>

        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setActiveView('feed')}
            className={`px-2.5 py-1 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors ${
              activeView === 'feed' ? 'bg-primary text-primary-foreground font-semibold' : 'text-muted-foreground hover:bg-muted'
            }`}
          >
            <Compass className="w-3.5 h-3.5" />
            <span>Feed</span>
          </button>
          <button
            onClick={() => setActiveView('canvas')}
            className={`px-2.5 py-1 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors ${
              activeView === 'canvas' ? 'bg-primary text-primary-foreground font-semibold' : 'text-muted-foreground hover:bg-muted'
            }`}
          >
            <GitFork className="w-3.5 h-3.5" />
            <span>Graph</span>
          </button>
          <button
            onClick={() => setActiveView('analytics')}
            className={`px-2.5 py-1 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors ${
              activeView === 'analytics' ? 'bg-primary text-primary-foreground font-semibold' : 'text-muted-foreground hover:bg-muted'
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            <span>Analytics</span>
          </button>
          <button
            onClick={handleSignOut}
            title="Sign out"
            className="p-1.5 rounded-lg text-muted-foreground hover:text-destructive hover:bg-muted transition-colors ml-1"
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>
      </header>

      {/* Main Workspace Body */}
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* Column 2: Center Feed / Viewport */}
        {activeView === 'feed' && (
          <>
            {/* Center Feed List */}
            <div className="flex-1 lg:max-w-xl xl:max-w-2xl border-r border-border/60 h-full overflow-hidden flex flex-col">
              <MilestoneFeed onSelectMilestone={(nodeId) => setActiveNode(nodeId)} />
            </div>

            {/* Column 3: Right Studio Pane */}
            <div className="flex-1 p-6 h-full overflow-hidden hidden lg:block bg-background">
              <MilestoneStudioPane />
            </div>
          </>
        )}

        {/* Alternate View: Interactive Visual Graph */}
        {activeView === 'canvas' && (
          <div className="flex-1 flex flex-col lg:flex-row h-full overflow-hidden">
            <div className="flex-1 p-6 h-full overflow-hidden">
              <RoadmapCanvas />
            </div>
            <div className="w-[420px] p-6 h-full overflow-hidden hidden xl:block border-l border-border/60">
              <MilestoneStudioPane />
            </div>
          </div>
        )}

        {/* Alternate View: Cohort & Analytics Dashboard */}
        {activeView === 'analytics' && (
          <div className="flex-1 p-6 md:p-8 overflow-y-auto">
            <div className="max-w-5xl mx-auto space-y-6">
              <div className="flex items-center justify-between pb-4 border-b border-border">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight text-foreground">
                    Curriculum Analytics & Study Cohort
                  </h1>
                  <p className="text-xs text-muted-foreground mt-1">
                    Path to: {roadmap.target_role} • {roadmap.learner_summary}
                  </p>
                </div>
              </div>
              <LearnerDashboard />
            </div>
          </div>
        )}
      </div>

      {/* Slide-out drawer for Mobile fallback only */}
      {isMobile && <NodeInspectorDrawer />}
    </div>
  );
}
