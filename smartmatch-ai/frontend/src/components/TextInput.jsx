import React from 'react';
import { HelpCircle, XCircle, Type, Lightbulb } from 'lucide-react';

export default function TextInput({
  value,
  onChange,
  onClear,
  error,
  disabled,
  onSelectSampleQuery
}) {
  const charCount = value ? value.length : 0;
  const wordCount = value.trim() ? value.trim().split(/\s+/).length : 0;

  const quickSamples = [
    "What are the main causes of diabetes?",
    "How does TF-IDF and cosine similarity work in NLP?",
    "What greenhouse gases drive global warming and climate change?",
    "How do qubits and superposition differ from classical bits?"
  ];

  return (
    <div className="card-soft rounded-2xl p-6 transition-all duration-200">
      {/* Section Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-sky-100 flex items-center justify-center text-sky-700">
            <HelpCircle className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900">
              Enter Your Question or Text
            </h2>
            <p className="text-xs text-slate-500">
              Type any question, statement, or concept you want to search within your document
            </p>
          </div>
        </div>

        {/* Clear Button */}
        {value && (
          <button
            onClick={onClear}
            disabled={disabled}
            className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors cursor-pointer"
            title="Clear entered text"
          >
            <XCircle className="w-3.5 h-3.5" />
            <span>Clear</span>
          </button>
        )}
      </div>

      {/* Main Textarea */}
      <div className="relative">
        <textarea
          rows={4}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          placeholder="Example: What are the main causes of diabetes?"
          className={`w-full p-4 rounded-xl text-slate-800 placeholder-slate-400 bg-slate-50/70 border focus:bg-white focus:outline-none focus:ring-2 transition-all resize-none text-sm sm:text-base leading-relaxed ${
            error
              ? 'border-red-400 focus:ring-red-200 bg-red-50/30'
              : 'border-slate-200 focus:border-sky-500 focus:ring-sky-100'
          }`}
        />

        {/* Character & Word Counter */}
        <div className="flex items-center justify-between mt-2 px-1 text-xs text-slate-400">
          <div className="flex items-center gap-1.5">
            <Type className="w-3.5 h-3.5 text-slate-400" />
            <span>{wordCount} {wordCount === 1 ? 'word' : 'words'}</span>
          </div>
          <div>
            <span className={charCount > 1000 ? 'text-amber-600 font-medium' : ''}>
              {charCount} characters
            </span>
          </div>
        </div>
      </div>

      {/* Inline Validation Error Banner */}
      {error && (
        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 flex items-center gap-2 animate-shake">
          <span className="w-1.5 h-1.5 rounded-full bg-red-600"></span>
          <span>{error}</span>
        </div>
      )}

      {/* Quick Demonstration Chips */}
      <div className="mt-4 pt-4 border-t border-slate-100">
        <div className="flex items-center gap-1.5 text-xs text-slate-500 mb-2 font-medium">
          <Lightbulb className="w-3.5 h-3.5 text-amber-500" />
          <span>Try a sample question:</span>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {quickSamples.map((q, idx) => (
            <button
              key={idx}
              type="button"
              disabled={disabled}
              onClick={() => onSelectSampleQuery(q)}
              className="text-xs px-2.5 py-1 rounded-lg bg-sky-50/80 hover:bg-sky-100 text-sky-800 border border-sky-200/60 transition-colors text-left truncate max-w-full cursor-pointer hover:border-sky-300"
            >
              "{q}"
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
