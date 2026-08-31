"use client";

import React, { useCallback } from 'react';
import { 
  ReactFlow, 
  Controls, 
  Background, 
  useNodesState, 
  useEdgesState, 
  BackgroundVariant,
  Panel
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

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
    if (roadmap) {
      setNodes(roadmap.nodes);
      // Ensure all edges map to our custom type and have animated properties if needed
      setEdges(roadmap.edges.map((e: any) => ({
        ...e,
        type: 'prerequisiteEdge',
        animated: true // simple default for now
      })));
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
        nodesDraggable={!readOnly}
        nodesConnectable={false}
        elementsSelectable={!readOnly}
        minZoom={0.2}
        maxZoom={1.5}
        className="dark"
      >
        <Background 
          variant={BackgroundVariant.Dots} 
          gap={24} 
          size={1.5} 
          color="oklch(1 0 0 / 15%)" 
        />
        <Controls className="bg-card border-border fill-foreground" />
        <Panel position="top-left" className="bg-card/80 backdrop-blur-md p-4 rounded-lg border border-border">
          <h2 className="text-xl font-bold text-primary">{roadmap.title}</h2>
          <p className="text-sm text-muted-foreground">{roadmap.total_estimated_weeks} weeks • {roadmap.total_hours} hours</p>
        </Panel>
      </ReactFlow>
    </div>
  );
}
