import React from 'react';
import { Metadata } from 'next';
import { RoadmapCanvas } from '@/components/roadmap/RoadmapCanvas';
import { notFound } from 'next/navigation';
import { GenerateRoadmapResponse } from '@/lib/types';

export const dynamic = 'force-dynamic';

// Dynamically generate OpenGraph metadata based on the user's roadmap
export async function generateMetadata({ params }: { params: Promise<{ username: string }> }): Promise<Metadata> {
  const { username } = await params;
  const roadmapData = await fetchRoadmap(username);
  
  if (!roadmapData) {
    return { title: 'Roadmap Not Found' };
  }

  const { roadmap } = roadmapData;
  const title = `${username}'s Path to ${roadmap.target_role} | AI Pathfinder`;
  const description = `Follow ${username}'s interactive learning journey. ${roadmap.learner_summary}`;
  
  return {
    title,
    description,
    openGraph: {
      title,
      description,
      type: 'website',
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
    }
  };
}

async function fetchRoadmap(username: string): Promise<GenerateRoadmapResponse | null> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
  try {
    const res = await fetch(`${apiUrl}/public/roadmap/${username}`, {
      next: { revalidate: 60 } // Cache for 60 seconds
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.error(err);
    return null;
  }
}

export default async function PublicRoadmapPage({ params }: { params: Promise<{ username: string }> }) {
  const { username } = await params;
  const data = await fetchRoadmap(username);

  if (!data) {
    notFound();
  }

  return (
    <main className="min-h-screen bg-background text-foreground p-4 md:p-8 flex flex-col items-center">
      <div className="w-full max-w-7xl flex flex-col gap-6">
        <header className="flex justify-between items-center pb-4 border-b border-border/60">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-primary text-primary-foreground flex items-center justify-center font-bold text-xs tracking-wider">
              PF
            </div>
            <div>
              <h1 className="text-lg font-bold text-foreground tracking-tight font-sans">
                PATHFINDER
              </h1>
              <p className="text-xs text-muted-foreground">
                Public Learner Portfolio: @{username}
              </p>
            </div>
          </div>
        </header>

        <div className="bg-card border border-border p-6 rounded-2xl shadow-xs">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Curriculum Track
            </span>
          </div>
          <h2 className="text-xl font-bold text-foreground mb-1">Path to {data.roadmap.target_role}</h2>
          <p className="text-xs text-muted-foreground leading-relaxed">{data.roadmap.learner_summary}</p>
        </div>
        
        <div className="w-full rounded-2xl overflow-hidden border border-border shadow-xs">
           <RoadmapCanvas readOnly={true} readOnlyRoadmap={data.roadmap} />
        </div>
      </div>
    </main>
  );
}
