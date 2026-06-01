import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAnalysisStore } from "@/store/useAnalysisStore";
import type { AnalysisSummary, GraphResponse, ChatResponse } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function analyzeRepo(repoUrl: string): Promise<AnalysisSummary> {
  const res = await fetch(`${API_URL}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_url: repoUrl }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Analysis failed");
  }
  return res.json();
}

async function pollSummary(id: string): Promise<AnalysisSummary | null> {
  const res = await fetch(`${API_URL}/api/summary/${id}`);
  if (!res.ok) return null;
  const data = await res.json();
  return data;
}

async function fetchGraph(id: string): Promise<GraphResponse> {
  const res = await fetch(`${API_URL}/api/graph/${id}`);
  if (!res.ok) throw new Error("Failed to fetch graph");
  return res.json();
}

async function sendChat(analysisId: string, question: string): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ analysis_id: analysisId, question }),
  });
  if (!res.ok) throw new Error("Failed to send message");
  return res.json();
}

export function useAnalyzeRepo() {
  const setSummary = useAnalysisStore((s) => s.setSummary);
  const setGraphData = useAnalysisStore((s) => s.setGraphData);
  const setArchitecture = useAnalysisStore((s) => s.setArchitecture);
  const setOnboarding = useAnalysisStore((s) => s.setOnboarding);
  const setError = useAnalysisStore((s) => s.setError);
  const setAnalyzing = useAnalysisStore((s) => s.setAnalyzing);

  return useMutation({
    mutationFn: analyzeRepo,
    onMutate: () => setAnalyzing("analyzing"),
    onSuccess: (data) => {
      setSummary(data);
      localStorage.setItem("lastAnalysisId", data.id);
    },
    onError: (error: Error) => {
      setError(error.message);
      setAnalyzing("failed");
    },
  });
}

export function usePollAnalysis(analysisId: string) {
  const setSummary = useAnalysisStore((s) => s.setSummary);
  const setGraphData = useAnalysisStore((s) => s.setGraphData);
  const setArchitecture = useAnalysisStore((s) => s.setArchitecture);
  const setOnboarding = useAnalysisStore((s) => s.setOnboarding);
  const setAnalyzing = useAnalysisStore((s) => s.setAnalyzing);
  const setError = useAnalysisStore((s) => s.setError);

  return useQuery({
    queryKey: ["analysis", analysisId],
    queryFn: () => pollSummary(analysisId),
    enabled: !!analysisId,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data?.status === "completed" || data?.status === "failed") return false;
      return 2000;
    },
    onSuccess: (data) => {
      if (!data) return;
      setSummary(data as AnalysisSummary);
      if (data.status === "completed") {
        setAnalyzing("completed");
        fetchGraph(analysisId).then(setGraphData);
      }
      if (data.status === "failed") {
        setAnalyzing("failed");
        setError(data.error ?? "Unknown");
      }
    },
  });
}

export function useGraph(analysisId: string) {
  return useQuery({
    queryKey: ["graph", analysisId],
    queryFn: () => fetchGraph(analysisId),
    enabled: !!analysisId,
  });
}

export function useChat() {
  const addChatMessage = useAnalysisStore((s) => s.addChatMessage);
  return useMutation({
    mutationFn: ({ analysisId, question }: { analysisId: string; question: string }) =>
      sendChat(analysisId, question),
    onSuccess: (data, variables) => {
      addChatMessage({ role: "user", content: variables.question, timestamp: new Date().toISOString() });
      addChatMessage({ role: "assistant", content: data.answer, timestamp: new Date().toISOString() });
    },
  });
}
