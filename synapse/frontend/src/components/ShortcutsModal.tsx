import React from 'react';
import { X, Keyboard, Command } from 'lucide-react';

interface ShortcutsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ShortcutsModal: React.FC<ShortcutsModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const shortcuts = [
    { key: "Ctrl + Enter", desc: "Execute semantic analysis in Query Studio" },
    { key: "Esc", desc: "Close any active modal or drawer" },
    { key: "Click Passage", desc: "Locate and highlight passage in Document Viewer" },
    { key: "Drag & Drop", desc: "Instantly upload and parse PDF, DOCX, TXT, or CSV" }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fadeIn">
      <div className="relative w-full max-w-md rounded-2xl bg-background-card border border-surface-border shadow-premium p-6 space-y-4">
        
        <div className="flex items-center justify-between border-b border-surface-border pb-3">
          <div className="flex items-center gap-2">
            <Keyboard className="w-5 h-5 text-cyan" />
            <h3 className="text-sm font-bold text-slate-100">
              Keyboard Shortcuts & Controls
            </h3>
          </div>
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-100 rounded">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-2">
          {shortcuts.map((s, idx) => (
            <div key={idx} className="flex items-center justify-between p-2.5 rounded-lg bg-surface-50 border border-surface-border">
              <span className="text-xs text-slate-300">{s.desc}</span>
              <kbd className="px-2 py-1 rounded bg-surface-100 border border-surface-border text-[11px] font-mono text-cyan font-medium">
                {s.key}
              </kbd>
            </div>
          ))}
        </div>

        <div className="pt-2 text-center">
          <button
            onClick={onClose}
            className="w-full py-2 rounded-lg bg-surface-100 hover:bg-surface-200 border border-surface-border text-xs font-semibold text-slate-200 transition-colors"
          >
            Got it
          </button>
        </div>

      </div>
    </div>
  );
};
