"use client";

import { useState } from "react";
import { useAnalysisStore } from "@/store/useAnalysisStore";
import { useAnalyzeRepo } from "@/services/api";
import { cn } from "@/lib/utils";
import { Search, Loader2, Zap, Github, ArrowRight, BarChart2, MessageSquare, BookOpen, Shield } from "lucide-react";
import Link from "next/link";

const FEATURES = [
  { icon: BarChart2, title: "Architecture Graph", desc: "Interactive visualization of modules, files, and dependencies" },
  { icon: MessageSquare, title: "Repository Chat", desc: "Ask questions about any part of the codebase" },
  { icon: BookOpen, title: "AI Onboarding", desc: "Personalized learning path for new developers" },
  { icon: Shield, title: "Security Audit", desc: "Identify vulnerabilities and code quality issues" },
];

export default function HomePage() {
  const [input, setInput] = useState("");
  const [error, setError] = useState("");
  const repoUrl = useAnalysisStore((s) => s.repoUrl);
  const setRepoUrl = useAnalysisStore((s) => s.setRepoUrl);
  const mutate = useAnalyzeRepo();

  const isValidGitHubUrl = (url: string) =>
    /^https?:\/\/(www\.)?github\.com\/[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+\/?$/.test(url.trim());

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed) { setError("Please enter a repository URL"); return; }
    if (!isValidGitHubUrl(trimmed)) { setError("Please enter a valid GitHub repository URL"); return; }
    setError("");
    setRepoUrl(trimmed);
    mutate.mutate(trimmed);
  };

  return (
    <main className="min-h-screen bg-slate-950 flex flex-col items-center justify-center relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-atlas-500/5 rounded-full blur-3xl" />
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-indigo-500/5 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 max-w-5xl w-full px-6">
        <header className="text-center mb-12 space-y-4">
          <Link href="/" className="inline-flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-atlas-500 flex items-center justify-center shadow-lg shadow-atlas-500/40">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white tracking-tight">Atlas</span>
          </Link>
          <h1 className="text-5xl md:text-6xl font-extrabold text-white tracking-tight leading-[1.1]">
            Understand any GitHub{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-atlas-400 to-indigo-400">
              repository
            </span>
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto leading-relaxed">
            AI-powered architecture analysis. Paste any public GitHub repository URL and instantly understand how the codebase works.
          </p>
        </header>

        <form onSubmit={handleSubmit} className="mb-16">
          <div className="max-w-3xl mx-auto">
            <div
              className={cn(
                "flex items-center gap-3 rounded-2xl border bg-slate-900/80 backdrop-blur-sm p-2 transition-all",
                mutate.isPending && "border-atlas-500 shadow-2xl shadow-atlas-500/20",
                "border-slate-700"
              )}
            >
              <div className="flex items-center gap-2 pl-3 text-slate-400">
                <Github className="w-5 h-5" />
              </div>
              <input
                type="text"
                value={input}
                onChange={(e) => { setInput(e.target.value); if (error) setError(""); }}
                placeholder="https://github.com/owner/repository"
                className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 outline-none text-base min-w-0"
                disabled={mutate.isPending}
              />
              <button
                type="submit"
                disabled={mutate.isPending || !input.trim()}
                className={cn(
                  "flex items-center gap-2 px-8 py-3 rounded-xl font-semibold transition-all",
                  "disabled:opacity-50 disabled:cursor-not-allowed",
                  mutate.isPending
                    ? "bg-atlas-600/50 text-atlas-200"
                    : "bg-atlas-500 hover:bg-atlas-400 text-white shadow-xl shadow-atlas-500/30"
                )}
              >
                {mutate.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Search className="w-4 h-4" />
                    Analyze Repository
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
            {error && <p className="mt-3 text-sm text-red-400 px-2 max-w-3xl mx-auto">{error}</p>}
          </div>
        </form>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          {FEATURES.map((feature) => (
            <div
              key={feature.title}
              className="group rounded-2xl border border-slate-800 bg-slate-900/60 p-5 hover:bg-slate-800/50 hover:border-slate-600 transition-all duration-300"
            >
              <div className="w-10 h-10 rounded-xl bg-atlas-500/10 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                <feature.icon className="w-5 h-5 text-atlas-400" />
              </div>
              <h3 className="text-sm font-semibold text-slate-200 mb-1">{feature.title}</h3>
              <p className="text-xs text-slate-500 leading-relaxed">{feature.desc}</p>
            </div>
          ))}
        </div>

        <footer className="mt-16 text-center text-xs text-slate-600">
          Built with Next.js, AI, and a lot of patience. Analysis time: ~60ms for small repos.
        </footer>
      </div>
    </main>
  );
}
