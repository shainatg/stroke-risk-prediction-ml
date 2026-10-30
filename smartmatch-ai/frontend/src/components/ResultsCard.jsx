import React, { useState } from 'react';
import {
  Check,
  Copy,
  RotateCcw,
  FileText,
  AlertTriangle,
  Info,
  ChevronDown,
  ChevronUp,
  Percent,
  Sparkles,
  HelpCircle,
  Tag
} from 'lucide-react';

export default function ResultsCard({
  result,
  onAnalyzeAgain
}) {
  const [copied, setCopied] = useState(false);
  const [showCandidates, setShowCandidates] = useState(false);

  if (!result) return null;

  const {
    question,
    answer,
    similarity_score,
    similarity_percentage,
    confidence_label,
    source_document,
    total_paragraphs_compared,
    best_paragraph_index,
    matched_terms = [],
    candidates = [],
    match_found
  } = result;

  // Copy Answer to clipboard with visual confirmation
  const handleCopy = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(answer).then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      });
    }
  };

  // Select progress bar color scheme based on similarity percentage
  const getProgressStyles = (pct) => {
    if (pct >= 50) {
      return {
        bar: 'bg-gradient-to-r from-emerald-500 to-teal-500',
        badge: 'bg-emerald-50 text-emerald-700 border-emerald-200',
        ring: 'border-emerald-200'
      };
    } else if (pct >= 25) {
      return {
        bar: 'bg-gradient-to-r from-sky-500 to-blue-600',
        badge: 'bg-sky-50 text-sky-700 border-sky-200',
        ring: 'border-sky-200'
      };
    } else if (pct > 5) {
      return {
        bar: 'bg-gradient-to-r from-amber-400 to-orange-500',
        badge: 'bg-amber-50 text-amber-700 border-amber-200',
        ring: 'border-amber-200'
      };
    } else {
      return {
        bar: 'bg-slate-300',
        badge: 'bg-slate-100 text-slate-600 border-slate-200',
        ring: 'border-slate-200'
      };
    }
  };

  const theme = getProgressStyles(similarity_percentage);

  return (
    <section id="results-section" className="w-full mt-8 animate-fadeIn">
      <div className="card-soft rounded-3xl p-6 sm:p-8 bg-white border border-sky-200/90 shadow-xl shadow-sky-500/5">
        
        {/* Results Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-6 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-2xl bg-sky-50 border border-sky-200 flex items-center justify-center text-sky-600 shadow-xs">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <span className="text-xs font-semibold text-sky-600 uppercase tracking-wider">
                Analysis Complete
              </span>
              <h2 className="text-2xl font-extrabold text-slate-900">
                Document Similarity Result
              </h2>
            </div>
          </div>

          {/* Action Buttons: Copy Answer & Analyze Again */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold text-slate-700 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-xl transition-all cursor-pointer shadow-xs active:scale-95"
              title="Copy the most relevant answer to clipboard"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4 text-emerald-600" />
                  <span className="text-emerald-700">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4 text-slate-500" />
                  <span>Copy Answer</span>
                </>
              )}
            </button>

            <button
              onClick={onAnalyzeAgain}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold text-white bg-sky-600 hover:bg-sky-700 rounded-xl transition-all cursor-pointer shadow-xs shadow-sky-600/20 active:scale-95"
              title="Reset query and analyze again"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Analyze Again</span>
            </button>
          </div>
        </div>

        {/* 1. Your Question Section */}
        <div className="mt-6 p-4 rounded-2xl bg-slate-50/80 border border-slate-200/80">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">
            <HelpCircle className="w-3.5 h-3.5 text-slate-400" />
            <span>Your Question</span>
          </div>
          <p className="text-base sm:text-lg font-semibold text-slate-900 leading-snug">
            "{question}"
          </p>
        </div>

        {/* 2. Most Relevant Answer Section */}
        <div className="mt-5 p-5 rounded-2xl bg-sky-50/40 border border-sky-100 relative">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-sky-700">
              <FileText className="w-3.5 h-3.5 text-sky-600" />
              <span>Most Relevant Answer</span>
              {best_paragraph_index && (
                <span className="text-[11px] font-normal text-slate-500 lowercase">
                  (extracted from paragraph #{best_paragraph_index})
                </span>
              )}
            </div>

            {matched_terms.length > 0 && (
              <div className="hidden sm:flex items-center gap-1 text-[11px] text-slate-500">
                <Tag className="w-3 h-3 text-sky-500" />
                <span>Matched: {matched_terms.slice(0, 3).join(', ')}</span>
              </div>
            )}
          </div>

          <p className="text-base text-slate-800 leading-relaxed font-normal whitespace-pre-wrap">
            {answer}
          </p>
        </div>

        {/* 3. Similarity Score & Source Document Grid */}
        <div className="mt-5 grid grid-cols-1 md:grid-cols-2 gap-4">
          
          {/* Similarity Score Card with Progress Bar */}
          <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <Percent className="w-3.5 h-3.5 text-sky-600" />
                Similarity Score
              </span>
              <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${theme.badge}`}>
                {confidence_label || 'Calculated'}
              </span>
            </div>

            {/* Large Percentage Metric */}
            <div className="flex items-baseline gap-2 mb-2">
              <span className="text-3xl font-extrabold text-slate-900">
                {similarity_percentage}%
              </span>
              <span className="text-xs text-slate-500 font-mono">
                (Cosine: {similarity_score})
              </span>
            </div>

            {/* Visual Progress Bar */}
            <div className="w-full h-3 rounded-full bg-slate-100 overflow-hidden border border-slate-200 p-0.5">
              <div
                className={`h-full rounded-full transition-all duration-700 ease-out ${theme.bar}`}
                style={{ width: `${Math.min(100, Math.max(4, similarity_percentage))}%` }}
              ></div>
            </div>
          </div>

          {/* Source Document Metadata Card */}
          <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs flex flex-col justify-between">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5 mb-2">
                <FileText className="w-3.5 h-3.5 text-sky-600" />
                Source Document
              </span>
              <p className="text-sm font-bold text-slate-900 truncate">
                {source_document}
              </p>
            </div>

            <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100 mt-2">
              <span>{total_paragraphs_compared} paragraphs analyzed</span>
              <span className="text-sky-600 font-medium">Scikit-Learn TF-IDF</span>
            </div>
          </div>
        </div>

        {/* 4. Educational Disclaimer Note (Required by prompt) */}
        <div className="mt-5 p-3.5 rounded-xl bg-amber-50/80 border border-amber-200/80 text-xs text-amber-900 flex items-start gap-2.5 leading-relaxed">
          <Info className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">Understanding Your Similarity Score: </span>
            This score measures <em>textual and semantic vector alignment</em> between your question and the document content using TF-IDF and Cosine Similarity. It reflects how closely the wording and themes overlap, not the scientific certainty or probability that the statement is factually accurate.
          </div>
        </div>

        {/* 5. Optional Expandable Candidates Drawer (For Professor Demonstration) */}
        {candidates && candidates.length > 1 && (
          <div className="mt-5 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setShowCandidates(!showCandidates)}
              className="w-full flex items-center justify-between py-2 text-xs font-semibold text-slate-600 hover:text-sky-700 transition-colors cursor-pointer"
            >
              <span>View other candidate paragraphs compared ({candidates.length} total)</span>
              {showCandidates ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {showCandidates && (
              <div className="mt-3 space-y-2.5">
                {candidates.map((cand, idx) => (
                  <div
                    key={idx}
                    className={`p-3 rounded-xl border text-xs ${
                      idx === 0
                        ? 'bg-sky-50/60 border-sky-300 font-medium text-slate-900'
                        : 'bg-slate-50/50 border-slate-200 text-slate-600'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold">
                        {idx === 0 ? 'Rank #1 (Best Match)' : `Rank #${idx + 1}`} • Paragraph #{cand.index}
                      </span>
                      <span className="font-mono font-bold text-sky-700">
                        {cand.similarity_percentage}% match
                      </span>
                    </div>
                    <p className="line-clamp-3 leading-relaxed">
                      {cand.text}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

      </div>
    </section>
  );
}
