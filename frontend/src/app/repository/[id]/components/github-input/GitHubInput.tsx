"use client";

import { useState, useCallback } from "react";
import { useAnalyzeRepo } from "@/services/api";
import { useAnalysisStore } from "@/store/useAnalysisStore";
import { cn } from "@/lib/utils";
import { Search, Loader2, X } from "lucide-react";

export function GitHubInput() {
  const [input, setInput] = useState("");
  const [error, setError] = useState("");
  const mutate = useAnalyzeRepo();
  const setRepoUrl = useAnalysisStore((s) => s.setRepoUrl);
  const repoUrl = useAnalysisStore((s) => s.repoUrl);
  const isAnalyzing = useAnalysisStore((s) => s.status === "analyzing");

  const isValidGitHubUrl = useCallback((url: string) => {
    const pattern = /^https?:\/\/(www\.)?github\.com\/[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+\/?$/;
    return pattern.test(url.trim());
  }, []);

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      const trimmed = input.trim();
      if (!trimmed) {
        setError("Please enter a repository URL");
        return;
      }
      if (!isValidGitHubUrl(trimmed)) {
        setError("Please enter a valid GitHub repository URL");
        return;
      }
      setError("");
      setRepoUrl(trimmed);
      mutate.mutate(trimmed);
    },
    [input, isValidGitHubUrl, setRepoUrl, mutate]
  );

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-3xl mx-auto">
      <div
        className={cn(
          "flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900/80 backdrop-blur-sm p-2 transition-all",
          isAnalyzing && "border-atlas-500 shadow-lg shadow-atlas-500/20"
        )}
      >
        <div className="flex items-center gap-2 pl-3 text-slate-400">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
          </svg>
        </div>

        <input
          type="text"
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            if (error) setError("");
          }}
          placeholder="https://github.com/owner/repository"
          className={cn(
            "flex-1 bg-transparent text-slate-100 placeholder-slate-500 outline-none",
            "text-base min-w-0"
          )}
          disabled={isAnalyzing}
        />

        {input && !isAnalyzing && (
          <button
            type="button"
            onClick={() => { setInput(""); setError(""); }}
            className="p-2 text-slate-400 hover:text-slate-200 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}

        <button
          type="submit"
          disabled={isAnalyzing || !input.trim()}
          className={cn(
            "flex items-center gap-2 px-6 py-2.5 rounded-lg font-medium transition-all",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            isAnalyzing
              ? "bg-atlas-600/50 text-atlas-200"
              : "bg-atlas-500 hover:bg-atlas-400 text-white shadow-lg shadow-atlas-500/30"
          )}
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Search className="w-4 h-4" />
              Analyze
            </>
          )}
        </button>
      </div>

      {error && <p className="mt-2 text-sm text-red-400 px-2">{error}</p>}
    </form>
  );
}
