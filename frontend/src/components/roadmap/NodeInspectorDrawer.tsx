"use client";

import React, { useEffect, useState } from 'react';
import { useRoadmapStore } from '@/store/useRoadmapStore';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from '@/components/ui/sheet';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { BrainCircuit, ExternalLink, PlayCircle, Star, Clock, MessageCircleQuestion } from 'lucide-react';
import { api } from '@/lib/api';
import { ExplainabilityResponse } from '@/lib/types';
import { AdaptationControls } from './AdaptationControls';
import { MilestoneChatTutor } from './MilestoneChatTutor';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export function NodeInspectorDrawer() {
  const { activeNodeId, setActiveNode, roadmap, profile } = useRoadmapStore();
  const [xaiData, setXaiData] = useState<ExplainabilityResponse | null>(null);
  const [isXaiLoading, setIsXaiLoading] = useState(false);

  const activeNode = roadmap?.nodes.find((n) => n.id === activeNodeId);

  useEffect(() => {
    if (activeNodeId && roadmap && profile) {
      // Lazy load the deep XAI justification from the backend
      const fetchXai = async () => {
        setIsXaiLoading(true);
        try {
          const data = await api.explainNode(activeNodeId, profile, roadmap);
          setXaiData(data);
        } catch (error) {
          console.error("Failed to fetch XAI data:", error);
        } finally {
          setIsXaiLoading(false);
        }
      };
      
      // Clear previous
      setXaiData(null);
      fetchXai();
    }
  }, [activeNodeId, roadmap, profile]);

  if (!activeNode) return null;

  const data = activeNode.data;

  return (
    <Sheet open={!!activeNodeId} onOpenChange={(open) => !open && setActiveNode(null)}>
      <SheetContent className="w-full sm:max-w-md lg:max-w-lg border-l-border bg-background/95 backdrop-blur-xl p-0 flex flex-col">
        <ScrollArea className="h-full px-6 py-6">
          <SheetHeader className="mb-6">
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="outline" className="text-xs uppercase bg-primary/10 text-primary border-primary/20">
                Phase {data.phase}: {data.phase_title}
              </Badge>
              <Badge variant="secondary" className="capitalize">
                {data.status.replace("_", " ")}
              </Badge>
            </div>
            <SheetTitle className="text-2xl font-bold">{data.label}</SheetTitle>
            <SheetDescription className="text-base mt-2">
              {data.description}
            </SheetDescription>
          </SheetHeader>

          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-6">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="tutor" className="flex gap-2">
                <MessageCircleQuestion className="w-4 h-4" /> AI Tutor
              </TabsTrigger>
            </TabsList>

            <TabsContent value="overview">
              {/* Explainable AI (XAI) Section */}
              <Card className="mb-6 border-accent/50 bg-accent/5 shadow-[0_0_20px_rgba(var(--accent),0.1)]">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-semibold flex items-center gap-2 text-accent">
                    <BrainCircuit className="w-4 h-4" />
                    Why was this recommended for you?
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {isXaiLoading ? (
                    <div className="animate-pulse flex flex-col gap-2">
                      <div className="h-4 bg-muted rounded w-3/4"></div>
                      <div className="h-4 bg-muted rounded w-1/2"></div>
                    </div>
                  ) : xaiData ? (
                    <div className="space-y-4">
                      <p className="text-sm text-muted-foreground leading-relaxed">
                        {xaiData.justification}
                      </p>
                      {xaiData.missing_prerequisites_for_this_node.length > 0 && (
                        <div className="mt-3">
                          <span className="text-xs font-semibold text-destructive uppercase tracking-wider block mb-2">
                            Missing Prerequisites
                          </span>
                          <ul className="list-disc pl-4 text-sm text-muted-foreground">
                            {xaiData.missing_prerequisites_for_this_node.map(prereq => (
                              <li key={prereq}>{prereq}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {data.why_recommended}
                    </p>
                  )}
                </CardContent>
              </Card>

              <Separator className="my-6 bg-border/50" />

              {/* Learning Resources */}
              <div className="space-y-4 mb-8">
                <h3 className="text-lg font-semibold tracking-tight">Curated Resources</h3>
                
                {data.primary_resource && (
                  <a 
                    href={data.primary_resource.url} 
                    target="_blank" 
                    rel="noreferrer"
                    className="block group"
                  >
                    <Card className="bg-primary/5 border-primary/20 hover:border-primary/50 hover:bg-primary/10 transition-colors">
                      <CardHeader className="p-4 pb-2">
                        <div className="flex justify-between items-start gap-2">
                          <CardTitle className="text-base group-hover:text-primary transition-colors flex items-center gap-2">
                            <PlayCircle className="w-4 h-4" />
                            {data.primary_resource.title}
                          </CardTitle>
                          <ExternalLink className="w-4 h-4 text-muted-foreground group-hover:text-primary shrink-0" />
                        </div>
                        <CardDescription className="text-xs flex items-center gap-2 mt-1">
                          <span className="font-medium text-foreground">{data.primary_resource.provider}</span>
                          <span>•</span>
                          <span className="flex items-center gap-1"><Star className="w-3 h-3 text-yellow-500" /> {data.primary_resource.rating}</span>
                          <span>•</span>
                          <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {data.primary_resource.estimated_hours}h</span>
                          <span>•</span>
                          <span className="capitalize">{data.primary_resource.cost}</span>
                        </CardDescription>
                      </CardHeader>
                    </Card>
                  </a>
                )}

                {data.alternative_resources && data.alternative_resources.length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-sm font-semibold text-muted-foreground mb-3">Alternative Options</h4>
                    <div className="flex flex-col gap-3">
                      {data.alternative_resources.map(res => (
                        <a 
                          key={res.id}
                          href={res.url} 
                          target="_blank" 
                          rel="noreferrer"
                          className="block group"
                        >
                          <Card className="bg-card hover:bg-muted/50 transition-colors border-border/50">
                            <CardHeader className="p-3">
                              <CardTitle className="text-sm group-hover:text-primary transition-colors flex items-center justify-between">
                                {res.title}
                                <ExternalLink className="w-3 h-3 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                              </CardTitle>
                              <CardDescription className="text-xs flex gap-2 mt-1">
                                <span>{res.provider}</span>
                                <span>•</span>
                                <span className="capitalize">{res.type}</span>
                                <span>•</span>
                                <span className="capitalize">{res.cost}</span>
                              </CardDescription>
                            </CardHeader>
                          </Card>
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <Separator className="my-6 bg-border/50" />

              {/* Dynamic Adaptation Controls */}
              <div className="mb-8">
                <h3 className="text-lg font-semibold tracking-tight mb-4">Milestone Actions</h3>
                <AdaptationControls nodeId={activeNode.id} data={data} />
              </div>
            </TabsContent>

            <TabsContent value="tutor">
              <MilestoneChatTutor />
            </TabsContent>
          </Tabs>

        </ScrollArea>
      </SheetContent>
    </Sheet>
  );
}
