import React from 'react';
import { BaseEdge, getSmoothStepPath, type EdgeProps } from '@xyflow/react';

export function PrerequisiteEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  markerEnd,
  data
}: EdgeProps) {
  const [edgePath] = getSmoothStepPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
    borderRadius: 16,
    offset: 28,
  });

  const edgeData = (data as any) || {};
  const isActiveFlow = edgeData.isActiveFlow ?? false;
  const isMastered = edgeData.isMastered ?? false;

  // Selected state-aware stroke color
  const strokeColor = edgeData.strokeColor || (isActiveFlow ? '#121212' : isMastered ? '#059669' : '#C8C0B5');
  const strokeWidth = isActiveFlow ? 2 : 1.5;
  const strokeDasharray = isActiveFlow ? '5,5' : 'none';

  return (
    <BaseEdge 
      id={id}
      path={edgePath} 
      markerEnd={markerEnd} 
      style={{ 
        ...style, 
        strokeWidth, 
        stroke: strokeColor,
        strokeDasharray,
      }} 
    />
  );
}
