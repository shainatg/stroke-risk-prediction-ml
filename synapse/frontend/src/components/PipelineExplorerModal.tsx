import React, { useState } from 'react';
import { 
  X, 
  Cpu, 
  ArrowRight, 
  CheckCircle2, 
  Code2, 
  BookOpen, 
  Layers, 
  Zap,
  Terminal
} from 'lucide-react';
import { PipelineStage } from '../types';

interface PipelineExplorerModalProps {
  isOpen: boolean;
  onClose: () => void;
  stages: PipelineStage[];
}

export const PipelineExplorerModal: React.FC<PipelineExplorerModalProps> = ({
  isOpen,
  onClose,
  stages
}) => {
  const [selectedStageIndex, setSelectedStageIndex] = useState<number>(3); // Default to 128D Embedding stage

  if (!isOpen) return null;

  const currentStage = stages[selectedStageIndex] || stages[0];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-5xl h-[88vh] rounded-2xl bg-background-card border border-surface-border shadow-premium flex flex-col overflow-hidden">
        
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-surface-border flex items-center justify-between bg-surface-50">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-lavender/10 border border-lavender/20">
              <Cpu className="w-5 h-5 text-lavender" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-slate-100">
                  Interactive Pipeline Explorer
                </h2>
                <span className="px-2 py-0.5 rounded bg-surface-200 text-lavender text-[10px] font-mono font-medium">
                  Architecture Blueprint
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">
                Click any stage to inspect the underlying mathematics, data structures, and algorithmic logic.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-surface-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">

          {/* Interactive Flow Diagram */}
          <div className="p-4 rounded-xl bg-surface-50 border border-surface-border overflow-x-auto">
            <div className="flex items-center justify-between min-w-[760px] gap-2">
              {stages.map((stage, idx) => {
                const isSelected = idx === selectedStageIndex;
                return (
                  <React.Fragment key={stage.id}>
                    <button
                      onClick={() => setSelectedStageIndex(idx)}
                      className={`flex-1 p-3 rounded-lg border text-left transition-all ${
                        isSelected
                          ? 'bg-surface-200 border-cyan text-cyan shadow-glow-cyan'
                          : 'bg-surface-100 hover:bg-surface-200/80 border-surface-border text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      <div className="text-[10px] font-mono uppercase tracking-wider text-slate-500 mb-1">
                        0{idx + 1} • {stage.phase}
                      </div>
                      <div className="text-xs font-semibold truncate text-slate-200">
                        {stage.name}
                      </div>
                    </button>

                    {idx < stages.length - 1 && (
                      <ArrowRight className="w-4 h-4 text-slate-600 shrink-0" />
                    )}
                  </React.Fragment>
                );
              })}
            </div>
          </div>

          {/* Selected Stage Deep Dive Card */}
          {currentStage && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              
              {/* Left Column: Conceptual Overview */}
              <div className="md:col-span-2 p-6 rounded-xl bg-surface-50 border border-surface-border space-y-4 text-left">
                <div className="flex items-center justify-between border-b border-surface-border pb-3">
                  <div>
                    <span className="text-[11px] font-mono text-cyan uppercase tracking-wider">
                      Stage Deep Dive // 0{selectedStageIndex + 1}
                    </span>
                    <h3 className="text-base font-bold text-slate-100">
                      {currentStage.name}
                    </h3>
                  </div>
                  <span className="px-2.5 py-1 rounded bg-surface-100 border border-surface-border text-xs font-mono text-slate-300">
                    {currentStage.phase}
                  </span>
                </div>

                <div className="space-y-3 text-xs text-slate-300 leading-relaxed">
                  <div>
                    <h4 className="text-[11px] font-mono uppercase text-slate-500 mb-1">
                      Functional Description
                    </h4>
                    <p className="text-slate-200 bg-surface-100/60 p-3 rounded-lg border border-surface-border/60">
                      {currentStage.description}
                    </p>
                  </div>

                  <div>
                    <h4 className="text-[11px] font-mono uppercase text-slate-500 mb-1">
                      Technical & Algorithmic Implementation
                    </h4>
                    <p className="text-slate-300 leading-relaxed">
                      {currentStage.technical_details}
                    </p>
                  </div>
                </div>

                {/* Mathematical Formula Box */}
                {currentStage.formula && (
                  <div className="pt-2">
                    <h4 className="text-[11px] font-mono uppercase text-slate-500 mb-1 flex items-center gap-1.5">
                      <Code2 className="w-3.5 h-3.5 text-cyan" />
                      Mathematical Notation
                    </h4>
                    <div className="p-3.5 rounded-lg bg-surface-100 font-mono text-xs text-cyan border border-surface-border/80 overflow-x-auto">
                      {currentStage.formula}
                    </div>
                  </div>
                )}
              </div>

              {/* Right Column: Architectural Principles */}
              <div className="p-5 rounded-xl bg-surface-50 border border-surface-border space-y-4 text-left">
                <h4 className="text-xs font-semibold text-slate-200 flex items-center gap-2 border-b border-surface-border pb-2">
                  <Zap className="w-4 h-4 text-amber-400" />
                  Key Guarantees
                </h4>

                <div className="space-y-3 text-xs">
                  <div className="p-2.5 rounded-lg bg-surface-100/50 border border-surface-border">
                    <div className="font-semibold text-slate-200 mb-0.5">Zero Fabricated Numbers</div>
                    <p className="text-[11px] text-slate-400">
                      Every cosine similarity score is calculated directly between the 128D query and passage vectors.
                    </p>
                  </div>

                  <div className="p-2.5 rounded-lg bg-surface-100/50 border border-surface-border">
                    <div className="font-semibold text-slate-200 mb-0.5">Zero External Dependencies</div>
                    <p className="text-[11px] text-slate-400">
                      The core similarity engine is written in pure Python using standard library math and hashing.
                    </p>
                  </div>

                  <div className="p-2.5 rounded-lg bg-surface-100/50 border border-surface-border">
                    <div className="font-semibold text-slate-200 mb-0.5">Strict Verifiable Citations</div>
                    <p className="text-[11px] text-slate-400">
                      All grounded findings provide passage numbers, page references, and similarity match percentages.
                    </p>
                  </div>
                </div>
              </div>

            </div>
          )}

        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3.5 border-t border-surface-border bg-surface-50 flex items-center justify-between text-xs font-mono text-slate-400">
          <span>Production Pipeline: Synapse Semantic Core v1.0.0</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-md bg-surface-100 hover:bg-surface-200 text-slate-200 border border-surface-border transition-colors"
          >
            Close Explorer
          </button>
        </div>

      </div>
    </div>
  );
};
