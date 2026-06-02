"use client";

import { useState } from "react";
import { useGraphSearch, useSyncGraph, useEntryPoints } from "@/services/api";
import { useAnalysisStore } from "@/store/useAnalysisStore";
import { cn } from "@/lib/utils";
import { Search, RefreshCw, BookOpen, GitBranch, Loader2, X, ChevronRight } from "lucide-react";

export { SearchPanel };

function SearchPanel() {
  const [query, setQuery] = useState("");
  const [hops, setHops] = useState(2);
  const analysisId = useAnalysisStore((s) => s.analysisId);
  const syncMut = useSyncGraph();
  const { data: entryData, isLoading: entryLoading } = useEntryPoints(analysisId || "");

  const searchResult = useGraphSearch(analysisId || "", query, hops);
  const isSearching = searchResult.isFetching;
  const results = searchResult.data?.results ?? [];

  const handleSync = async () => {
    if (!analysisId) return;
    await syncMut.mutateAsync(analysisId);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <GitBranch className="w-4 h-4 text-atlas-400" />
            Graph Search (Neo4j)
          </h3>
          <button
            onClick={handleSync}
            disabled={!analysisId || syncMut.isPending}
            className={cn(
              "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors",
              "bg-slate-800 border border-slate-700 text-slate-300 hover:bg-slate-700",
              (!analysisId || syncMut.isPending) && "opacity-50 cursor-not-allowed"
            )}
          >
            <RefreshCw className={cn("w-3 h-3", syncMut.isPending && "animate-spin")} />
            Sync Graph
          </button>
        </div>
        <p className="text-[11px] text-slate-500 leading-relaxed">
          Search across the full codebase graph in Neo4j. Useful for large, undocumented repos. Uses
          APOC variable-length traversal.
        </p>
      </div>

      <div className="mt-4 space-y-2">
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search: auth, payment, user model…"
              className="w-full rounded-xl border border-slate-700 bg-slate-900/80 pl-9 pr-8 py-2 text-xs text-slate-100 placeholder-slate-500 outline-none focus:border-atlas-500"
            />
            {query && (
              <button
                onClick={() => setQuery("")}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-slate-200"
              >
                <X className="w-3 h-3" />
              </button>
            )}
          </div>
        </div>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-[11px] text-slate-400">
            <span>Hops</span>
            <select
              value={hops}
              onChange={(e) => setHops(Number(e.target.value))}
              className="rounded-lg border border-slate-700 bg-slate-900 px-2 py-1 text-xs text-slate-200 outline-none focus:border-atlas-500"
            >
              <option value={1}>1</option>
              <option value={2}>2</option>
              <option value={3}>3</option>
              <option value={4}>4</option>
            </select>
          </label>
          {searchResult.isFetching && (
            <span className="flex items-center gap-1.5 text-[11px] text-atlas-400">
              <Loader2 className="w-3 h-3 animate-spin" />
              Searching…
            </span>
          )}
        </div>
      </div>

      {query && !isSearching && searchResult.isFetched && (
        <div className="mt-4 space-y-2">
          <p className="text-[11px] text-slate-500">
            {results.length} result{results.length !== 1 ? "s" : ""} for "{query}"
          </p>
          <div className="space-y-2 max-h-[260px] overflow-y-auto pr-1">
            {results.map((path: any, i: number) => (
              <PathCard key={i} path={path} />
            ))}
            {results.length === 0 && (
              <p className="text-xs text-slate-600 py-4 text-center">No nodes matched. Try a broader term or fewer hops.</p>
            )}
          </div>
        </div>
      )}

      <div className="mt-auto pt-4 border-t border-slate-800 space-y-2">
        <p className="text-[11px] text-slate-500 font-medium uppercase tracking-wider">Entry Points</p>
        {entryLoading ? (
          <p className="text-xs text-slate-600 py-2">Loading entry points…</p>
        ) : (
          <div className="space-y-1.5 max-h-[160px] overflow-y-auto">
            {(entryData?.entry_points ?? []).slice(0, 8).map((ep: any) => (
              <div
                key={ep.id}
                className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg border border-slate-800 bg-slate-900/60 text-xs"
              >
                <BookOpen className="w-3 h-3 text-atlas-400 shrink-0" />
                <span className="truncate text-slate-300" title={ep.path}>{ep.label}</span>
              </div>
            ))}
            {(entryData?.entry_points ?? []).length === 0 && (
              <p className="text-[11px] text-slate-600 py-2">No entry points found. Sync the graph first.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function PathCard({ path }: { path: any }) {
  const nodes = path.node_path ?? path.nodes ?? [];
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-3">
      <div className="flex flex-wrap items-center gap-1.5">
        {nodes.map((n: any, i: number) => (
          <span key={i} className="flex items-center gap-1.5">
            <span
              className={cn(
                "px-2 py-0.5 rounded-md text-[10px] font-mono truncate max-w-[140px]",
                i === 0 ? "bg-atlas-500/15 text-atlas-300" : "bg-slate-800 text-slate-400"
              )}
              title={n.path ?? n.id}
            >
              {n.label ?? n.id}
            </span>
            {i < nodes.length - 1 && <ChevronRight className="w-3 h-3 text-slate-600" />}
          </span>
        ))}
      </div>
      <div className="mt-1.5 flex gap-1.5 flex-wrap">
        {(path.edge_types ?? []).map((et: string, i: number) => (
          <span key={i} className="text-[10px] text-slate-500 bg-slate-800/60 px-1.5 py-0.5 rounded">
            {et}
          </span>
        ))}
      </div>
    </div>
  );
}
