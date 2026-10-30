import React, { useState } from 'react';
import { 
  X, 
  History, 
  Search, 
  Trash2, 
  ArrowRight, 
  Clock, 
  Sparkles, 
  FileText 
} from 'lucide-react';
import { AnalysisHistoryItem } from '../types';

interface HistoryDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  history: AnalysisHistoryItem[];
  onSelectHistoryItem: (id: string) => void;
  onDeleteHistoryItem: (id: string) => void;
  onSearchHistory: (query: string) => void;
}

export const HistoryDrawer: React.FC<HistoryDrawerProps> = ({
  isOpen,
  onClose,
  history,
  onSelectHistoryItem,
  onDeleteHistoryItem,
  onSearchHistory
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  if (!isOpen) return null;

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setSearchTerm(val);
    onSearchHistory(val);
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-950/60 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-md h-full bg-background-card border-l border-surface-border shadow-premium flex flex-col">
        
        {/* Drawer Header */}
        <div className="p-4 border-b border-surface-border flex items-center justify-between bg-surface-50">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-md bg-surface-100 border border-surface-border">
              <History className="w-4 h-4 text-cyan" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-100">
                Research Analysis History
              </h3>
              <p className="text-[11px] text-slate-400 font-mono">
                {history.length} saved audit sessions (SQLite)
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-md text-slate-400 hover:text-slate-100 hover:bg-surface-100 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Search */}
        <div className="p-3 border-b border-surface-border bg-surface-50/50">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={searchTerm}
              onChange={handleSearchChange}
              placeholder="Search previous queries..."
              className="w-full pl-8 pr-3 py-1.5 text-xs bg-surface-100 border border-surface-border rounded-md text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-cyan font-mono"
            />
          </div>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {history.length === 0 ? (
            <div className="text-center py-12 px-4 border border-surface-border rounded-lg bg-surface-50/50">
              <History className="w-8 h-8 mx-auto text-slate-600 mb-2" />
              <p className="text-xs text-slate-400">No analysis history recorded</p>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Execute a semantic query in the studio to populate history.
              </p>
            </div>
          ) : (
            history.map((item) => (
              <div
                key={item.id}
                onClick={() => {
                  onSelectHistoryItem(item.id);
                  onClose();
                }}
                className="group p-3.5 rounded-lg border border-surface-border bg-surface-50/70 hover:bg-surface-100 hover:border-cyan/40 text-left cursor-pointer transition-all space-y-2"
              >
                <div className="flex items-center justify-between text-[11px] font-mono">
                  <span className="text-cyan font-semibold truncate max-w-[200px]">
                    {item.document_name}
                  </span>
                  <div className="flex items-center gap-1.5">
                    <span className="text-emerald-400 font-semibold bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
                      {(item.top_score * 100).toFixed(1)}%
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteHistoryItem(item.id);
                      }}
                      className="opacity-0 group-hover:opacity-100 p-1 text-slate-500 hover:text-rose-400 transition-opacity"
                      title="Delete record"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <div className="text-xs font-medium text-slate-200 line-clamp-2">
                  "{item.query}"
                </div>

                <div className="text-[11px] text-slate-400 line-clamp-2 bg-surface-200/40 p-2 rounded border border-surface-border/50">
                  {item.key_insight}
                </div>

                <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 pt-1">
                  <span>{formatDate(item.created_at)}</span>
                  <span>{item.duration_ms.toFixed(1)} ms</span>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-surface-border bg-surface-50 flex items-center justify-between text-xs font-mono text-slate-400">
          <span>Synced with SQLite</span>
          <button
            onClick={onClose}
            className="px-3 py-1 rounded bg-surface-100 hover:bg-surface-200 text-slate-200 border border-surface-border transition-colors"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
};
