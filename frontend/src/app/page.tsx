"use client";

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useRoadmapStore } from '@/store/useRoadmapStore';
import { GoalChat } from '@/components/chat/GoalChat';
import { RoadmapCanvas } from '@/components/roadmap/RoadmapCanvas';
import { LearnerDashboard } from '@/components/dashboard/LearnerDashboard';
import { NodeInspectorDrawer } from '@/components/roadmap/NodeInspectorDrawer';
import { createClient } from '@/lib/supabase/client';

export default function Home() {
  const { roadmap, initializeState, isLoading, reset } = useRoadmapStore();
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const router = useRouter();
  const supabase = createClient();

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
      <main className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-pulse flex flex-col items-center">
          <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
          <p className="text-muted-foreground">Loading your learning space...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background text-foreground p-4 md:p-8 flex flex-col items-center">
      
      {!roadmap ? (
        // Initial state: Only show Goal Chat vertically centered
        <div className="flex-1 flex flex-col justify-center items-center w-full max-w-4xl relative">
          <div className="w-full flex justify-end items-center gap-3 mb-2">
            {userEmail && (
              <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-xs text-primary font-medium">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                {userEmail}
              </div>
            )}
            <button 
              onClick={handleSignOut}
              className="text-xs px-3 py-1.5 rounded-md bg-secondary/50 hover:bg-destructive/20 hover:text-destructive text-muted-foreground transition-colors"
            >
              Sign Out
            </button>
          </div>
          <div className="text-center mb-8 mt-4">
            <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight mb-4 text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
              AI Pathfinder
            </h1>
            <p className="text-muted-foreground text-lg md:text-xl max-w-2xl mx-auto">
              Tell us what you want to learn. Our AI agents will instantly synthesize a personalized, interactive curriculum.
            </p>
          </div>
          <GoalChat />
        </div>
      ) : (
        // Roadmap state: Show Dashboard, Canvas, and keep GoalChat at the bottom or top
        <div className="w-full max-w-7xl flex flex-col gap-8 animate-in fade-in zoom-in duration-500">
          <header className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
              AI Pathfinder
            </h1>
            <div className="flex items-center gap-3">
              {userEmail && (
                <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-xs text-primary font-medium">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                  {userEmail}
                </div>
              )}
              <button 
                onClick={handleSignOut}
                className="text-sm px-4 py-2 rounded-md bg-secondary text-secondary-foreground hover:bg-destructive/20 hover:text-destructive transition-colors"
              >
                Sign Out
              </button>
            </div>
          </header>
          
          <LearnerDashboard />
          
          <div className="w-full relative shadow-[0_0_50px_rgba(var(--primary),0.1)] rounded-lg">
            <RoadmapCanvas />
          </div>

          <div className="w-full max-w-2xl mx-auto mt-8">
            <GoalChat />
          </div>

          <NodeInspectorDrawer />
        </div>
      )}

    </main>
  );
}
