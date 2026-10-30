import React, { useState } from 'react';
import { Layers, Search, Sparkles } from 'lucide-react';

interface ThreePanelLayoutProps {
  leftPanel: React.ReactNode;
  centerPanel: React.ReactNode;
  rightPanel: React.ReactNode;
  hasAnalysis: boolean;
}

export const ThreePanelLayout: React.FC<ThreePanelLayoutProps> = ({
  leftPanel,
  centerPanel,
  rightPanel,
  hasAnalysis
}) => {
  const [mobileTab, setMobileTab] = useState<'sources' | 'studio' | 'results'>('studio');

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-4rem)] overflow-hidden">
      
      {/* Mobile Tab Switcher */}
      <div className="lg:hidden flex items-center justify-around border-b border-surface-border bg-background-secondary p-1.5 text-xs font-mono">
        <button
          onClick={() => setMobileTab('sources')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
            mobileTab === 'sources' 
              ? 'bg-surface-200 text-cyan border border-surface-border' 
              : 'text-slate-400'
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          <span>Sources</span>
        </button>

        <button
          onClick={() => setMobileTab('studio')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
            mobileTab === 'studio' 
              ? 'bg-surface-200 text-cyan border border-surface-border' 
              : 'text-slate-400'
          }`}
        >
          <Search className="w-3.5 h-3.5" />
          <span>Studio</span>
        </button>

        <button
          onClick={() => setMobileTab('results')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
            mobileTab === 'results' 
              ? 'bg-surface-200 text-cyan border border-surface-border' 
              : 'text-slate-400'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Results {hasAnalysis && '•'}</span>
        </button>
      </div>

      {/* Main Workspace Panels */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Left Panel: Knowledge Sources */}
        <aside className={`w-full lg:w-72 xl:w-80 shrink-0 h-full overflow-hidden ${
          mobileTab === 'sources' ? 'block' : 'hidden lg:block'
        }`}>
          {leftPanel}
        </aside>

        {/* Center Panel: Semantic Query Studio */}
        <main className={`flex-1 h-full overflow-hidden ${
          mobileTab === 'studio' ? 'block' : 'hidden lg:block'
        }`}>
          {centerPanel}
        </main>

        {/* Right Panel: Intelligence Results */}
        <aside className={`w-full lg:w-96 xl:w-[440px] shrink-0 h-full overflow-hidden ${
          mobileTab === 'results' ? 'block' : 'hidden lg:block'
        }`}>
          {rightPanel}
        </aside>

      </div>

    </div>
  );
};
