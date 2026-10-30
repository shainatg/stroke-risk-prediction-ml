import React from 'react';
import { CheckCircle2, Clock, Loader2 } from 'lucide-react';
import { TimelineStep } from '../types';

interface LiveTimelineProps {
  timeline: TimelineStep[];
  isAnalyzing: boolean;
  totalDurationMs?: number;
}

const DEFAULT_STAGES = [
  "Document received",
  "Text extracted",
  "Text normalized",
  "Similarity processing",
  "Relevant content identified",
  "Answer prepared"
];

export const LiveTimeline: React.FC<LiveTimelineProps> = ({
  timeline,
  isAnalyzing,
  totalDurationMs
}) => {
  if (!isAnalyzing && timeline.length === 0) {
    return null;
  }

  return (
    <div className="rounded-lg bg-surface-50 border border-surface-border p-3.5 space-y-2.5">
      <div className="flex items-center justify-between">
        <span className="text-xs font-mono font-medium uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5 text-cyan" />
          Execution Timeline
        </span>
        {totalDurationMs !== undefined && !isAnalyzing && (
          <span className="text-xs font-mono text-cyan bg-cyan/10 border border-cyan/20 px-2 py-0.5 rounded">
            Total: {totalDurationMs.toFixed(1)} ms
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
        {DEFAULT_STAGES.map((stageName, idx) => {
          const stepNum = idx + 1;
          const completedStep = timeline.find(t => t.step === stepNum || t.name.toLowerCase() === stageName.toLowerCase());
          const isDone = !!completedStep;
          const isCurrent = isAnalyzing && !isDone && (idx === 0 || timeline.some(t => t.step === idx));

          return (
            <div 
              key={stageName}
              className={`p-2 rounded border text-left transition-all duration-200 ${
                isDone 
                  ? 'bg-surface-100 border-emerald-500/30 text-slate-200'
                  : isCurrent 
                  ? 'bg-surface-100/90 border-cyan/40 text-cyan animate-pulse'
                  : 'bg-surface-50/50 border-surface-border/50 text-slate-500'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] font-mono text-slate-400">0{stepNum}</span>
                {isDone ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                ) : isCurrent ? (
                  <Loader2 className="w-3.5 h-3.5 text-cyan animate-spin" />
                ) : (
                  <div className="w-2 h-2 rounded-full bg-surface-border" />
                )}
              </div>
              <div className="text-[11px] font-medium truncate">{stageName}</div>
              {completedStep && (
                <div className="text-[10px] font-mono text-slate-400 mt-0.5">
                  {completedStep.duration_ms.toFixed(1)} ms
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
