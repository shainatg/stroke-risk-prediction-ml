import React from 'react';
import { Search, Loader2, Sparkles, ArrowRight } from 'lucide-react';

export default function ActionButton({
  onClick,
  isLoading,
  disabled
}) {
  return (
    <div className="w-full text-center py-2">
      <button
        type="button"
        onClick={onClick}
        disabled={disabled || isLoading}
        className={`w-full sm:w-auto min-w-[320px] px-8 py-4 rounded-2xl font-bold text-base transition-all duration-200 flex items-center justify-center gap-3 shadow-md mx-auto cursor-pointer ${
          isLoading
            ? 'bg-sky-500 text-white cursor-wait opacity-90 shadow-sky-200'
            : disabled
            ? 'bg-slate-200 text-slate-400 cursor-not-allowed border border-slate-300'
            : 'bg-gradient-to-r from-sky-600 via-blue-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white shadow-sky-500/25 hover:shadow-lg hover:shadow-sky-500/35 hover:-translate-y-0.5 active:translate-y-0'
        }`}
      >
        {isLoading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin text-white" />
            <span className="tracking-wide">Analyzing your document...</span>
          </>
        ) : (
          <>
            <Sparkles className="w-5 h-5 text-sky-200" />
            <span className="tracking-wide">Find Similarity & Generate Answer</span>
            <ArrowRight className="w-5 h-5 text-white/80" />
          </>
        )}
      </button>

      {/* Helper text under button */}
      {!isLoading && !disabled && (
        <p className="text-xs text-slate-400 mt-2 font-normal">
          Calculates Scikit-Learn TF-IDF paragraph vectors & cosine similarity in real-time
        </p>
      )}
    </div>
  );
}
