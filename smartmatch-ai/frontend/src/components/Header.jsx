import React from 'react';
import { Sparkles, FileText, Cpu, BookOpen } from 'lucide-react';

export default function Header({ onOpenExplainer }) {
  return (
    <header className="w-full pt-8 pb-6 px-4">
      <div className="max-w-5xl mx-auto text-center">
        {/* Top Badges */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-sky-100/80 border border-sky-200 text-sky-800 text-xs font-semibold uppercase tracking-wider mb-4 shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-sky-600 animate-pulse" />
          <span>NLP & Text Similarity Studio</span>
          <span className="w-1 h-1 rounded-full bg-sky-400"></span>
          <span className="text-sky-600">College Demonstration Edition</span>
        </div>

        {/* Main Application Title */}
        <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight mb-3">
          SmartMatch <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-600 to-blue-700">AI</span>
        </h1>

        {/* Required Subtitle */}
        <p className="text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto font-normal leading-relaxed">
          Upload a document, ask a question, and find the most relevant answer.
        </p>

        {/* Technology Highlights */}
        <div className="mt-5 flex flex-wrap items-center justify-center gap-2.5 text-xs text-slate-600">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-white rounded-lg border border-sky-100 shadow-xs font-medium">
            <Cpu className="w-3.5 h-3.5 text-sky-600" /> Scikit-Learn TF-IDF
          </span>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-white rounded-lg border border-sky-100 shadow-xs font-medium">
            <Sparkles className="w-3.5 h-3.5 text-blue-600" /> Cosine Similarity Vector Space
          </span>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-white rounded-lg border border-sky-100 shadow-xs font-medium">
            <FileText className="w-3.5 h-3.5 text-emerald-600" /> PDF (PyMuPDF) + DOCX + TXT
          </span>
          {onOpenExplainer && (
            <button
              onClick={onOpenExplainer}
              className="inline-flex items-center gap-1.5 px-3 py-1 bg-sky-600 hover:bg-sky-700 text-white rounded-lg font-medium transition-colors shadow-xs cursor-pointer"
              title="Learn how TF-IDF and Cosine Similarity mathematically work"
            >
              <BookOpen className="w-3.5 h-3.5" /> How Similarity Works
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
