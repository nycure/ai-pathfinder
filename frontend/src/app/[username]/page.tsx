import React from 'react';
import { Metadata } from 'next';
import { RoadmapCanvas } from '@/components/roadmap/RoadmapCanvas';
import { notFound } from 'next/navigation';
import { GenerateRoadmapResponse } from '@/lib/types';

// Dynamically generate OpenGraph metadata based on the user's roadmap
export async function generateMetadata({ params }: { params: Promise<{ username: string }> | { username: string } }): Promise<Metadata> {
  const { username } = await Promise.resolve(params);
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

export default async function PublicRoadmapPage({ params }: { params: Promise<{ username: string }> | { username: string } }) {
  const { username } = await Promise.resolve(params);
  const data = await fetchRoadmap(username);

  if (!data) {
    notFound();
  }

  return (
    <main className="min-h-screen bg-background text-foreground p-4 md:p-8 flex flex-col items-center">
      <div className="w-full max-w-7xl flex flex-col gap-8">
        <header className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
              AI Pathfinder
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              Public Portfolio: @{username}
            </p>
          </div>
        </header>

        <div className="bg-card/60 backdrop-blur-xl border border-border p-6 rounded-lg shadow-sm">
          <h2 className="text-xl font-semibold mb-2">Path to {data.roadmap.target_role}</h2>
          <p className="text-muted-foreground">{data.roadmap.learner_summary}</p>
        </div>
        
        
        <div className="w-full relative shadow-[0_0_50px_rgba(var(--primary),0.1)] rounded-lg">
           <RoadmapCanvas readOnly={true} readOnlyRoadmap={data.roadmap} />
        </div>
      </div>
    </main>
  );
}
