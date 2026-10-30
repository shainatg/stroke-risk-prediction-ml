import React from 'react';
import { 
  Cpu, 
  Layers, 
  FileText, 
  History, 
  HelpCircle, 
  CheckCircle2, 
  AlertCircle
} from 'lucide-react';

interface NavbarProps {
  backendOnline: boolean;
  onOpenSimilarityLab: () => void;
  onOpenDocumentViewer: () => void;
  onOpenPipelineExplorer: () => void;
  onOpenHistory: () => void;
  onOpenShortcuts: () => void;
  activeDocName?: string;
  hasAnalysis: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  backendOnline,
  onOpenSimilarityLab,
  onOpenDocumentViewer,
  onOpenPipelineExplorer,
  onOpenHistory,
  onOpenShortcuts,
  activeDocName,
  hasAnalysis
}) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-surface-border bg-background-secondary/90 backdrop-blur-md">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6 max-w-7xl mx-auto">
        
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="relative flex h-9 w-9 items-center justify-center rounded-lg bg-surface-100 border border-surface-border shadow-subtle group">
            <Cpu className="h-5 w-5 text-cyan transition-transform duration-300 group-hover:scale-110" />
            <div className="absolute inset-0 rounded-lg bg-cyan-glow blur-sm opacity-50" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-display text-base font-bold tracking-tight text-slate-100">
                SYNAPSE
              </span>
              <span className="rounded-full bg-cyan/10 border border-cyan/20 px-2 py-0.5 text-[10px] font-mono font-medium text-cyan uppercase tracking-wider">
                128D Studio
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono tracking-tight hidden sm:block">
              Intelligent Semantic Analysis Studio
            </p>
          </div>
        </div>

        {/* Center: Active Document Badge (if loaded) */}
        {activeDocName && (
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-md bg-surface-50 border border-surface-border text-xs text-slate-300 max-w-xs truncate font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan animate-pulse" />
            <span className="truncate">{activeDocName}</span>
          </div>
        )}

        {/* Right Navigation Controls */}
        <div className="flex items-center gap-1.5 sm:gap-2">
          
          {/* Similarity Lab Button */}
          <button
            onClick={onOpenSimilarityLab}
            disabled={!hasAnalysis}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md border transition-all ${
              hasAnalysis 
                ? 'bg-surface-100 hover:bg-surface-200 text-slate-200 border-surface-border hover:border-cyan/40 hover:text-cyan shadow-subtle' 
                : 'opacity-40 cursor-not-allowed bg-surface-50 text-slate-500 border-surface-border'
            }`}
            title={hasAnalysis ? "Open Interactive Similarity Lab" : "Run an analysis first to open Similarity Lab"}
          >
            <Layers className="h-3.5 w-3.5 text-cyan" />
            <span className="hidden sm:inline">Similarity Lab</span>
          </button>

          {/* Document Viewer Button */}
          <button
            onClick={onOpenDocumentViewer}
            disabled={!activeDocName}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md border transition-all ${
              activeDocName 
                ? 'bg-surface-100 hover:bg-surface-200 text-slate-200 border-surface-border hover:border-indigo/40 hover:text-indigo-subtle shadow-subtle' 
                : 'opacity-40 cursor-not-allowed bg-surface-50 text-slate-500 border-surface-border'
            }`}
            title={activeDocName ? "Open Document Inspection Viewer" : "Select or upload a document first"}
          >
            <FileText className="h-3.5 w-3.5 text-indigo" />
            <span className="hidden sm:inline">Viewer</span>
          </button>

          {/* Pipeline Explorer Button */}
          <button
            onClick={onOpenPipelineExplorer}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md border border-surface-border bg-surface-100 hover:bg-surface-200 text-slate-300 hover:text-slate-100 transition-all shadow-subtle"
            title="Interactive Pipeline Explorer"
          >
            <Cpu className="h-3.5 w-3.5 text-lavender" />
            <span className="hidden sm:inline">Pipeline</span>
          </button>

          {/* History Button */}
          <button
            onClick={onOpenHistory}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md border border-surface-border bg-surface-100 hover:bg-surface-200 text-slate-300 hover:text-slate-100 transition-all shadow-subtle"
            title="View Analysis History"
          >
            <History className="h-3.5 w-3.5 text-slate-400" />
            <span className="hidden sm:inline">History</span>
          </button>

          {/* Shortcuts Button */}
          <button
            onClick={onOpenShortcuts}
            className="p-1.5 text-slate-400 hover:text-slate-200 rounded-md hover:bg-surface-100 transition-colors"
            title="Keyboard Shortcuts"
          >
            <HelpCircle className="h-4 w-4" />
          </button>

          {/* Backend Health Pill */}
          <div 
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-surface-100 border border-surface-border text-[11px] font-mono text-slate-300"
            title={backendOnline ? "FastAPI Engine Connected" : "Backend Disconnected"}
          >
            {backendOnline ? (
              <>
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                <span className="text-emerald-400 font-medium hidden lg:inline">Core Online</span>
              </>
            ) : (
              <>
                <AlertCircle className="h-3.5 w-3.5 text-rose-400 animate-pulse" />
                <span className="text-rose-400 font-medium hidden lg:inline">Offline</span>
              </>
            )}
          </div>

        </div>

      </div>
    </header>
  );
};
