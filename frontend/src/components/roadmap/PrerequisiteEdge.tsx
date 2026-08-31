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
    <>
      {/* Background shadow path for glow effect if animated */}
      {animated && (
        <BaseEdge 
          path={edgePath} 
          style={{ 
            ...style, 
            strokeWidth: 6, 
            stroke: 'oklch(0.65 0.25 250 / 30%)', // matches our primary neon blue
            filter: 'blur(4px)' 
          }} 
        />
      )}
      {/* Main path */}
      <BaseEdge 
        path={edgePath} 
        markerEnd={markerEnd} 
        style={{ 
          ...style, 
          strokeWidth: 2, 
          stroke: animated ? 'oklch(0.65 0.25 250)' : 'oklch(1 0 0 / 20%)',
          animation: animated ? 'dash 1.5s linear infinite' : 'none',
          strokeDasharray: animated ? '5,5' : 'none'
        }} 
      />
    </>
  );
}
