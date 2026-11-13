import React from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Lock, CheckCircle2, PlayCircle, Clock } from 'lucide-react';
import { RoadmapNode } from '@/lib/types';

export function MilestoneNode({ data, selected }: NodeProps<RoadmapNode>) {
  const statusIcons = {
    locked: <Lock className="w-3.5 h-3.5 text-muted-foreground" />,
    available: <PlayCircle className="w-3.5 h-3.5 text-foreground" />,
    in_progress: <PlayCircle className="w-3.5 h-3.5 text-foreground" />,
    completed: <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
  };

  return (
    <div className="relative group min-w-[260px]">
      <Handle type="target" position={Position.Top} className="w-2.5 h-2.5 bg-foreground border border-card" />
      
      <Card className={`
        bg-card border-border transition-all duration-200 rounded-xl shadow-xs
        ${selected ? 'ring-2 ring-foreground shadow-sm border-foreground' : 'hover:border-foreground/40'}
        ${data.status === 'locked' ? 'opacity-60 bg-muted/30' : 'opacity-100'}
      `}>
        <CardHeader className="p-4 pb-2">
          <div className="flex justify-between items-start gap-3">
            <CardTitle className="text-sm font-bold leading-tight text-foreground">
              {data.label}
            </CardTitle>
            <div title={`Status: ${data.status}`}>
              {statusIcons[data.status]}
            </div>
          </div>
          <div className="flex gap-2 text-[11px] text-muted-foreground mt-1.5 items-center">
            <Clock className="w-3 h-3" />
            <span>{data.estimated_weeks}w</span>
            <span>•</span>
            <span className="capitalize">{data.difficulty}</span>
          </div>
        </CardHeader>
        
        <CardContent className="p-4 pt-1">
          <div className="flex flex-wrap gap-1 mt-1.5">
            {data.skills_acquired.slice(0, 3).map(skill => (
              <span key={skill} className="text-[10px] px-1.5 py-0.5 rounded-md bg-muted/80 text-foreground border border-border/60">
                {skill}
              </span>
            ))}
            {data.skills_acquired.length > 3 && (
              <span className="text-[10px] px-1.5 py-0.5 rounded-md bg-muted/50 text-muted-foreground">
                +{data.skills_acquired.length - 3}
              </span>
            )}
          </div>
        </CardContent>
      </Card>

      <Handle type="source" position={Position.Bottom} className="w-2.5 h-2.5 bg-foreground border border-card" />
    </div>
  );
}
