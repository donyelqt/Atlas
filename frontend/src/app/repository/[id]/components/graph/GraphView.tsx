"use client";

import { useCallback, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  type NodeTypes,
  type Edge,
  type Node,
  BackgroundVariant,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useGraph } from "@/services/api";
import { cn } from "@/lib/utils";
import { FileCode2, FolderOpen, GitBranch } from "lucide-react";

const NODE_COLORS: Record<string, string> = {
  file: "#0ea5e9",
  module: "#6366f1",
  root: "#f59e0b",
  unknown: "#94a3b8",
};

const nodeTypes: NodeTypes = {
  custom: ({ data }: { data: Record<string, unknown> }) => {
    const color = NODE_COLORS[String(data.type)] || "#94a3b8";
    const isModule = String(data.type) === "module";
    const Icon = isModule ? FolderOpen : FileCode2;
    return (
      <div
        className={cn(
          "px-4 py-2.5 rounded-xl border-2 shadow-xl min-w-[140px] max-w-[220px]",
          "backdrop-blur-sm transition-all hover:shadow-2xl"
        )}
        style={{
          borderColor: color,
          background: `linear-gradient(135deg, ${color}22, ${color}11)`,
        }}
      >
        <div className="flex items-center gap-2">
          <Icon className="w-4 h-4 shrink-0" style={{ color }} />
          <span className="text-xs font-semibold text-slate-100 truncate" title={String(data.label)}>
            {String(data.label)}
          </span>
        </div>
        <div className="text-[10px] text-slate-400 mt-1 truncate font-mono">
          {String(data.path || "").replace(/^.*\//, "")}
        </div>
      </div>
    );
  },
};

export function GraphView({ analysisId }: { analysisId: string }) {
  const { data, isLoading, error } = useGraph(analysisId);

  const { nodes, edges } = useMemo(() => {
    if (!data) return { nodes: [], edges: [] };

    const nodeMap = new Map(data.nodes.map((n) => [n.id, n]));

    const rfNodes: Node[] = data.nodes.map((n) => ({
      id: n.id,
      type: n.type === "module" || n.type === "file" ? "custom" : "custom",
      position: { x: (Math.sin(n.id.length) % 1) * 600 + 100, y: (Math.cos(n.id.length) % 1) * 400 + 100 },
      data: n,
    }));

    const rfEdges: Edge[] = data.edges.map((e, i) => ({
      id: `${e.source}-${e.target}-${i}`,
      source: e.source,
      target: e.target,
      type: "smoothstep",
      animated: Math.random() > 0.5,
      style: { stroke: "#475569", strokeWidth: 1.5 },
      label: e.type === "imports" || e.type === "depends_on" ? n.label : undefined,
    }));

    return { nodes: rfNodes, edges: rfEdges };
  }, [data]);

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState message={error.message} />;
  if (!data || nodes.length === 0) return <EmptyState />;

  return (
    <div className="h-full w-full rounded-2xl overflow-hidden border border-slate-800">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.1}
        maxZoom={2}
        defaultEdgeOptions={{ type: "smoothstep" }}
      >
        <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#1e293b" />
        <Controls className="bg-slate-900 border border-slate-700 rounded-lg" />
        <MiniMap
          nodeColor={(n) => NODE_COLORS[n.data?.type] || "#475569"}
          className="!bg-slate-950 !rounded-lg border border-slate-700"
          maskColor="rgba(15, 23, 42, 0.7)"
        />
      </ReactFlow>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="flex flex-col items-center justify-center h-[500px] gap-4">
      <div className="relative">
        <GitBranch className="w-12 h-12 text-atlas-400 animate-pulse" />
        <div className="absolute inset-0 w-12 h-12 border-2 border-atlas-500 rounded-full animate-ping" />
      </div>
      <p className="text-slate-400 text-sm">Building architecture graph...</p>
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex items-center justify-center h-[500px]">
      <div className="text-center">
        <p className="text-red-400 text-sm">Failed to load graph</p>
        <p className="text-slate-500 text-xs mt-1">{message}</p>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex items-center justify-center h-[500px]">
      <div className="text-center">
        <FolderOpen className="w-12 h-12 text-slate-700 mx-auto mb-3" />
        <p className="text-slate-500 text-sm">No graph data available</p>
      </div>
    </div>
  );
}
