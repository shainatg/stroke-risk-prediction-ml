import React, { useState, useEffect } from 'react';
import { 
  Play, 
  RotateCcw, 
  Sliders, 
  CornerDownLeft, 
  Lightbulb, 
  History, 
  Search,
  Sparkles
} from 'lucide-react';
import { LiveTimeline } from './LiveTimeline';
import { TimelineStep, DocumentMeta } from '../types';

interface QueryStudioPanelProps {
  query: string;
  setQuery: (q: string) => void;
  onAnalyze: () => void;
  isAnalyzing: boolean;
  activeDoc: DocumentMeta | null;
  timeline: TimelineStep[];
  totalDurationMs?: number;
  recentQueries: string[];
  onSelectRecentQuery: (q: string) => void;
  chunkSize: number;
  setChunkSize: (s: number) => void;
  chunkOverlap: number;
  setChunkOverlap: (o: number) => void;
  topK: number;
  setTopK: (k: number) => void;
}

export const QueryStudioPanel: React.FC<QueryStudioPanelProps> = ({
  query,
  setQuery,
  onAnalyze,
  isAnalyzing,
  activeDoc,
  timeline,
  totalDurationMs,
  recentQueries,
  onSelectRecentQuery,
  chunkSize,
  setChunkSize,
  chunkOverlap,
  setChunkOverlap,
  topK,
  setTopK
}) => {
  const [showSettings, setShowSettings] = useState(false);

  // Generate contextual sample questions based on active document
  const getSuggestions = () => {
    if (!activeDoc) {
      return [
        "What are the primary findings presented in this study?",
        "What methodology and experimental setup was utilized?",
        "What are the specific quantitative performance metrics reported?"
      ];
    }
    const name = activeDoc.filename.toLowerCase();
    if (name.includes('quantum') || name.includes('cryo')) {
      return [
        "How are quantum chips kept cold and what temperature is used?",
        "What principles of quantum mechanics do qubits utilize?",
        "Why is Shor's algorithm a threat to classical RSA encryption?"
      ];
    } else if (name.includes('travel') || name.includes('policy') || name.includes('sec-2026')) {
      return [
        "What laptop must be used for Category A travel and how many days notice is required?",
        "What authentication protocol is mandatory for traveling employees?",
        "Are personal mobile devices permitted to access company files abroad?"
      ];
    } else if (name.includes('moxie') || name.includes('mars') || name.includes('perseverance')) {
      return [
        "How many grams of oxygen did MOXIE produce on Mars and over how many runs?",
        "Why was Jezero Crater chosen as the landing site for Perseverance?",
        "How many flights did the Ingenuity helicopter complete?"
      ];
    } else if (name.includes('stroke') || name.includes('patient') || name.includes('clinic')) {
      return [
        "Which patients have documented hypertension and high blood glucose?",
        "What are the clinical characteristics of patient PT-1001?",
        "How many patients are flagged with high stroke risk?"
      ];
    }
    return [
      `What is the central topic described in ${activeDoc.filename}?`,
      "What key dates, numbers, or metrics are reported in this file?",
      "Summarize the most important conclusion or directive."
    ];
  };

  const suggestions = getSuggestions();

  // Keyboard shortcut Ctrl+Enter
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      if (query.trim() && !isAnalyzing && activeDoc) {
        onAnalyze();
      }
    }
  };

  const wordCount = query.trim() ? query.trim().split(/\s+/).length : 0;
  const charCount = query.length;

  return (
    <div className="flex flex-col h-full bg-background relative overflow-y-auto">
      
      {/* Studio Header */}
      <div className="p-4 sm:p-5 border-b border-surface-border flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-md bg-cyan/10 border border-cyan/20">
            <Search className="w-4 h-4 text-cyan" />
          </div>
          <div>
            <h2 className="text-sm font-semibold tracking-tight text-slate-100">
              Semantic Query Studio
            </h2>
            <p className="text-xs text-slate-400">
              Formulate analytical questions or hypotheses against the active document.
            </p>
          </div>
        </div>

        {/* Hyperparameters Toggle */}
        <button
          onClick={() => setShowSettings(!showSettings)}
          className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-md border text-xs font-mono transition-all ${
            showSettings 
              ? 'bg-surface-200 border-cyan text-cyan' 
              : 'bg-surface-50 hover:bg-surface-100 border-surface-border text-slate-400 hover:text-slate-200'
          }`}
          title="Configure Sliding Window & Similarity Hyperparameters"
        >
          <Sliders className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Engine Params</span>
        </button>
      </div>

      {/* Main Studio Body */}
      <div className="p-4 sm:p-5 space-y-4 flex-1">

        {/* Hyperparameter Settings Drawer */}
        {showSettings && (
          <div className="p-4 rounded-lg bg-surface-50 border border-surface-border space-y-3 animate-fadeIn">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 border-b border-surface-border pb-2">
              <span className="uppercase tracking-wider">Algorithmic Hyperparameters</span>
              <span>128D Dense Vector Architecture</span>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="text-[11px] font-mono text-slate-300 block mb-1">
                  Chunk Size (Words): <span className="text-cyan">{chunkSize}</span>
                </label>
                <input
                  type="range"
                  min="10"
                  max="60"
                  value={chunkSize}
                  onChange={(e) => setChunkSize(Number(e.target.value))}
                  className="w-full accent-cyan"
                />
                <span className="text-[10px] text-slate-500 font-mono">Sliding window width</span>
              </div>

              <div>
                <label className="text-[11px] font-mono text-slate-300 block mb-1">
                  Chunk Overlap (Words): <span className="text-cyan">{chunkOverlap}</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max={Math.max(1, chunkSize - 2)}
                  value={chunkOverlap}
                  onChange={(e) => setChunkOverlap(Number(e.target.value))}
                  className="w-full accent-cyan"
                />
                <span className="text-[10px] text-slate-500 font-mono">Boundary preservation</span>
              </div>

              <div>
                <label className="text-[11px] font-mono text-slate-300 block mb-1">
                  Top-K Passages: <span className="text-cyan">{topK}</span>
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={topK}
                  onChange={(e) => setTopK(Number(e.target.value))}
                  className="w-full accent-cyan"
                />
                <span className="text-[10px] text-slate-500 font-mono">Leaderboard depth</span>
              </div>
            </div>
          </div>
        )}

        {/* Document Context Alert */}
        {!activeDoc && (
          <div className="p-3 rounded-lg bg-indigo/10 border border-indigo/20 text-indigo-200 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo" />
              <span>No document currently selected. Select or upload one from the left panel.</span>
            </div>
          </div>
        )}

        {/* Textarea Editor */}
        <div className="relative rounded-lg border border-surface-border bg-surface-50 focus-within:border-cyan/50 focus-within:ring-1 focus-within:ring-cyan/30 transition-all shadow-subtle">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={5}
            placeholder={activeDoc ? `Ask anything about ${activeDoc.filename}... (e.g. key dates, rules, scientific findings)` : "Enter any question, statement, or description..."}
            className="w-full p-4 bg-transparent text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none resize-none leading-relaxed"
          />

          {/* Editor Footer */}
          <div className="px-4 py-2.5 border-t border-surface-border/60 flex items-center justify-between text-xs text-slate-400 font-mono">
            <div className="flex items-center gap-3 text-[11px]">
              <span>{charCount} chars</span>
              <span>•</span>
              <span>{wordCount} words</span>
            </div>

            <div className="flex items-center gap-2">
              {query && (
                <button
                  onClick={() => setQuery('')}
                  className="p-1 hover:text-slate-200 text-slate-500 transition-colors"
                  title="Clear Query"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
              )}
              <div className="hidden sm:flex items-center gap-1 text-[11px] text-slate-500 bg-surface-100 px-2 py-0.5 rounded border border-surface-border">
                <span>Ctrl</span>
                <span>+</span>
                <CornerDownLeft className="w-3 h-3" />
              </div>
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center justify-between pt-1">
          <div className="text-xs text-slate-400">
            {activeDoc ? (
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                Targeting: <strong className="text-slate-200">{activeDoc.filename}</strong>
              </span>
            ) : (
              <span className="text-slate-500">Please select a document first</span>
            )}
          </div>

          <button
            onClick={onAnalyze}
            disabled={!query.trim() || isAnalyzing || !activeDoc}
            className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-semibold tracking-wide transition-all ${
              !query.trim() || isAnalyzing || !activeDoc
                ? 'opacity-40 cursor-not-allowed bg-surface-200 text-slate-400 border border-surface-border'
                : 'bg-cyan hover:bg-cyan-muted text-slate-950 shadow-glow-cyan hover:scale-[1.01]'
            }`}
          >
            {isAnalyzing ? (
              <>
                <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                <span>Running Similarity Engine...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Analyze Similarity</span>
              </>
            )}
          </button>
        </div>

        {/* Live Execution Timeline */}
        <LiveTimeline 
          timeline={timeline}
          isAnalyzing={isAnalyzing}
          totalDurationMs={totalDurationMs}
        />

        {/* Contextual Suggestions */}
        <div className="space-y-2 pt-2">
          <div className="flex items-center gap-1.5 text-[11px] font-mono uppercase tracking-wider text-slate-500">
            <Lightbulb className="w-3 h-3 text-cyan" />
            Suggested Research Prompts
          </div>
          <div className="space-y-1.5">
            {suggestions.map((s, idx) => (
              <button
                key={idx}
                onClick={() => setQuery(s)}
                className="w-full text-left p-2.5 rounded-md bg-surface-50 hover:bg-surface-100 border border-surface-border hover:border-cyan/30 text-xs text-slate-300 hover:text-slate-100 transition-all flex items-center justify-between group"
              >
                <span className="truncate pr-2">{s}</span>
                <span className="text-[10px] font-mono text-cyan opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                  Fill Prompt →
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Recent Queries */}
        {recentQueries.length > 0 && (
          <div className="space-y-2 pt-2 border-t border-surface-border">
            <div className="flex items-center gap-1.5 text-[11px] font-mono uppercase tracking-wider text-slate-500">
              <History className="w-3 h-3 text-slate-400" />
              Recent Studio Queries
            </div>
            <div className="flex flex-wrap gap-1.5">
              {recentQueries.slice(0, 5).map((rq, idx) => (
                <button
                  key={idx}
                  onClick={() => onSelectRecentQuery(rq)}
                  className="px-2.5 py-1 rounded bg-surface-50 hover:bg-surface-100 border border-surface-border hover:border-slate-400 text-[11px] text-slate-300 truncate max-w-xs transition-colors"
                  title={rq}
                >
                  {rq}
                </button>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
