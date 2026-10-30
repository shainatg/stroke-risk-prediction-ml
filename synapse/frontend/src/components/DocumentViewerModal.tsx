import React, { useState, useEffect, useRef } from 'react';
import { 
  X, 
  FileText, 
  Search, 
  ChevronLeft, 
  ChevronRight, 
  ZoomIn, 
  ZoomOut, 
  Maximize2,
  Bookmark,
  Hash
} from 'lucide-react';
import { DocumentDetail, Chunk } from '../types';

interface DocumentViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  document: DocumentDetail | null;
  highlightChunk: Chunk | null;
}

export const DocumentViewerModal: React.FC<DocumentViewerModalProps> = ({
  isOpen,
  onClose,
  document,
  highlightChunk
}) => {
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [zoomLevel, setZoomLevel] = useState<number>(100);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (highlightChunk) {
      setCurrentPage(highlightChunk.page || 1);
    }
  }, [highlightChunk]);

  if (!isOpen || !document) return null;

  const totalPages = document.total_pages || 1;
  const pageObj = document.pages?.find(p => p.page === currentPage) || {
    page: currentPage,
    text: document.full_text,
    char_count: document.char_count,
    word_count: document.word_count
  };

  const handleZoomIn = () => setZoomLevel(prev => Math.min(prev + 15, 160));
  const handleZoomOut = () => setZoomLevel(prev => Math.max(prev - 15, 80));

  // Render text with highlights
  const renderHighlightedText = (text: string) => {
    if (!text) return null;

    let highlighted = text;
    // If highlightChunk is on this page
    const chunkText = highlightChunk?.text?.trim();

    return (
      <div 
        className="font-mono text-slate-200 leading-relaxed whitespace-pre-wrap select-text"
        style={{ fontSize: `${(zoomLevel / 100) * 13}px` }}
      >
        {chunkText && text.includes(chunkText) ? (
          <>
            <span>{text.split(chunkText)[0]}</span>
            <mark className="bg-cyan/20 border-l-2 border-cyan text-cyan font-semibold px-1 py-0.5 rounded shadow-glow-cyan">
              {chunkText}
            </mark>
            <span>{text.split(chunkText).slice(1).join(chunkText)}</span>
          </>
        ) : (
          text
        )}
      </div>
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-5xl h-[88vh] rounded-2xl bg-background-card border border-surface-border shadow-premium flex flex-col overflow-hidden">
        
        {/* Viewer Header */}
        <div className="px-6 py-4 border-b border-surface-border flex items-center justify-between bg-surface-50 flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-indigo/10 border border-indigo/20">
              <FileText className="w-5 h-5 text-indigo" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-slate-100 truncate max-w-sm">
                  {document.filename}
                </h2>
                <span className="px-2 py-0.5 rounded bg-surface-200 text-indigo text-[10px] font-mono font-medium uppercase">
                  {document.file_type}
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">
                {document.word_count.toLocaleString()} words • {document.chunk_count} passages • {totalPages} {totalPages === 1 ? 'page' : 'pages'}
              </p>
            </div>
          </div>

          {/* Controls Bar */}
          <div className="flex items-center gap-2">
            
            {/* Page Navigation */}
            <div className="flex items-center gap-1 bg-surface-100 p-1 rounded-lg border border-surface-border text-xs font-mono">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage <= 1}
                className="p-1 text-slate-400 hover:text-slate-100 disabled:opacity-30 disabled:hover:text-slate-400 rounded"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="px-2 text-slate-300">
                {currentPage} / {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage >= totalPages}
                className="p-1 text-slate-400 hover:text-slate-100 disabled:opacity-30 disabled:hover:text-slate-400 rounded"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>

            {/* Zoom Controls */}
            <div className="flex items-center gap-1 bg-surface-100 p-1 rounded-lg border border-surface-border text-xs font-mono">
              <button
                onClick={handleZoomOut}
                className="p-1 text-slate-400 hover:text-slate-100 rounded"
                title="Zoom Out"
              >
                <ZoomOut className="w-4 h-4" />
              </button>
              <span className="px-1 text-[11px] text-slate-400 min-w-[38px] text-center">
                {zoomLevel}%
              </span>
              <button
                onClick={handleZoomIn}
                className="p-1 text-slate-400 hover:text-slate-100 rounded"
                title="Zoom In"
              >
                <ZoomIn className="w-4 h-4" />
              </button>
            </div>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-surface-100 transition-colors ml-2"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Selected Highlight Banner */}
        {highlightChunk && (
          <div className="px-6 py-2 bg-cyan/10 border-b border-cyan/20 flex items-center justify-between text-xs font-mono text-cyan">
            <span className="flex items-center gap-1.5">
              <Bookmark className="w-3.5 h-3.5 fill-current" />
              Viewing Citation for Passage #{highlightChunk.index + 1} (Page {highlightChunk.page})
            </span>
            <span className="text-[11px] text-cyan font-medium">
              Score: {((highlightChunk.score || 0) * 100).toFixed(1)}%
            </span>
          </div>
        )}

        {/* Document Content View */}
        <div ref={contentRef} className="flex-1 overflow-y-auto p-6 sm:p-8 bg-surface-50/50">
          <div className="max-w-3xl mx-auto p-8 rounded-xl bg-surface-50 border border-surface-border shadow-subtle min-h-[500px]">
            {renderHighlightedText(pageObj.text)}
          </div>
        </div>

        {/* Viewer Footer */}
        <div className="px-6 py-3 border-t border-surface-border bg-surface-50 flex items-center justify-between text-xs font-mono text-slate-400">
          <span>Page {currentPage} of {totalPages}</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-md bg-surface-100 hover:bg-surface-200 text-slate-200 border border-surface-border transition-colors"
          >
            Close Viewer
          </button>
        </div>

      </div>
    </div>
  );
};
