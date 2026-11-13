"use client";

import React, { useEffect, useState } from 'react';
import { useRoadmapStore } from '@/store/useRoadmapStore';
import {
  Sheet,
  SheetContent,
} from '@/components/ui/sheet';
import { MilestoneStudioPane } from './MilestoneStudioPane';

export function NodeInspectorDrawer() {
  const { activeNodeId, setActiveNode } = useRoadmapStore();
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 1024);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  if (!isMobile) return null;

  return (
    <Sheet open={isMobile && !!activeNodeId} onOpenChange={(open) => !open && setActiveNode(null)}>
      <SheetContent className="w-full sm:max-w-lg p-0 bg-background border-l-border flex flex-col h-full overflow-hidden lg:hidden">
        <MilestoneStudioPane />
      </SheetContent>
    </Sheet>
  );
}
