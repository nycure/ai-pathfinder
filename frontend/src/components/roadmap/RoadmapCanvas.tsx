"use client";

import React, { useCallback } from 'react';
import { 
  ReactFlow, 
  Controls, 
  Background, 
  useNodesState, 
  useEdgesState, 
  BackgroundVariant,
  Panel,
  MarkerType
} from '@xyflow/react';

import { useRoadmapStore } from '@/store/useRoadmapStore';
import { MilestoneNode } from './MilestoneNode';
import { PrerequisiteEdge } from './PrerequisiteEdge';

const nodeTypes: any = {
  customMilestoneNode: MilestoneNode,
};

const edgeTypes: any = {
  prerequisiteEdge: PrerequisiteEdge,
};

interface RoadmapCanvasProps {
  readOnlyRoadmap?: any;
  readOnly?: boolean;
}

export function RoadmapCanvas({ readOnlyRoadmap, readOnly = false }: RoadmapCanvasProps = {}) {
  const storeRoadmap = useRoadmapStore((state) => state.roadmap);
  const storeSetActiveNode = useRoadmapStore((state) => state.setActiveNode);
  
  const roadmap = readOnly ? readOnlyRoadmap : storeRoadmap;
  const setActiveNode = readOnly ? () => {} : storeSetActiveNode;

  // XYFlow expects nodes and edges state
  // We sync our zustand store into local state for reactflow rendering
  const [nodes, setNodes, onNodesChange] = useNodesState(roadmap?.nodes || []);
  const [edges, setEdges, onEdgesChange] = useEdgesState(roadmap?.edges || []);

  // Update flow state when global roadmap changes
  React.useEffect(() => {
    if (roadmap && roadmap.nodes) {
      // 1. Layout Normalizer: Expand older 300px/150px coordinates to 420px/180px
      const xPositions = Array.from(new Set(roadmap.nodes.map((n: any) => n.position?.x ?? 0))).sort((a: any, b: any) => a - b) as number[];
      let minPositiveDeltaX = Infinity;
      for (let i = 1; i < xPositions.length; i++) {
        const delta = xPositions[i] - xPositions[i - 1];
        if (delta > 20 && delta < minPositiveDeltaX) {
          minPositiveDeltaX = delta;
        }
      }

      const shouldScale = minPositiveDeltaX > 20 && minPositiveDeltaX < 380;
      const scaleX = shouldScale ? 420 / minPositiveDeltaX : 1.0;
      const scaleY = shouldScale ? 1.2 : 1.0;

      const normalizedNodes = roadmap.nodes.map((n: any) => ({
        ...n,
        position: {
          x: Math.round((n.position?.x ?? 0) * scaleX),
          y: Math.round((n.position?.y ?? 0) * scaleY),
        },
      }));
      setNodes(normalizedNodes);

      // 2. Intelligent, State-Aware Edge Mapping
      const nodeMap = new Map(roadmap.nodes.map((n: any) => [n.id, n]));

      setEdges(
        (roadmap.edges || []).map((e: any) => {
          const sourceNode: any = nodeMap.get(e.source);
          const targetNode: any = nodeMap.get(e.target);

          const sourceStatus = sourceNode?.data?.status;
          const targetStatus = targetNode?.data?.status;

          // Prerequisite statuses
          const isMastered = sourceStatus === 'completed' && targetStatus === 'completed';
          // Active flow: points to the currently active/available milestone
          const isActiveFlow = targetStatus === 'available';

          let strokeColor = '#C8C0B5'; // Inactive/Locked warm gray
          if (isActiveFlow) {
            strokeColor = '#121212';   // Active high-contrast dark
          } else if (isMastered) {
            strokeColor = '#059669';   // Mastered emerald
          }

          return {
            ...e,
            type: 'prerequisiteEdge',
            animated: isActiveFlow,
            data: {
              strokeColor,
              isActiveFlow,
              isMastered,
              targetStatus: targetStatus || 'locked',
              sourceStatus: sourceStatus || 'locked',
            },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              width: 14,
              height: 14,
              color: strokeColor,
            },
          };
        })
      );
    }
  }, [roadmap, setNodes, setEdges]);

  const onNodeClick = useCallback((event: any, node: any) => {
    setActiveNode(node.id);
  }, [setActiveNode]);

  const onPaneClick = useCallback(() => {
    setActiveNode(null); // Deselect when clicking canvas background
  }, [setActiveNode]);

  if (!roadmap) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-background text-muted-foreground border border-border rounded-lg">
        Generate a learning path to see the roadmap here.
      </div>
    );
  }

  return (
    <div className="w-full h-[80vh] border border-border rounded-lg overflow-hidden bg-background relative">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={readOnly ? undefined : onNodesChange}
        onEdgesChange={readOnly ? undefined : onEdgesChange}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        nodesDraggable={!readOnly}
        nodesConnectable={false}
        elementsSelectable={!readOnly}
        minZoom={0.15}
        maxZoom={1.5}
        className="bg-background"
      >
        <Background 
          variant={BackgroundVariant.Dots} 
          gap={24} 
          size={1.5} 
          color="#DFD7CE" 
        />
        <Controls className="bg-card border-border fill-foreground rounded-lg shadow-xs" />
        {readOnly && (
          <Panel position="top-left" className="bg-card px-3.5 py-2 rounded-xl border border-border shadow-xs">
            <h2 className="text-xs font-bold text-foreground">{roadmap.title}</h2>
            <p className="text-[10px] text-muted-foreground">{roadmap.total_estimated_weeks}w • {roadmap.total_hours}h</p>
          </Panel>
        )}
      </ReactFlow>
    </div>
  );
}
