import React from 'react';
import { X, BookOpen, Calculator, Compass, CheckCircle } from 'lucide-react';

export default function HowItWorksModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs animate-fadeIn">
      <div className="bg-white rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 sm:p-8 shadow-2xl border border-sky-100 relative">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-2xl bg-sky-100 border border-sky-200 flex items-center justify-center text-sky-700">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-xl font-extrabold text-slate-900">
              How Text Similarity Works
            </h3>
            <p className="text-xs text-slate-500">
              College Assignment Theory & Machine Learning Guide
            </p>
          </div>
        </div>

        {/* Content Sections */}
        <div className="space-y-6 text-sm text-slate-700 leading-relaxed">
          
          {/* Step 1: Text Extraction */}
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
            <h4 className="font-bold text-slate-900 flex items-center gap-2 mb-2">
              <span className="w-5 h-5 rounded-full bg-sky-600 text-white text-xs flex items-center justify-center font-bold">1</span>
              Document Ingestion & Text Extraction
            </h4>
            <p className="text-xs text-slate-600">
              When a document is uploaded, our Python Flask backend parses its internal binary structure:
            </p>
            <ul className="mt-2 space-y-1 text-xs text-slate-600 list-disc list-inside">
              <li><strong>PDF (.pdf):</strong> PyMuPDF extracts text streams across pages.</li>
              <li><strong>Word (.docx):</strong> python-docx parses native XML paragraph tags.</li>
              <li><strong>Text (.txt):</strong> Decoded with UTF-8 / Latin-1 encoding detection.</li>
            </ul>
          </div>

          {/* Step 2: TF-IDF Vectorization */}
          <div className="p-4 rounded-2xl bg-sky-50/60 border border-sky-200">
            <h4 className="font-bold text-slate-900 flex items-center gap-2 mb-2">
              <span className="w-5 h-5 rounded-full bg-sky-600 text-white text-xs flex items-center justify-center font-bold">2</span>
              TF-IDF Numerical Vectorization
            </h4>
            <p className="text-xs text-slate-600 mb-2">
              Computers cannot compare strings directly. Scikit-learn's <code>TfidfVectorizer</code> transforms both your question and document paragraphs into numerical vectors:
            </p>
            <div className="p-3 bg-white rounded-xl border border-sky-200 text-xs font-mono text-sky-950">
              TF-IDF(t, d, D) = TF(t, d) &times; log( N / DF(t) )
            </div>
            <p className="text-xs text-slate-600 mt-2">
              • <strong>TF (Term Frequency):</strong> Measures how frequently a word appears in a paragraph.<br/>
              • <strong>IDF (Inverse Document Frequency):</strong> Gives higher weight to rare, informative words (e.g. <em>"diabetes"</em>) and lowers common words (e.g. <em>"is", "the"</em>).
            </p>
          </div>

          {/* Step 3: Cosine Similarity Metric */}
          <div className="p-4 rounded-2xl bg-blue-50/60 border border-blue-200">
            <h4 className="font-bold text-slate-900 flex items-center gap-2 mb-2">
              <span className="w-5 h-5 rounded-full bg-blue-600 text-white text-xs flex items-center justify-center font-bold">3</span>
              Cosine Similarity Metric
            </h4>
            <p className="text-xs text-slate-600 mb-2">
              The mathematical cosine of the angle &theta; between query vector <strong>A</strong> and paragraph vector <strong>B</strong> is computed:
            </p>
            <div className="p-3 bg-white rounded-xl border border-blue-200 text-xs font-mono text-blue-950">
              Cosine Similarity = (A &sdot; B) / ( ||A|| &times; ||B|| )
            </div>
            <p className="text-xs text-slate-600 mt-2">
              • <strong>1.0 (100%):</strong> Vectors point in the exact same orientation (identical semantic topic).<br/>
              • <strong>0.0 (0%):</strong> Orthogonal vectors (no shared vocabulary or relationship).
            </p>
          </div>

          {/* Step 4: Grounded Result */}
          <div className="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-200">
            <h4 className="font-bold text-slate-900 flex items-center gap-2 mb-2">
              <span className="w-5 h-5 rounded-full bg-emerald-600 text-white text-xs flex items-center justify-center font-bold">4</span>
              Answer Extraction & Grounding
            </h4>
            <p className="text-xs text-slate-600">
              The paragraph with the highest cosine score is ranked #1 and returned directly from the document. The exact similarity score is displayed with a progress bar and source attribution.
            </p>
          </div>

        </div>

        {/* Modal Footer */}
        <div className="mt-6 pt-4 border-t border-slate-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2.5 bg-sky-600 hover:bg-sky-700 text-white text-xs font-bold rounded-xl transition-colors cursor-pointer"
          >
            Got It! Close Window
          </button>
        </div>

      </div>
    </div>
  );
}
