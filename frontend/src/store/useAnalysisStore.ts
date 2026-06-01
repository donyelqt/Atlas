import { create } from "zustand";
import type { AnalysisSummary, GraphNode, GraphEdge, ChatMessage, ArchitectureSummary, OnboardingPlan } from "@/types";

interface AnalysisState {
  analysisId: string | null;
  repoUrl: string;
  status: "idle" | "analyzing" | "completed" | "failed";
  summary: AnalysisSummary | null;
  error: string | null;
  graphData: { nodes: GraphNode[]; edges: GraphEdge[] } | null;
  architecture: ArchitectureSummary | null;
  onboarding: OnboardingPlan | null;
  chatHistory: ChatMessage[];
  setRepoUrl: (url: string) => void;
  setAnalyzing: (status: "idle" | "analyzing" | "completed" | "failed") => void;
  setSummary: (summary: AnalysisSummary | null) => void;
  setError: (error: string | null) => void;
  setGraphData: (data: { nodes: GraphNode[]; edges: GraphEdge[] } | null) => void;
  setArchitecture: (data: ArchitectureSummary | null) => void;
  setOnboarding: (data: OnboardingPlan | null) => void;
  addChatMessage: (message: ChatMessage) => void;
  reset: () => void;
}

const initialState = {
  analysisId: null,
  repoUrl: "",
  status: "idle" as const,
  summary: null,
  error: null,
  graphData: null,
  architecture: null,
  onboarding: null,
  chatHistory: [],
};

export const useAnalysisStore = create<AnalysisState>((set) => ({
  ...initialState,
  setRepoUrl: (url) => set({ repoUrl: url }),
  setAnalyzing: (status) => set({ status, error: status === "completed" || status === "failed" ? null : null }),
  setSummary: (summary) => set({ summary, analysisId: summary?.id ?? null }),
  setError: (error) => set({ error }),
  setGraphData: (graphData) => set({ graphData }),
  setArchitecture: (architecture) => set({ architecture }),
  setOnboarding: (onboarding) => set({ onboarding }),
  addChatMessage: (message) => set((state) => ({ chatHistory: [...state.chatHistory, message] })),
  reset: () => set(initialState),
}));
