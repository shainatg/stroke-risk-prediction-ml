import React, { useState } from 'react';
import { 
  Sparkles, 
  Copy, 
  Check, 
  Download, 
  Layers, 
  FileText, 
  HelpCircle, 
  ChevronDown, 
  ChevronUp, 
  ArrowRight,
  ShieldAlert,
  Hash,
  ExternalLink
} from 'lucide-react';
import { AnalysisResult, Chunk } from '../types';

interface ResultsPanelProps {
  analysis: AnalysisResult | null;
  onOpenSimilarityLab: () => void;
  onOpenDocumentViewer: () => void;
  onSelectPassageForViewer: (chunk: Chunk) => void;
  onDownloadPdf: (analysisId: string) => void;
}

export const ResultsPanel: React.FC<ResultsPanelProps> = ({
  analysis,
  onOpenSimilarityLab,
  onOpenDocumentViewer,
  onSelectPassageForViewer,
  onDownloadPdf
}) => {
  const [copied, setCopied] = useState(false);
  const [mode, setMode] = useState<'grounded' | 'llm_comparison'>('grounded');
  const [showExplanation, setShowExplanation] = useState(true);
  const [selectedPassageIndex, setSelectedPassageIndex] = useState<number>(0);

  if (!analysis) {
    return (
      <div className="flex flex-col h-full bg-background-secondary border-l border-surface-border p-6 items-center justify-center text-center">
        <div className="p-4 rounded-2xl bg-surface-100 border border-surface-border mb-3 shadow-subtle">
          <Sparkles className="w-8 h-8 text-slate-500 animate-pulse" />
        </div>
        <h3 className="text-sm font-semibold text-slate-200">
          Awaiting Semantic Analysis
        </h3>
        <p className="text-xs text-slate-400 max-w-xs mt-1.5 leading-relaxed">
          Select a document, formulate a query in the studio, and click Analyze to view verified citations, similarity scores, and grounded answers.
        </p>
      </div>
    );
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(analysis.grounded_answer);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const activeChunk = analysis.ranked_chunks[selectedPassageIndex] || analysis.ranked_chunks[0];

  return (
    <div className="flex flex-col h-full bg-background-secondary border-l border-surface-border overflow-y-auto">
      
      {/* Results Header */}
      <div className="p-4 sm:p-5 border-b border-surface-border flex items-center justify-between sticky top-0 bg-background-secondary/95 backdrop-blur z-10">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400">
              Intelligence Findings
            </span>
            <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-[10px] font-mono text-emerald-400 font-semibold">
              Peak: {analysis.top_score_percentage}
            </span>
          </div>
          <h2 className="text-sm font-bold text-slate-100 truncate max-w-xs">
            {analysis.document_name}
          </h2>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={handleCopy}
            className="p-1.5 rounded-md bg-surface-50 hover:bg-surface-100 border border-surface-border text-slate-300 hover:text-slate-100 transition-colors"
            title="Copy Grounded Answer"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
          </button>
          
          {analysis.analysis_id && (
            <button
              onClick={() => onDownloadPdf(analysis.analysis_id!)}
              className="p-1.5 rounded-md bg-surface-50 hover:bg-surface-100 border border-surface-border text-slate-300 hover:text-cyan transition-colors"
              title="Download PDF Analysis Report"
            >
              <Download className="w-4 h-4" />
            </button>
          )}

          <button
            onClick={onOpenSimilarityLab}
            className="p-1.5 rounded-md bg-surface-50 hover:bg-surface-100 border border-surface-border text-slate-300 hover:text-cyan transition-colors"
            title="Open in Similarity Lab"
          >
            <Layers className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="p-4 sm:p-5 space-y-4 flex-1">

        {/* Grounded vs LLM Simulator Toggle */}
        <div className="flex p-1 rounded-lg bg-surface-50 border border-surface-border">
          <button
            onClick={() => setMode('grounded')}
            className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-all ${
              mode === 'grounded'
                ? 'bg-surface-200 text-cyan shadow-subtle border border-surface-border'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Grounded Finding
          </button>
          <button
            onClick={() => setMode('llm_comparison')}
            className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-all flex items-center justify-center gap-1.5 ${
              mode === 'llm_comparison'
                ? 'bg-surface-200 text-amber-300 shadow-subtle border border-surface-border'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Pure LLM Contrast</span>
          </button>
        </div>

        {/* Content Box */}
        {mode === 'grounded' ? (
          <div className="space-y-4">
            
            {/* Primary Grounded Answer Card */}
            <div className="p-4 rounded-xl bg-surface-50 border border-surface-border space-y-3 shadow-subtle">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-mono text-cyan flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-cyan" />
                  Verified Document Synthesis
                </span>
                <span className="text-[11px] font-mono text-slate-400">
                  {analysis.duration_ms.toFixed(1)} ms
                </span>
              </div>

              {/* Key Insight */}
              <div className="text-sm font-medium text-slate-100 leading-relaxed bg-surface-100/70 p-3 rounded-lg border border-surface-border/70">
                {analysis.key_insight}
              </div>

              {/* Primary Passage Citation */}
              <div className="pt-2 border-t border-surface-border space-y-1.5">
                <div className="flex items-center justify-between text-[11px] font-mono">
                  <span className="text-slate-400">Primary Citation</span>
                  <span className="text-emerald-400 font-semibold">
                    Page {analysis.top_page} • {analysis.top_score_percentage}
                  </span>
                </div>
                <blockquote className="p-2.5 rounded bg-surface-100/40 border-l-2 border-cyan text-xs text-slate-300 italic leading-relaxed">
                  "{analysis.top_passage_text}"
                </blockquote>
              </div>
            </div>

            {/* Explainable Match Drivers */}
            <div className="rounded-xl bg-surface-50 border border-surface-border overflow-hidden">
              <button
                onClick={() => setShowExplanation(!showExplanation)}
                className="w-full p-3 flex items-center justify-between text-xs font-mono text-slate-300 hover:bg-surface-100 transition-colors"
              >
                <span className="flex items-center gap-2">
                  <HelpCircle className="w-4 h-4 text-cyan" />
                  Why Did This Passage Match?
                </span>
                {showExplanation ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>

              {showExplanation && (
                <div className="p-3.5 pt-0 space-y-2.5 text-xs border-t border-surface-border/50">
                  <p className="text-slate-300 leading-relaxed text-[11px]">
                    {analysis.match_explanation.explanation}
                  </p>

                  {analysis.match_explanation.exact_term_matches.length > 0 && (
                    <div>
                      <span className="text-[10px] font-mono uppercase text-slate-500 block mb-1">
                        Exact Co-occurring Terms:
                      </span>
                      <div className="flex flex-wrap gap-1">
                        {analysis.match_explanation.exact_term_matches.map((term, i) => (
                          <span key={i} className="px-2 py-0.5 rounded bg-cyan/10 border border-cyan/20 text-cyan text-[10px] font-mono font-medium">
                            {term}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex items-center justify-between pt-1 text-[10px] font-mono text-slate-400 border-t border-surface-border/50">
                    <span>Dot Product: {analysis.match_explanation.dot_product.toFixed(4)}</span>
                    <span>128D Cosine Angle</span>
                  </div>
                </div>
              )}
            </div>

            {/* Top Matching Passages List */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-[11px] font-mono uppercase tracking-wider text-slate-400 px-1">
                <span>Ranked Matching Passages</span>
                <span>Top {analysis.ranked_chunks.length}</span>
              </div>

              <div className="space-y-2">
                {analysis.ranked_chunks.map((chunk, idx) => {
                  const isSelected = idx === selectedPassageIndex;
                  return (
                    <div
                      key={chunk.index}
                      onClick={() => setSelectedPassageIndex(idx)}
                      className={`p-3 rounded-lg border text-left cursor-pointer transition-all ${
                        isSelected
                          ? 'bg-surface-100 border-cyan/40 shadow-subtle'
                          : 'bg-surface-50/60 hover:bg-surface-100 border-surface-border'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1.5 text-[11px] font-mono">
                        <span className="text-slate-400 flex items-center gap-1.5">
                          <Hash className="w-3 h-3 text-cyan" />
                          Passage #{chunk.index + 1}
                        </span>
                        <div className="flex items-center gap-2">
                          <span className="text-slate-400">Page {chunk.page}</span>
                          <span className="text-emerald-400 font-semibold">
                            {(chunk.score! * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>

                      <p className="text-xs text-slate-300 line-clamp-3 leading-relaxed">
                        {chunk.text}
                      </p>

                      <div className="mt-2 pt-1.5 border-t border-surface-border/40 flex items-center justify-between">
                        <span className="text-[10px] font-mono text-slate-500">
                          {chunk.wordCount} words
                        </span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectPassageForViewer(chunk);
                            onOpenDocumentViewer();
                          }}
                          className="text-[11px] font-mono text-cyan hover:underline flex items-center gap-1"
                        >
                          <span>Locate in Viewer</span>
                          <ExternalLink className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

          </div>
        ) : (
          /* Pure LLM Simulator Comparison */
          <div className="p-4 rounded-xl bg-surface-50 border border-amber-500/20 space-y-3">
            <div className="flex items-center gap-2 text-xs font-mono text-amber-300">
              <ShieldAlert className="w-4 h-4 text-amber-400" />
              <span>Ungrounded Parametric Model Simulator</span>
            </div>
            
            <p className="text-xs text-slate-400 leading-relaxed">
              Demonstrates how a standard LLM answers purely from pre-trained memory without document grounding:
            </p>

            <div className="p-3.5 rounded-lg bg-surface-100 text-xs text-slate-200 leading-relaxed font-mono whitespace-pre-wrap border border-surface-border">
              {analysis.normal_llm_answer}
            </div>

            <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-[11px] text-amber-200 leading-relaxed">
              <strong>Key Architectural Insight:</strong> Pure LLM generation suffers from hallucinations and cannot cite private document pages. Synapse's 128D semantic vector similarity architecture guarantees that answers are grounded in verifiable passages with exact page references.
            </div>
          </div>
        )}

      </div>

    </div>
  );
};
