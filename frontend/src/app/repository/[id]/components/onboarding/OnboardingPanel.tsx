"use client";

import { useAnalysisStore } from "@/store/useAnalysisStore";
import { cn } from "@/lib/utils";
import { BookOpen, Clock, ArrowRight } from "lucide-react";

export function OnboardingPanel() {
  const onboarding = useAnalysisStore((s) => s.onboarding);
  const summary = useAnalysisStore((s) => s.summary);

  if (!onboarding || !summary) {
    return (
      <div className="flex items-center justify-center h-full text-slate-500 text-sm p-8 text-center">
        <div>
          <BookOpen className="w-8 h-8 mx-auto mb-2 text-slate-700" />
          <p>Onboarding plan will be generated after analysis.</p>
        </div>
      </div>
    );
  }

  const steps = onboarding.steps ?? [];
  const totalMinutes = onboarding.total_estimated_minutes ?? 0;

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3 rounded-xl border border-slate-800 bg-slate-900/60 p-4">
        <div className="w-10 h-10 rounded-full bg-atlas-500/10 flex items-center justify-center">
          <Clock className="w-5 h-5 text-atlas-400" />
        </div>
        <div>
          <p className="text-sm font-semibold text-slate-200">Estimated Learning Time</p>
          <p className="text-2xl font-bold text-atlas-400">{totalMinutes} min</p>
        </div>
      </div>

      {onboarding.prerequisites && onboarding.prerequisites.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Prerequisites</h4>
          <div className="flex flex-wrap gap-2">
            {onboarding.prerequisites.map((p: string, i: number) => (
              <span key={i} className="px-3 py-1 rounded-lg border border-slate-700 bg-slate-900 text-xs text-slate-300">
                {p}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="space-y-2">
        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Learning Path</h4>
        <div className="space-y-0">
          {steps.map((step: { title: string; description: string; files?: string[]; estimated_minutes?: number }, i: number) => (
            <div key={i} className="relative flex gap-4">
              {i < steps.length - 1 && (
                <div className="absolute left-[19px] top-10 bottom-[-8px] w-px bg-slate-700" />
              )}
              <div className="z-10 w-10 h-10 rounded-full bg-slate-800 border-2 border-atlas-500 flex items-center justify-center shrink-0">
                <span className="text-xs font-bold text-atlas-400">{i + 1}</span>
              </div>
              <div className="flex-1 pb-6">
                <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
                  <div className="flex items-start justify-between gap-2">
                    <h5 className="text-sm font-semibold text-slate-200">{step.title}</h5>
                    {step.estimated_minutes && (
                      <span className="text-[10px] font-medium text-slate-400 bg-slate-800 px-2 py-0.5 rounded-full whitespace-nowrap">
                        {step.estimated_minutes}m
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">{step.description}</p>
                  {step.files && step.files.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-1.5">
                      {step.files.map((f: string, j: number) => (
                        <code key={j} className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-atlas-300 border border-slate-700">
                          {f.replace(/^.*\//, "")}
                        </code>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
