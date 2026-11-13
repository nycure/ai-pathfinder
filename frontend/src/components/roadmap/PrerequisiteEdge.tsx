import React from 'react';
import { BaseEdge, getBezierPath, type EdgeProps } from '@xyflow/react';

export function PrerequisiteEdge({
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  markerEnd,
  animated
}: EdgeProps) {
  const [edgePath] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  return (
    <BaseEdge 
      path={edgePath} 
      markerEnd={markerEnd} 
      style={{ 
        ...style, 
        strokeWidth: 1.5, 
        stroke: animated ? '#121212' : '#B8AEA2',
        strokeDasharray: animated ? '4,4' : 'none'
      }} 
    />
  );
}
