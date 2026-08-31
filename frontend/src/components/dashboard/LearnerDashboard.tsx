"use client";

import React, { useMemo, useEffect, useState } from 'react';
import { useRoadmapStore } from '@/store/useRoadmapStore';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts';
import { Target, Trophy, Clock, Brain, CalendarPlus, RefreshCw, Loader2, Users } from 'lucide-react';

export function LearnerDashboard() {
  const { roadmap, profile, syncCalendar, recalibrateRoadmap, isLoading } = useRoadmapStore();
  const [cohortData, setCohortData] = useState<any>(null);

  useEffect(() => {
    async function fetchCohort() {
      try {
        const data = await api.getMyCohort();
        setCohortData(data);
      } catch (err) {
        console.error("Failed to fetch cohort", err);
      }
    }
    if (roadmap) {
      fetchCohort();
    }
  }, [roadmap]);

  const analytics = useMemo(() => {
    if (!roadmap) return null;

    const totalNodes = roadmap.nodes.length;
    const completedNodes = roadmap.nodes.filter(n => n.data.status === 'completed').length;
    const progressPercent = totalNodes > 0 ? (completedNodes / totalNodes) * 100 : 0;

    // Dynamically group milestones by Phase Title
    const phaseMap: Record<string, { total: number; completed: number }> = {};

    roadmap.nodes.forEach(node => {
      const phaseName = node.data.phase_title || `Phase ${node.data.phase}`;
      if (!phaseMap[phaseName]) {
        phaseMap[phaseName] = { total: 0, completed: 0 };
      }
      phaseMap[phaseName].total += 1;
      if (node.data.status === 'completed') {
        phaseMap[phaseName].completed += 1;
      }
    });

    let radarData = Object.entries(phaseMap).map(([subject, stats]) => ({
      subject,
      A: stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0,
      fullMark: 100
    }));

    // If fewer than 3 dimensions, ensure minimum 4 axes for proper radar geometry
    if (radarData.length < 3) {
      const defaultDimensions = ['Foundations', 'Core Concepts', 'Applied Practice', 'Advanced Mastery'];
      radarData = defaultDimensions.map((subject, idx) => {
        const matching = radarData[idx];
        return matching || { subject, A: Math.round(progressPercent), fullMark: 100 };
      });
    }

    return {
      totalNodes,
      completedNodes,
      progressPercent,
      radarData
    };
  }, [roadmap, profile]);

  if (!roadmap || !analytics) {
    return null;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
      {/* High Level Stats */}
      <Card className="col-span-1 md:col-span-2 bg-card/60 backdrop-blur-xl border-border shadow-lg">
        <CardHeader>
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <CardTitle className="text-xl flex items-center gap-2 text-primary">
                <Target className="w-5 h-5" />
                Path to: {roadmap.target_role}
              </CardTitle>
              <CardDescription className="mt-1">{roadmap.learner_summary}</CardDescription>
            </div>
            <div className="flex gap-2 shrink-0">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => syncCalendar()}
                disabled={isLoading}
                className="text-xs border-primary/20 hover:bg-primary/10"
              >
                <CalendarPlus className="w-3.5 h-3.5 mr-2" />
                Add to Calendar
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => recalibrateRoadmap()}
                disabled={isLoading}
                className="text-xs border-accent/20 hover:bg-accent/10"
              >
                {isLoading ? <Loader2 className="w-3.5 h-3.5 mr-2 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5 mr-2" />}
                Recalibrate
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="flex flex-col gap-1 p-3 bg-background rounded-lg border border-border/50">
              <span className="text-xs text-muted-foreground uppercase tracking-wider flex items-center gap-1"><Clock className="w-3 h-3"/> Weeks</span>
              <span className="text-2xl font-bold">{roadmap.total_estimated_weeks}</span>
            </div>
            <div className="flex flex-col gap-1 p-3 bg-background rounded-lg border border-border/50">
              <span className="text-xs text-muted-foreground uppercase tracking-wider flex items-center gap-1"><Clock className="w-3 h-3"/> Hours</span>
              <span className="text-2xl font-bold">{roadmap.total_hours}</span>
            </div>
            <div className="flex flex-col gap-1 p-3 bg-background rounded-lg border border-border/50">
              <span className="text-xs text-muted-foreground uppercase tracking-wider flex items-center gap-1"><Trophy className="w-3 h-3 text-yellow-500"/> Milestones</span>
              <span className="text-2xl font-bold">{analytics.completedNodes} / {analytics.totalNodes}</span>
            </div>
            <div className="flex flex-col gap-1 p-3 bg-background rounded-lg border border-border/50">
              <span className="text-xs text-muted-foreground uppercase tracking-wider flex items-center gap-1"><Brain className="w-3 h-3 text-accent"/> Pace</span>
              <span className="text-2xl font-bold capitalize">{profile?.learning_pace || 'Medium'}</span>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-sm font-medium">
              <span>Overall Completion</span>
              <span>{Math.round(analytics.progressPercent)}%</span>
            </div>
            <Progress value={analytics.progressPercent} className="h-2 bg-muted">
              <div className="h-full bg-primary rounded-full transition-all duration-500 ease-in-out" style={{ width: `${analytics.progressPercent}%` }} />
            </Progress>
          </div>
        </CardContent>
      </Card>

      {/* Radar Chart */}
      <Card className="col-span-1 bg-card/60 backdrop-blur-xl border-border shadow-lg">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Skill Distribution</CardTitle>
        </CardHeader>
        <CardContent className="h-[250px] w-full pt-0">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="70%" data={analytics.radarData}>
              <PolarGrid stroke="oklch(1 0 0 / 10%)" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: 'oklch(0.7 0.05 250)', fontSize: 10 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
              <Radar
                name="Proficiency"
                dataKey="A"
                stroke="oklch(0.65 0.25 250)" // Primary
                fill="oklch(0.65 0.25 250)"
                fillOpacity={0.3}
              />
              <Tooltip 
                contentStyle={{ backgroundColor: 'oklch(0.12 0.01 250)', borderColor: 'oklch(1 0 0 / 10%)', borderRadius: '8px' }}
                itemStyle={{ color: 'oklch(0.98 0 0)' }}
              />
            </RadarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
      {/* Cohort Widget */}
      {cohortData && (
        <Card className="col-span-1 md:col-span-3 bg-card/60 backdrop-blur-xl border-border shadow-lg mt-6">
          <CardHeader>
            <CardTitle className="text-xl flex items-center gap-2 text-primary">
              <Users className="w-5 h-5" />
              Your Study Cohort: {cohortData.topic}
            </CardTitle>
            <CardDescription>Peers currently on a similar track as you.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-4">
              {cohortData.members.sort((a: any, b: any) => b.progress - a.progress).map((member: any, i: number) => (
                <div key={i} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center font-bold text-primary text-xs">
                      {member.username.substring(0, 2).toUpperCase()}
                    </div>
                    <span className={`font-medium ${member.is_me ? 'text-primary' : 'text-foreground'}`}>
                      @{member.username} {member.is_me && '(You)'}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 w-1/3">
                    <Progress value={member.progress} className="h-2 flex-1 bg-muted" />
                    <span className="text-sm font-semibold w-10 text-right">{member.progress}%</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
