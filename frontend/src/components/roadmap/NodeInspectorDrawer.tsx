"use client";

import React from 'react';
import { useRoadmapStore } from '@/store/useRoadmapStore';
import {
  Sheet,
  SheetContent,
} from '@/components/ui/sheet';
import { MilestoneStudioPane } from './MilestoneStudioPane';

export function NodeInspectorDrawer() {
  const { activeNodeId, setActiveNode } = useRoadmapStore();

  return (
    <Sheet open={!!activeNodeId} onOpenChange={(open) => !open && setActiveNode(null)}>
      <SheetContent className="w-full sm:max-w-lg p-0 bg-background border-l-border flex flex-col h-full overflow-hidden">
        <MilestoneStudioPane />
      </SheetContent>
    </Sheet>
  );
}
