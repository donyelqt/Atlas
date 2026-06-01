"use client";

import { useAnalysisStore } from "@/store/useAnalysisStore";
import { cn } from "@/lib/utils";
import { Layers, Zap, FileCode2, Building2 } from "lucide-react";

const COMPLEXITY_COLORS: Record<string, string> = {
  Low: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
  Medium: "text-amber-400 bg-amber-500/10 border-amber-500/30",
  High: "text-red-400 bg-red-500/10 border-red-500/30",
};

export function ArchitecturePanel() {
  const summary = useAnalysisStore((s) => s.summary);
  const architecture = useAnalysisStore((s) => s.architecture);

  if (!summary || !architecture) {
    return (
      <div className="flex items-center justify-center h-full text-slate-500 text-sm p-8 text-center">
        Architecture analysis will appear here once analysis is complete.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3">
        <StatCard icon={<Layers className="w-4 h-4" />} label="Framework" value={summary.framework ?? "Unknown"} />
        <StatCard icon={<FileCode2 className="w-4 h-4" />} label="Language" value={summary.language ?? "Unknown"} />
        <StatCard icon={<Building2 className="w-4 h-4" />} label="Architecture" value={architecture.architecture_type ?? "Unknown"} />
        <StatCard
          icon={<Zap className="w-4 h-4" />}
          label="Complexity"
          value={architecture.complexity ?? "Unknown"}
          badge
        />
      </div>

      <div className="space-y-2">
        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Summary</h4>
        <p className="text-sm text-slate-300 leading-relaxed bg-slate-900/60 rounded-xl p-4 border border-slate-800">
          {architecture.summary || "No summary available"}
        </p>
      </div>

      {architecture.key_modules && architecture.key_modules.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Key Modules</h4>
          <div className="grid gap-2">
            {architecture.key_modules.slice(0, 12).map((mod: { name: string; description?: string }, i: number) => (
              <div key={i} className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-900/60 px-4 py-3">
                <span className="text-sm font-medium text-slate-200 truncate mr-2">{mod.name}</span>
                <span className="text-xs text-slate-500 truncate flex-1">{mod.description || "—"}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  badge,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  badge?: boolean;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 px-4 py-3">
      <div className="flex items-center gap-2 text-slate-400 mb-1">
        {icon}
        <span className="text-xs uppercase tracking-wider">{label}</span>
      </div>
      <p
        className={cn(
          "text-sm font-semibold truncate",
          badge && value && COMPLEXITY_COLORS[value] && "px-2 py-0.5 rounded-md inline-block",
          badge && value && COMPLEXITY_COLORS[value]
        )}
      >
        {value || "Unknown"}
      </p>
    </div>
  );
}
