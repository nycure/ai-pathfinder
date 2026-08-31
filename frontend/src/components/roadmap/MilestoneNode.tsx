import React from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Lock, CheckCircle2, PlayCircle, Clock } from 'lucide-react';
import { RoadmapNode } from '@/lib/types';

export function MilestoneNode({ data, selected }: NodeProps<RoadmapNode>) {
  const statusIcons = {
    locked: <Lock className="w-4 h-4 text-muted-foreground" />,
    available: <PlayCircle className="w-4 h-4 text-primary" />,
    in_progress: <PlayCircle className="w-4 h-4 text-accent" />,
    completed: <CheckCircle2 className="w-4 h-4 text-green-500" />
  };

  const statusColors = {
    locked: "bg-muted/50 border-muted text-muted-foreground",
    available: "bg-primary/20 border-primary text-primary-foreground",
    in_progress: "bg-accent/20 border-accent text-accent-foreground",
    completed: "bg-green-500/20 border-green-500 text-green-400"
  };

  return (
    <div className="relative group min-w-[280px]">
      <Handle type="target" position={Position.Top} className="w-3 h-3 bg-primary/50 border-background" />
      
      <Card className={`
        bg-card/50 backdrop-blur-md border-border transition-all duration-300
        ${selected ? 'ring-2 ring-primary shadow-[0_0_15px_rgba(var(--primary),0.5)]' : 'hover:border-primary/50'}
        ${data.status === 'locked' ? 'opacity-70' : 'opacity-100'}
      `}>
        <CardHeader className="p-4 pb-2">
          <div className="flex justify-between items-start gap-4">
            <CardTitle className="text-lg font-bold leading-tight">
              {data.label}
            </CardTitle>
            <div title={`Status: ${data.status}`}>
              {statusIcons[data.status]}
            </div>
          </div>
          <div className="flex gap-2 text-xs text-muted-foreground mt-1 items-center">
            <Clock className="w-3 h-3" />
            <span>{data.estimated_weeks} weeks</span>
            <span>•</span>
            <span className="capitalize">{data.difficulty}</span>
          </div>
        </CardHeader>
        
        <CardContent className="p-4 pt-2">
          <div className="flex flex-wrap gap-1 mt-2">
            {data.skills_acquired.map(skill => (
              <Badge key={skill} variant="secondary" className="text-[10px] px-1.5 py-0 h-4">
                {skill}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      <Handle type="source" position={Position.Bottom} className="w-3 h-3 bg-primary/50 border-background" />
    </div>
  );
}
