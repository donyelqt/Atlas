"use client";

import { useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { useAnalysisStore } from "@/store/useAnalysisStore";
import { usePollAnalysis } from "@/services/api";
import { GitHubInput } from "./components/github-input";
import { GraphView } from "./components/graph";
import { ChatInterface } from "./components/chat";
import { ArchitecturePanel } from "./components/architecture";
import { OnboardingPanel } from "./components/onboarding";
import { cn } from "@/lib/utils";
import { BarChart3, GitBranch, MessageSquare, BookOpen, ArrowLeft } from "lucide-react";
import Link from "next/link";

const TABS = [
  { id: "graph", label: "Architecture", icon: GitBranch },
  { id: "chat", label: "Chat", icon: MessageSquare },
  { id: "architecture", label: "Analysis", icon: BarChart3 },
  { id: "onboarding", label: "Onboarding", icon: BookOpen },
] as const;

type TabId = (typeof TABS)[number]["id"];

export default function RepositoryPage() {
  const searchParams = useSearchParams();
  const initialUrl = searchParams.get("url") ?? "";
  const repoUrl = useAnalysisStore((s) => s.repoUrl);
  const analysisId = useAnalysisStore((s) => s.analysisId);
  const status = useAnalysisStore((s) => s.status);
  const setRepoUrl = useAnalysisStore((s) => s.setRepoUrl);

  useEffect(() => {
    if (initialUrl && !repoUrl) setRepoUrl(initialUrl);
  }, [initialUrl, repoUrl, setRepoUrl]);

  usePollAnalysis(analysisId);

  const activeTab = status === "idle" || status === "analyzing" ? "graph" : "graph";

  return (
    <main className="h-screen flex flex-col bg-slate-950 overflow-hidden">
      <header className="shrink-0 border-b border-slate-800 bg-slate-950/80 backdrop-blur-sm z-10">
        <div className="max-w-screen-2xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <Link
              href="/"
              className="flex items-center gap-2 text-slate-400 hover:text-slate-200 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span className="text-sm">Back to Atlas</span>
            </Link>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-atlas-500 animate-pulse" />
              <span className="text-xs text-slate-400">Atlas AI</span>
            </div>
          </div>
          <GitHubInput />
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex flex-col min-w-0">
          {status === "completed" && (
            <div className="shrink-0 flex items-center gap-1 px-6 pt-4 overflow-x-auto">
              {TABS.map((tab) => (
                <button
                  key={tab.id}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 rounded-full text-xs font-medium transition-all",
                    activeTab === tab.id
                      ? "bg-atlas-500/20 text-atlas-300 border border-atlas-500/30"
                      : "text-slate-500 hover:text-slate-300 border border-transparent"
                  )}
                >
                  <tab.icon className="w-3.5 h-3.5" />
                  {tab.label}
                </button>
              ))}
            </div>
          )}

          <div className="flex-1 p-6 overflow-hidden min-w-0">
            {status === "analyzing" && (
              <div className="h-full flex items-center justify-center">
                <AnalyzingState />
              </div>
            )}
            {status === "completed" && (
              <div className="h-full flex flex-col overflow-hidden">
                <GraphView analysisId={analysisId!} />
              </div>
            )}
            {status === "idle" && !repoUrl && (
              <div className="h-full flex items-center justify-center">
                <EmptyRepoState />
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}

function AnalyzingState() {
  return (
    <div className="text-center space-y-4">
      <div className="relative w-16 h-16 mx-auto">
        <div className="absolute inset-0 border-4 border-atlas-500/30 rounded-full" />
        <div className="absolute inset-0 border-4 border-atlas-500 rounded-full border-t-transparent animate-spin" />
      </div>
      <div>
        <h3 className="text-sm font-semibold text-slate-200">Analyzing repository</h3>
        <p className="text-xs text-slate-500 mt-1">Building architecture graph and AI summary...</p>
      </div>
    </div>
  );
}

function EmptyRepoState() {
  return (
    <div className="text-center space-y-3">
      <div className="w-16 h-16 mx-auto rounded-full bg-slate-900 flex items-center justify-center">
        <BarChart3 className="w-8 h-8 text-slate-700" />
      </div>
      <h3 className="text-sm font-semibold text-slate-400">Enter a GitHub repository URL above</h3>
      <p className="text-xs text-slate-600 max-w-md mx-auto">
        Atlas will analyze the codebase, build an interactive architecture graph, generate an AI summary, and answer your questions.
      </p>
    </div>
  );
}
